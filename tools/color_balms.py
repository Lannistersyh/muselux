"""Color-adaptive balm references with official claims and shared-case links."""
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def selection(data, root=ROOT):
    config = json.loads((root/'tools/research/color-changing-balms.json').read_text())
    brands = {b['id']: b for b in data['brands']}
    clear = {e['id']: e for e in json.loads((root/'tools/research/lip-balms.json').read_text())['entries']}
    if len(config['entries']) != config['targetCount'] or not 3 <= config['targetCount'] <= 8:
        raise ValueError('Color-adaptive balms need three to eight sourced references')
    seen_ids, seen_refs, seen_cases = set(), set(), set()
    for entry in config['entries']:
        if entry['brand'] not in brands:
            raise ValueError('Color-adaptive balm needs an existing brand archive')
        reference = (entry['brand'], entry['reference'])
        case = (entry['brand'], entry['packagingId'])
        if not re.fullmatch(r'[a-z0-9-]+', entry['id']) or entry['id'] in seen_ids or reference in seen_refs or case in seen_cases:
            raise ValueError('Color-adaptive balm references and containers must be unique')
        seen_ids.add(entry['id']); seen_refs.add(reference); seen_cases.add(case)
        if entry['kind'] != 'full-size' or entry['currency'] != 'USD' or 'refill' in entry:
            raise ValueError('Color-adaptive balms need full-size USD quotes')
        if type(entry['priceUSD']) not in (int, float) or not 0 < entry['priceUSD'] < 1000:
            raise ValueError('Invalid color-adaptive balm price')
        if entry['priceStatus'] != 'official-snapshot' or not entry['method']:
            raise ValueError('Color-adaptive balm needs official price evidence')
        if entry.get('mechanism') != 'brand-described-ph-adaptive' or not entry.get('mechanismZh'):
            raise ValueError('Color-adaptive balm needs an explicit sourced mechanism claim')
        for field in ('source', 'mechanismSource'):
            if urlsplit(entry[field]).scheme != 'https':
                raise ValueError('Color-adaptive balm needs HTTPS sources')
        date.fromisoformat(entry['checkedAt'])
        if entry.get('sharedContainerWith'):
            parent = clear.get(entry['sharedContainerWith'])
            if not parent or (parent['brand'], parent['packagingId']) != case or 'image' in entry:
                raise ValueError('Same-container shades must link the matching existing case without a duplicate image')
        else:
            if any((p['brand'], p['packagingId']) == case for p in clear.values()):
                raise ValueError('Existing containers must be linked rather than photographed twice')
            for field in ('imageSource', 'imageSourcePage'):
                if urlsplit(entry[field]).scheme != 'https':
                    raise ValueError('Color-adaptive balm needs a sourced photograph')
            date.fromisoformat(entry['imageCheckedAt'])
    return [(entry, brands[entry['brand']]) for entry in config['entries']]


def annotate_brands(data):
    selected = selection(data)
    for brand in data['brands']:
        brand['colorBalmCount'] = sum(e['brand'] == brand['id'] for e, _ in selected)
    return selected


def brand_links(selected, brand_id, price_text):
    entries = [e for e, _ in selected if e['brand'] == brand_id]
    if not entries:
        return ''
    links = ''.join(f'<li><a href="../perfumery.html#color-balm-{e["id"]}"><span lang="en">{escape(e["series"])} · {escape(e["sample"])}</span> ↗</a><span>{price_text(e["priceUSD"])}</span></li>' for e in entries)
    return f'<section class="section brand-lipsticks" id="catalog-color-balm"><p class="eyebrow">LIP CARE / COLOR-ADAPTIVE BALMS</p><h2>变色润唇 · 具体版本</h2><p class="section-intro">本站收录 {len(entries)} 款变色润唇版本，按官网的 pH 自适应显色说明归集；相同外壳合并展示。</p><ul>{links}</ul></section>'


