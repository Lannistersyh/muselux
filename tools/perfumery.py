"""A sourced fragrance-house column within the existing fragrance category."""
from html import escape
from pathlib import Path
import json
import lip_balms
import color_balms

ROOT = Path(__file__).resolve().parents[1]
TITLE_ZH = '香氛与美妆'
TITLE_EN = 'Perfumery & Beauty'


def selection(data, root=ROOT):
    config = json.loads((root/'tools/perfumery.json').read_text())
    products = {x['id']: x for x in data['items']}
    brands = {x['id']: x for x in data['brands']}
    selected = []
    seen = set()
    for entry in config['houses']:
        product = products[entry['product']]
        if product['brand'] in seen or product['category'] != 'fragrance' or not product.get('styleEdit'):
            raise ValueError('Perfumery needs distinct houses and photographed fragrances')
        seen.add(product['brand'])
        selected.append((entry, brands[product['brand']], product))
    if not 3 <= len(selected) <= 5:
        raise ValueError('Perfumery column needs three to five houses')
    return selected


def teaser(data, prefix=''):
    selected = selection(data)
    names = ' / '.join(escape(b['name']) for _, b, _ in selected)
    photographs = ''.join(f'<img src="{prefix}{escape(p["image"])}" width="{p["imageWidth"]}" height="{p["imageHeight"]}" alt="{escape(b["name"]+" "+p["name"])}" loading="lazy">' for _, b, p in selected[:3])
    return f'''<section class="perfumery-teaser" aria-labelledby="perfumery-teaser-title"><div><p class="eyebrow rose-text">THE PERFUMERY EDIT / A NEW CHAPTER</p><h2 id="perfumery-teaser-title">{TITLE_ZH}</h2><p>从一瓶香水，认识一个以气味表达自己的名字。</p><p class="perfumery-house-names" lang="en">{names}</p><a class="text-link" href="{prefix}perfumery.html">走进 {len(selected)} 家香氛品牌 ↗</a></div><a class="perfumery-teaser-images" href="{prefix}perfumery.html" aria-label="浏览香氛与美妆栏目">{photographs}</a></section>'''


def lipstick_selection(data, root=ROOT):
    """One card per distinct container design; shade variants stay in one card."""
    from datetime import date
    from urllib.parse import urlsplit
    import re
    config = json.loads((root/'tools/research/lipstick-prices.json').read_text())
    entries = config['entries']
    brands = {b['id']: b for b in data['brands']}
    if config.get('targetCount') != 20 or len(entries) != 20:
        raise ValueError('Lipstick edit needs twenty full-size examples')
    if config.get('selectionPolicy') != 'one-card-per-container':
        raise ValueError('Lipstick edit needs the container selection policy')
    seen_ids, seen_refs, seen_cases = set(), set(), set()
    for entry in entries:
        if entry['brand'] not in brands:
            raise ValueError('Lipstick prices need existing brand archives')
        identity = (entry['brand'], entry['reference'])
        if not re.fullmatch(r'[a-z0-9-]+', entry['id']) or entry['id'] in seen_ids or identity in seen_refs:
            raise ValueError('Lipstick IDs and brand references must be unique')
        seen_ids.add(entry['id'])
        seen_refs.add(identity)
        case = entry.get('packagingId', '')
        if not re.fullmatch(r'[a-z0-9-]+', case) or case in seen_cases or not entry.get('packagingTitleZh') or not entry.get('packagingSource'):
            raise ValueError('Lipstick container designs must be unique and sourced')
        seen_cases.add(case)
        if entry.get('kind') != 'full-size' or entry.get('currency') != 'USD' or 'refill' in entry:
            raise ValueError('Lipstick prices require full-size format and USD, without refill quotes')
        if entry.get('priceStatus') != 'official-snapshot' or not entry.get('reference') or not entry.get('method'):
            raise ValueError('Lipstick quote needs a specific sourced reference')
        if type(entry.get('priceUSD')) not in (int, float) or not 0 < entry['priceUSD'] < 1000:
            raise ValueError('Invalid lipstick price')
        components = entry.get('fullSizeComponents', [])
        if components and (len(components) != 2 or sum(p['priceUSD'] for p in components) != entry['priceUSD'] or not entry.get('priceBasisZh')):
            raise ValueError('Complete lipstick price must include its case and colour')
        for offer in [entry] + components:
            date.fromisoformat(offer['checkedAt'])
            if urlsplit(offer['source']).scheme != 'https':
                raise ValueError('Lipstick quote needs a source URL')
    return [(entry, brands[entry['brand']]) for entry in entries]


