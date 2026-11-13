"""Sourced clear lip-care notes, kept separate from lipstick and annual catalogs."""
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def selection(data, root=ROOT):
    config = json.loads((root/'tools/research/lip-balms.json').read_text())
    entries = config['entries']
    brands = {b['id']: b for b in data['brands']}
    if not 3 <= len(entries) <= 8 or len(entries) != config['targetCount']:
        raise ValueError('Lip care needs three to eight sourced examples')
    seen_ids, seen_references, seen_containers = set(), set(), set()
    for entry in entries:
        if entry['brand'] not in brands:
            raise ValueError('Lip care needs an existing brand archive')
        identity = (entry['brand'], entry['reference'])
        if not re.fullmatch(r'[a-z0-9-]+', entry['id']) or entry['id'] in seen_ids or identity in seen_references:
            raise ValueError('Lip care IDs and references must be unique')
        container = (entry['brand'], entry['packagingId'])
        if container in seen_containers:
            raise ValueError('Lip care container variants must be merged')
        seen_ids.add(entry['id'])
        seen_references.add(identity)
        seen_containers.add(container)
        if entry['kind'] != 'full-size' or entry['currency'] != 'USD' or 'refill' in entry:
            raise ValueError('Lip care needs full-size USD quotes')
        if entry['tint'] != 'clear' or entry['audience'] != 'unisex':
            raise ValueError('This lip care selection needs clear, unisex products')
        if type(entry['priceUSD']) not in (int, float) or not 0 < entry['priceUSD'] < 1000:
            raise ValueError('Invalid lip care price')
        if entry['priceStatus'] != 'official-snapshot' or not entry['method']:
            raise ValueError('Lip care needs exact official price evidence')
        for field in ('source', 'imageSource', 'imageSourcePage'):
            if urlsplit(entry[field]).scheme != 'https':
                raise ValueError('Lip care needs HTTPS sources')
        date.fromisoformat(entry['checkedAt'])
        date.fromisoformat(entry['imageCheckedAt'])
    return [(entry, brands[entry['brand']]) for entry in entries]


def annotate_brands(data):
    selected = selection(data)
    for brand in data['brands']:
        brand['lipBalmCount'] = sum(e['brand'] == brand['id'] for e, _ in selected)
    return selected


def brand_links(selected, brand_id, price_text):
    entries = [e for e, _ in selected if e['brand'] == brand_id]
    if not entries:
        return ''
    links = ''.join(f'<li><a href="../perfumery.html#lip-balm-{e["id"]}"><span lang="en">{escape(e["series"])}</span> · {escape(e["sample"])} ↗</a><span>{price_text(e["priceUSD"])}</span></li>' for e in entries)
    return f'<section class="section brand-lipsticks" id="catalog-lip-balm"><p class="eyebrow">LIP CARE / CLEAR BALMS</p><h2>润唇膏 · 无色日常款</h2><p class="section-intro">本站收录 {len(entries)} 款无色润唇膏，男女通用；正装美元价格、实物图与光泽说明见美妆笔记。</p><ul>{links}</ul></section>'


def render(data, price_text):
    selected = selection(data)
    cards = []
    for entry, brand in selected:
        label = brand['name']
        cards.append(f'''<article class="lipstick-card lip-balm-card" id="lip-balm-{entry['id']}"><figure><a class="lipstick-photo" href="{escape(entry['image'])}" target="_blank" rel="noopener noreferrer" aria-label="放大查看 {escape(label)} {escape(entry['series'])} 润唇膏实物图"><img src="{escape(entry['image'])}" width="{entry['imageWidth']}" height="{entry['imageHeight']}" alt="{escape(entry['imageAlt'])}" loading="lazy" decoding="async"></a><figcaption><a href="{escape(entry['imageSourcePage'], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(entry['imageCredit'])} ↗</a></figcaption></figure><div class="lipstick-card-copy"><h3><a href="brand/{brand['id']}.html">{escape(label)} ↗</a></h3><p class="lipstick-series" lang="en">{escape(entry['series'])}</p><p class="lipstick-shade">{escape(entry['sample'])} · 无色 · 男女通用</p><h4 class="lipstick-case-title">{escape(entry['finishZh'])}</h4><p class="lipstick-description">{escape(entry['descriptionZh'])}</p><p class="lip-balm-english" lang="en">{escape(entry['introEn'])}</p><p class="lip-balm-availability">{escape(entry['availabilityZh'])}</p><dl class="lipstick-offers"><div><dt>完整正装 · USD · 未含税</dt><dd><a href="{escape(entry['source'], quote=True)}" target="_blank" rel="noopener noreferrer">{price_text(entry['priceUSD'])} ↗</a><small>美国官网页面快照 · <time datetime="{entry['checkedAt']}">{entry['checkedAt']}</time> 复核</small></dd></div></dl></div></article>''')
    return f'''<section class="lipstick-market lip-balm-market" id="lip-care" aria-labelledby="lip-care-title"><header><p class="eyebrow rose-text">BEAUTY NOTES / EVERYDAY LIP CARE</p><h2 id="lip-care-title">男士日常润唇</h2><p>先从无色款看起。这 {len(selected)} 款润唇膏均为男女通用，适合想保持自然唇色的日常使用；选择时可比较光泽、管身和正装价格。无色仍可能带有光泽，也不等于无香。</p><p class="lipstick-price-caption">一款容器一张实物图 · 仅列完整正装 · 美国官网参考 · USD · 未含税</p></header><div class="lipstick-card-grid lip-balm-grid">{''.join(cards)}</div><div class="lipstick-reading"><p><strong>偏低调的外观。</strong>Prada U000 是无色柔雾妆效；Hermès 是半哑光、接近隐形的妆效。这是品牌的妆效描述，实际光泽可先在柜台试用。</p><p><strong>接受一点自然光泽。</strong>Gucci 1 Joslyn Clair 是透明款，适合把柔和光泽作为日常外观的一部分。同系列有色版本没有另开卡片。</p><p><strong>先确认完整一支。</strong>这里的价格均对应带容器的正装。缺货状态按复核时页面注明；点击价格可查看品牌来源和最新情况。</p></div></section>'''