def render(data, price_text):
    cards = []
    for entry, brand in selection(data):
        if entry.get('sharedContainerWith'):
            photograph = f'<div class="color-balm-shared"><p class="eyebrow">ONE CASE / TWO FINISHES</p><p class="color-balm-shared-name" lang="en">{escape(brand["name"])}</p><p>与已收录的 U000 使用相同银色方管，外壳实物图合并展示。</p><a class="text-link" href="#lip-balm-{entry["sharedContainerWith"]}">查看这款外壳与 U000 无色款 ↗</a></div>'
        else:
            photograph = f'<figure><a class="lipstick-photo" href="{escape(entry["image"])}" target="_blank" rel="noopener noreferrer" aria-label="放大查看 {escape(brand["name"])} {escape(entry["series"])} 实物图"><img src="{escape(entry["image"])}" width="{entry["imageWidth"]}" height="{entry["imageHeight"]}" alt="{escape(entry["imageAlt"])}" loading="lazy" decoding="async"></a><figcaption><a href="{escape(entry["imageSourcePage"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(entry["imageCredit"])} ↗</a></figcaption></figure>'
        cards.append(f'''<article class="lipstick-card color-balm-card" id="color-balm-{entry['id']}">{photograph}<div class="lipstick-card-copy"><h3><a href="brand/{brand['id']}.html">{escape(entry.get('brandLabel',brand['name']))} ↗</a></h3><p class="lipstick-series" lang="en">{escape(entry['series'])}</p><p class="lipstick-shade">{escape(entry['sample'])} · {escape(entry['formatZh'])}</p><h4 class="lipstick-case-title">{escape(entry['finishZh'])}</h4><p class="lipstick-description">{escape(entry['descriptionZh'])}</p><p class="lip-balm-english" lang="en">{escape(entry['introEn'])}</p><p class="color-balm-mechanism"><a href="{escape(entry['mechanismSource'],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(entry['mechanismZh'])} ↗</a></p><p class="lip-balm-availability">{escape(entry['availabilityZh'])}</p><dl class="lipstick-offers"><div><dt>完整正装 · USD · 未含税</dt><dd><a href="{escape(entry['source'],quote=True)}" target="_blank" rel="noopener noreferrer">{price_text(entry['priceUSD'])} ↗</a><small>美国官网页面快照 · <time datetime="{entry['checkedAt']}">{entry['checkedAt']}</time> 复核</small></dd></div></dl></div></article>''')
    return f'''<section class="lipstick-market lip-balm-market" id="color-changing-balms" aria-labelledby="color-changing-balms-title"><header><p class="eyebrow rose-text">BEAUTY NOTES / COLOR-ADAPTIVE LIP CARE</p><h2 id="color-changing-balms-title">变色润唇，看看这三款</h2><p>想在润唇之外带一点粉色，可以从这三款了解。官网均有 pH 自适应显色的说明；它们属于会润色的润唇产品，最终颜色和光泽仍要上唇试色。下面按具体版本列出完整正装价格，相同外壳只保留一张图。</p><p class="lipstick-price-caption">品牌官网显色说明 · 具体版本 · 完整正装 · USD · 未含税</p></header><div class="lipstick-card-grid lip-balm-grid">{''.join(cards)}</div><div class="lipstick-reading"><p><strong>先看显色。</strong>Dior 001 Pink 偏清透粉色；Prada U001 偏玫瑰粉光泽；Tom Ford 官网描述为从透明逐渐转为个性化粉色。</p><p><strong>认准具体版本。</strong>Prada U000 是无色柔雾款，U001 才是这里收录的变色版本。Dior 此处选 001 Pink；同壳的其他色号不另开图片卡。</p><p><strong>想低调就先试色。</strong>男士也可按想要的显色程度选择。先在柜台薄涂，等颜色显现后再看是否符合自己的预期。</p></div></section>'''