def annotate_lipstick_brands(data):
    """Separate beauty-note coverage from the core and annual catalog counts."""
    selected = lipstick_selection(data)
    for brand in data['brands']:
        brand['lipstickCount'] = sum(e['brand'] == brand['id'] for e, _ in selected)
    return selected


def brand_lipstick_links(selected, brand_id, price_text):
    entries = [e for e, _ in selected if e['brand'] == brand_id]
    if not entries:
        return ''
    links = ''.join(f'<li><a href="../perfumery.html#lipstick-{e["id"]}"><span lang="en">{escape(e["series"])}</span> · {escape(e["packagingTitleZh"])} ↗</a><span>{price_text(e["priceUSD"])}</span></li>' for e in entries)
    return f'<section class="section brand-lipsticks" id="catalog-lipstick"><p class="eyebrow">LIPSTICK / THE CONTAINER EDIT</p><h2>口红 · 包装设计</h2><p class="section-intro">本站收录 {len(entries)} 款容器设计；同壳色号合并展示。正装价格为所列版本的美国官网美元参考，未含税。</p><ul>{links}</ul></section>'


def lipstick_guide(data, price_text):
    selected = lipstick_selection(data)
    prices = [e['priceUSD'] for e, _ in selected]
    cards, first_by_brand = [], {}
    for entry, brand in selected:
        label = entry.get('brandLabel', brand['name'])
        first_by_brand.setdefault(entry['brand'], (entry['id'], label))
        photograph = f'''<figure><a class="lipstick-photo lipstick-photo-{entry['brand']}" href="{escape(entry['image'])}" target="_blank" rel="noopener noreferrer" aria-label="放大查看 {escape(label)} {escape(entry['series'])} 容器实物图"><img src="{escape(entry['image'])}" width="{entry['imageWidth']}" height="{entry['imageHeight']}" alt="{escape(entry['imageAlt'])}" loading="lazy" decoding="async"></a><figcaption><a href="{escape(entry['imageSourcePage'], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(entry['imageCredit'])} ↗</a></figcaption></figure>'''
        alternatives = ''
        if entry.get('colourAlternatives'):
            alternatives = '<details class="lipstick-colours"><summary>同壳其他版本 · 合并查看</summary><p lang="en">'+escape(' / '.join(entry['colourAlternatives']))+'</p></details>'
        anchors = ''.join(f'<span id="lipstick-{escape(i)}" class="lipstick-merged-anchor"></span>' for i in entry.get('mergedIds', []))
        basis = f'<small>{escape(entry["priceBasisZh"])}</small>' if entry.get('priceBasisZh') else ''
        cards.append(f'''<article class="lipstick-card" id="lipstick-{entry['id']}">{anchors}{photograph}<div class="lipstick-card-copy"><h3><a href="brand/{brand['id']}.html">{escape(label)} ↗</a></h3><p class="lipstick-series" lang="en">{escape(entry['series'])}</p><h4 class="lipstick-case-title">{escape(entry['packagingTitleZh'])}</h4><p class="lipstick-description">{escape(entry['descriptionZh'])}</p><p class="lipstick-shade">图示参考：<span lang="en">{escape(entry['sample'])}</span></p>{alternatives}<dl class="lipstick-offers"><div><dt>正装 · USD</dt><dd><a href="{escape(entry['source'], quote=True)}" target="_blank" rel="noopener noreferrer">{price_text(entry['priceUSD'])} ↗</a>{basis}<small><time datetime="{entry['checkedAt']}">{entry['checkedAt']}</time> 复核</small></dd></div></dl></div></article>''')
    shortcuts = ''.join(f'<a href="#lipstick-{identity}">{escape(label)} <span>{sum(e["brand"]==brand_id for e, _ in selected)}</span></a>' for brand_id, (identity, label) in first_by_brand.items())
    return f'''<section class="lipstick-market" id="lipstick-prices" aria-labelledby="lipstick-prices-title"><header><p class="eyebrow rose-text">BEAUTY NOTES / THE LIPSTICK CONTAINER EDIT</p><h2 id="lipstick-prices-title">口红，先看外壳与价格</h2><p>从 {len(first_by_brand)} 个品牌选出 {len(selected)} 种包装设计：看管身轮廓、表面细节与容器结构。同一外壳的不同色号合并展示，每张卡片只用一张代表图。本组选款正装参考价为 <strong>{price_text(min(prices))}–{price_text(max(prices))}</strong>；图片可点击放大。</p><p class="lipstick-price-caption">仅列正装价格 · 美国官网参考 · USD · 未含税</p><nav class="lipstick-shortcuts" aria-label="跳至口红品牌">{shortcuts}</nav></header><div class="lipstick-card-grid">{''.join(cards)}</div><div class="lipstick-reading"><p><strong>先看容器。</strong>把花卉外壳、雕花金管、双镜盒与铆钉管放在一起比较。相同外壳的其他色号只作文字补充，图中色号用于辨认所示版本。</p><p><strong>再看完整正装价格。</strong>价格对应所列包装。需要自选外壳与膏体的产品，会注明完整组合的价格口径；套装、迷你装和单独外壳不作为一整支口红比较。</p><p><strong>把价格当预算线索。</strong>这些是逐项注明日期的官网参考；价格差本身不能说明妆效或适合程度。点击价格查看来源，展示颜色以实物为准。</p></div></section>'''


