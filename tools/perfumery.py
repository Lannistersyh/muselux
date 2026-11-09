"""A sourced fragrance-house column within the existing fragrance category."""
from html import escape
from pathlib import Path
import json

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
    """Keep full lipstick prices and compatible refills distinct and sourced."""
    from datetime import date
    from urllib.parse import urlsplit
    entries = json.loads((root/'tools/research/lipstick-prices.json').read_text())['entries']
    brands = {b['id']: b for b in data['brands']}
    seen = set()
    if not 3 <= len(entries) <= 5:
        raise ValueError('Lipstick price note needs three to five brands')
    for entry in entries:
        if entry['brand'] not in brands or entry['brand'] in seen:
            raise ValueError('Lipstick prices need distinct existing brands')
        seen.add(entry['brand'])
        for offer, kind in [(entry, 'full-size')] + ([(entry['refill'], 'refill')] if entry.get('refill') else []):
            if offer.get('kind') != kind or offer.get('currency') != 'USD':
                raise ValueError('Lipstick full-size/refill format and USD must be explicit')
            if offer.get('priceStatus') != 'official-snapshot' or not offer.get('reference') or not offer.get('method'):
                raise ValueError('Lipstick quote needs a specific sourced reference')
            if type(offer.get('priceUSD')) not in (int, float) or not 0 < offer['priceUSD'] < 1000:
                raise ValueError('Invalid lipstick price')
            date.fromisoformat(offer['checkedAt'])
            if urlsplit(offer['source']).scheme != 'https':
                raise ValueError('Lipstick quote needs a source URL')
    return [(entry, brands[entry['brand']]) for entry in entries]


def lipstick_guide(data, price_text):
    selected = lipstick_selection(data)
    prices = [e['priceUSD'] for e, _ in selected]
    rows = []
    for entry, brand in selected:
        refill = entry.get('refill')
        refill_html = (f'<a href="{escape(refill["source"], quote=True)}" target="_blank" rel="noopener noreferrer">{price_text(refill["priceUSD"])} ↗</a>'
                       f'<small>仅膏芯 · <time datetime="{refill["checkedAt"]}">{refill["checkedAt"]}</time> 复核</small>') if refill else '<span class="lipstick-unquoted">—</span><small>本次未收录报价</small>'
        rows.append(f'''<tr><th scope="row"><a href="brand/{brand['id']}.html">{escape(brand['name'])} ↗</a></th><td class="lipstick-sample"><span lang="en">{escape(entry['series'])}</span><small>{escape(entry['noteZh'])} · <span lang="en">{escape(entry['sample'])}</span></small></td><td class="lipstick-quote" data-label="正装"><a href="{escape(entry['source'], quote=True)}" target="_blank" rel="noopener noreferrer">{price_text(entry['priceUSD'])} ↗</a><small><time datetime="{entry['checkedAt']}">{entry['checkedAt']}</time> 复核</small></td><td class="lipstick-refill" data-label="补充装">{refill_html}</td></tr>''')
    return f'''<section class="lipstick-market" id="lipstick-prices" aria-labelledby="lipstick-prices-title"><header><p class="eyebrow rose-text">BEAUTY NOTES / THE PRICE OF A LIPSTICK</p><h2 id="lipstick-prices-title">口红，先看价格</h2><p>用 {len(selected)} 个品牌的具体正装样本，认识口红的消费价格。本组选取的官网参考价为 <strong>{price_text(min(prices))}–{price_text(max(prices))}</strong>；这是样本跨度，不是全市场均价或各品牌的完整价格范围。</p></header><table class="lipstick-price-table"><caption>美国官网参考价 · USD · 未含税</caption><thead><tr><th scope="col">品牌</th><th scope="col">参考系列 / 样本</th><th scope="col">正装</th><th scope="col">补充装</th></tr></thead><tbody>{''.join(rows)}</tbody></table><div class="lipstick-reading"><p><strong>先分清正装和补充装。</strong>补充装需要兼容的外壳；已有外壳再比较膏芯价格，首次购买先看正装。破折号表示本次没有收录该项报价。</p><p><strong>再看折扣与套装。</strong>比较同一系列、规格和包装的税后实付价；套装要逐件核对容量，赠品和迷你装不按正装支数计算。</p><p><strong>把价格当预算线索。</strong>这些是逐项注明日期的官网快照；价格差本身不能说明妆效或适合程度。色号仅用于核对样本，点击价格可查看官方页面。</p></div></section>'''


