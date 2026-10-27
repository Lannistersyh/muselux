"""A sourced fragrance-house column within the existing fragrance category."""
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


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
    return f'''<section class="perfumery-teaser" aria-labelledby="perfumery-teaser-title"><div><p class="eyebrow rose-text">THE PERFUMERY EDIT / A NEW CHAPTER</p><h2 id="perfumery-teaser-title">香氛品牌</h2><p>从一瓶香水，认识一个以气味表达自己的名字。</p><p class="perfumery-house-names" lang="en">{names}</p><a class="text-link" href="{prefix}perfumery.html">走进 {len(selected)} 家香氛品牌 ↗</a></div><a class="perfumery-teaser-images" href="{prefix}perfumery.html" aria-label="浏览香氛品牌栏目">{photographs}</a></section>'''


def render(data, page, price_text, review_span):
    selected = selection(data)
    count = len(selected)
    count_en = {3:'Three', 4:'Four', 5:'Five'}[count]
    shortcuts = ''.join(f'<a href="#house-{b["id"]}">{escape(b["name"])}</a>' for _, b, _ in selected)
    rows = []
    for index, (entry, brand, product) in enumerate(selected, 1):
        loading = 'fetchpriority="high"' if index == 1 else 'loading="lazy"'
        image = f'<a class="perfumery-photograph" href="item/{product["id"]}.html"><img src="{escape(product["image"])}" width="{product["imageWidth"]}" height="{product["imageHeight"]}" alt="{escape(brand["name"]+" "+product["name"]+" — "+product["color"])}" {loading}><span>{escape(product["imageCredit"])}</span></a>'
        rows.append(f'''<article class="perfumery-house" id="house-{brand['id']}">{image}<div class="perfumery-house-copy"><p class="eyebrow rose-text">{index:02} / {escape(brand['country'])} / EST. {brand['founded']}</p><h2>{escape(brand['name'])}</h2><p class="perfumery-house-zh">{escape(brand['nameZh'])} · {escape(brand['tagline'])}</p><p>{escape(entry['introZh'])}</p><a class="text-link" href="brand/{brand['id']}.html">品牌故事与时间线 ↗</a><div class="perfumery-bottle" lang="en"><p class="eyebrow">A FIRST ENCOUNTER</p><h3><a href="item/{product['id']}.html">{escape(product['name'])} ↗</a></h3><p>{escape(' · '.join(product['sizes']))}</p><p class="perfumery-scent">{escape(entry['scentEn'])}</p><p>{escape(product['oneLiner'])}</p><p class="perfumery-price">{price_text(product['priceUSD'])} <span>USD · before tax</span></p><p class="perfumery-price-context">{escape(product['priceContextEn'])}</p><a class="text-link" href="item/{product['id']}.html">Photographs & design notes ↗</a></div></div></article>''')
    content = f'''<div class="container perfumery-page"><nav class="breadcrumbs" aria-label="面包屑"><a href="index.html">首页</a><span>/</span><span aria-current="page">香氛品牌</span></nav><header class="perfumery-opening"><p class="eyebrow rose-text">THE PERFUMERY EDIT / VOL. 01</p><h1>把气味，读成一个名字<span class="rose-dot">。</span></h1><p class="perfumery-english" lang="en">{count_en} houses. {count_en} ways to leave an impression.</p><p>香水、香氛与居家气味，是这些品牌的重要表达。先读品牌故事，再从一款代表作认识它的气味语言；木质、花香、琥珀与清新气息，各有不同的入口。</p><nav class="perfumery-shortcuts" aria-label="跳至香氛品牌">{shortcuts}</nav></header><div class="perfumery-houses">{''.join(rows)}</div><aside class="perfumery-reading"><p class="eyebrow">BEFORE YOU CHOOSE</p><h2>先试闻，再决定</h2><p>这里是编辑选集。每款价格只对应所列容量与浓度，美元价格未含税；同名作品的 Eau de Parfum、Extrait 与 Cologne 需分别确认。香调词描述气味印象，不是完整配方，也不能保证在每个人皮肤上的留香表现。</p><p lang="en">Official U.S. sources reviewed {escape(review_span([p for _, _, p in selected]))}. Confirm the current price and availability with the brand. Each detail page credits its original photographs.</p><a class="text-link" href="cat/fragrance.html">继续读香水经典与其他款式 ↗</a></aside></div>'''
    page('perfumery.html', '香氛品牌 · The Perfumery Edit', f'走进 {count} 家香氛品牌，阅读品牌故事、代表香水、英文气味笔记、实物照片与有来源的美元价格。', content, 'perfumery')