def render(data, page, price_text, review_span):
    selected = selection(data)
    count = len(selected)
    count_en = {3:'Three', 4:'Four', 5:'Five'}[count]
    shortcuts = ''.join(f'<a href="#house-{b["id"]}">{escape(b["name"])}</a>' for _, b, _ in selected)
    shortcuts += '<a href="#lip-care">男士日常润唇 ↗</a><a href="#color-changing-balms">变色润唇 ↗</a><a href="#lipstick-prices">口红价格速览 ↗</a>'
    rows = []
    for index, (entry, brand, product) in enumerate(selected, 1):
        loading = 'fetchpriority="high"' if index == 1 else 'loading="lazy"'
        image = f'<a class="perfumery-photograph" href="item/{product["id"]}.html"><img src="{escape(product["image"])}" width="{product["imageWidth"]}" height="{product["imageHeight"]}" alt="{escape(brand["name"]+" "+product["name"]+" — "+product["color"])}" {loading}><span>{escape(product["imageCredit"])}</span></a>'
        rows.append(f'''<article class="perfumery-house" id="house-{brand['id']}">{image}<div class="perfumery-house-copy"><p class="eyebrow rose-text">{index:02} / {escape(brand['country'])} / EST. {brand['founded']}</p><h2>{escape(brand['name'])}</h2><p class="perfumery-house-zh">{escape(brand['nameZh'])} · {escape(brand['tagline'])}</p><p>{escape(entry['introZh'])}</p><a class="text-link" href="brand/{brand['id']}.html">品牌故事与时间线 ↗</a><div class="perfumery-bottle" lang="en"><p class="eyebrow">A FIRST ENCOUNTER</p><h3><a href="item/{product['id']}.html">{escape(product['name'])} ↗</a></h3><p>{escape(' · '.join(product['sizes']))}</p><p class="perfumery-scent">{escape(entry['scentEn'])}</p><p>{escape(product['oneLiner'])}</p><p class="perfumery-price">{price_text(product['priceUSD'])} <span>USD · before tax</span></p><p class="perfumery-price-context">{escape(product['priceContextEn'])}</p><a class="text-link" href="item/{product['id']}.html">Photographs & design notes ↗</a></div></div></article>''')
    content = f'''<div class="container perfumery-page"><nav class="breadcrumbs" aria-label="面包屑"><a href="index.html">首页</a><span>/</span><span aria-current="page">{TITLE_ZH}</span></nav><header class="perfumery-opening"><p class="eyebrow rose-text">PERFUMERY &amp; BEAUTY / VOL. 01</p><h1>把气味，读成一个名字<span class="rose-dot">。</span></h1><p class="perfumery-english" lang="en">{count_en} houses. {count_en} ways to leave an impression.</p><p>香水、香氛与居家气味，是这些品牌的重要表达。先读品牌故事，再从一款代表作认识它的气味语言；木质、花香、琥珀与清新气息，各有不同的入口。另附无色与变色润唇膏选集，以及口红包装价格速览。</p><nav class="perfumery-shortcuts" aria-label="跳至本页板块">{shortcuts}</nav></header><div class="perfumery-houses">{''.join(rows)}</div><aside class="perfumery-reading"><p class="eyebrow">BEFORE YOU CHOOSE</p><h2>先试闻，再决定</h2><p>这里是编辑选集。每款价格只对应所列容量与浓度，美元价格未含税；同名作品的 Eau de Parfum、Extrait 与 Cologne 需分别确认。香调词描述气味印象，不是完整配方，也不能保证在每个人皮肤上的留香表现。</p><p lang="en">Official U.S. sources reviewed {escape(review_span([p for _, _, p in selected]))}. Confirm the current price and availability with the brand. Each detail page credits its original photographs.</p><a class="text-link" href="cat/fragrance.html">继续读香水经典与其他款式 ↗</a></aside>{lip_balms.render(data, price_text)}{color_balms.render(data, price_text)}{lipstick_guide(data, price_text)}</div>'''
    page('perfumery.html', TITLE_EN, f'走进 {count} 家香氛品牌，阅读代表香水与美元价格；附无色与变色润唇膏及20种口红包装的实物图、说明与正装美元价格。', content, 'perfumery')