def render(data, page, price_text, review_span):
    selected = selection(data)
    count = len(selected)
    count_en = {3:'Three', 4:'Four', 5:'Five'}[count]
    shortcuts = ''.join(f'<a href="#house-{b["id"]}">{escape(b["name"])}</a>' for _, b, _ in selected)
    shortcuts += '<a href="#lipstick-prices">口红价格速览 ↗</a>'
    rows = []
    for index, (entry, brand, product) in enumerate(selected, 1):
        loading = 'fetchpriority="high"' if index == 1 else 'loading="lazy"'
        image = f'<a class="perfumery-photograph" href="item/{product["id"]}.html"><img src="{escape(product["image"])}" width="{product["imageWidth"]}" height="{product["imageHeight"]}" alt="{escape(brand["name"]+" "+product["name"]+" — "+product["color"])}" {loading}><span>{escape(product["imageCredit"])}</span></a>'
        rows.append(f'''<article class="perfumery-house" id="house-{brand['id']}">{image}<div class="perfumery-house-copy"><p class="eyebrow rose-text">{index:02} / {escape(brand['country'])} / EST. {brand['founded']}</p><h2>{escape(brand['name'])}</h2><p class="perfumery-house-zh">{escape(brand['nameZh'])} · {escape(brand['tagline'])}</p><p>{escape(entry['introZh'])}</p><a class="text-link" href="brand/{brand['id']}.html">品牌故事与时间线 ↗</a><div class="perfumery-bottle" lang="en"><p class="eyebrow">A FIRST ENCOUNTER</p><h3><a href="item/{product['id']}.html">{escape(product['name'])} ↗</a></h3><p>{escape(' · '.join(product['sizes']))}</p><p class="perfumery-scent">{escape(entry['scentEn'])}</p><p>{escape(product['oneLiner'])}</p><p class="perfumery-price">{price_text(product['priceUSD'])} <span>USD · before tax</span></p><p class="perfumery-price-context">{escape(product['priceContextEn'])}</p><a class="text-link" href="item/{product['id']}.html">Photographs & design notes ↗</a></div></div></article>''')
    content = f'''<div class="container perfumery-page"><nav class="breadcrumbs" aria-label="面包屑"><a href="index.html">首页</a><span>/</span><span aria-current="page">{TITLE_ZH}</span></nav><header class="perfumery-opening"><p class="eyebrow rose-text">PERFUMERY &amp; BEAUTY / VOL. 01</p><h1>把气味，读成一个名字<span class="rose-dot">。</span></h1><p class="perfumery-english" lang="en">{count_en} houses. {count_en} ways to leave an impression.</p><p>香水、香氛与居家气味，是这些品牌的重要表达。先读品牌故事，再从一款代表作认识它的气味语言；木质、花香、琥珀与清新气息，各有不同的入口。另附一份简洁的口红价格速览。</p><nav class="perfumery-shortcuts" aria-label="跳至本页板块">{shortcuts}</nav></header><div class="perfumery-houses">{''.join(rows)}</div><aside class="perfumery-reading"><p class="eyebrow">BEFORE YOU CHOOSE</p><h2>先试闻，再决定</h2><p>这里是编辑选集。每款价格只对应所列容量与浓度，美元价格未含税；同名作品的 Eau de Parfum、Extrait 与 Cologne 需分别确认。香调词描述气味印象，不是完整配方，也不能保证在每个人皮肤上的留香表现。</p><p lang="en">Official U.S. sources reviewed {escape(review_span([p for _, _, p in selected]))}. Confirm the current price and availability with the brand. Each detail page credits its original photographs.</p><a class="text-link" href="cat/fragrance.html">继续读香水经典与其他款式 ↗</a></aside>{lipstick_guide(data, price_text)}</div>'''
    page('perfumery.html', TITLE_EN, f'走进 {count} 家香氛品牌，阅读代表香水与美元价格；附五个品牌的口红正装、补充装价格速览。', content, 'perfumery')
