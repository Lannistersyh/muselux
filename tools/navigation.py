"""Presentation hierarchy; existing product categories and URLs stay stable."""
from html import escape

JEWELRY_CATEGORIES = ('necklace', 'jewelry')


def primary(categories, active_category='', prefix='', jewelry_hub=False):
    links = []
    for category in categories:
        identity = category['id']
        if identity == 'necklace':
            continue
        jewelry = identity == 'jewelry'
        active = (jewelry_hub or active_category in JEWELRY_CATEGORIES) if jewelry else active_category == identity
        href = 'jewelry.html' if jewelry else 'cat/'+identity+'.html'
        label = '珠宝与配饰' if jewelry else category['nameZh']
        links.append(f'<a class="{"active" if active else ""}" href="{prefix}{href}"'+(' aria-current="location"' if active else '')+f'>{escape(label)}</a>')
    return ''.join(links)


def jewelry_trail(category, prefix):
    if category not in JEWELRY_CATEGORIES:
        return ''
    links = [f'<a href="{prefix}jewelry.html">珠宝与配饰总览 ↗</a>']
    for identity, label in (('necklace', '项链与吊坠'), ('jewelry', '其他首饰与配饰')):
        links.append(f'<a href="{prefix}cat/{identity}.html"'+(' aria-current="location"' if category == identity else '')+f'>{label}</a>')
    return '<nav class="container collection-trail" aria-label="珠宝与配饰分类">'+''.join(links)+'</nav>'


def render_jewelry(data, page, card):
    groups = []
    for identity, title, description in (
        ('necklace', '项链与吊坠', '从链条、吊坠到层叠珠链，读颈间的形状。'),
        ('jewelry', '其他首饰与配饰', '戒指、手链与耳饰是主角；经典档案另收录鞋履与墨镜。'),
    ):
        products = [p for p in data['items'] if p.get('styleEdit') and p['category'] == identity]
        groups.append(f'<section class="section" id="collection-{identity}"><div class="section-head"><div><p class="eyebrow">{len(products):02} / PHOTOGRAPHED PIECES</p><h2>{title}</h2></div><a class="text-link" href="cat/{identity}.html">查看全部款式与年度精选 ↗</a></div><p class="section-intro">{description}</p><div class="collection-preview">'+''.join(card(p) for p in products[:3])+'</div></section>')
    content = '<div class="container"><nav class="breadcrumbs" aria-label="面包屑"><a href="index.html">首页</a><span>/</span><span aria-current="page">珠宝与配饰</span></nav><header class="perfumery-opening"><p class="eyebrow rose-text">JEWELRY &amp; ACCESSORIES</p><h1>从一件小物，读懂风格。</h1><p>项链属于首饰。在这里，先按佩戴部位找到款式，再读材质、设计故事与美元参考价。</p><nav class="perfumery-shortcuts" aria-label="选择珠宝分类"><a href="#collection-necklace">项链与吊坠</a><a href="#collection-jewelry">其他首饰与配饰</a></nav></header>'+''.join(groups)+'</div>'
    page('jewelry.html', 'Jewelry & Accessories', '项链与吊坠、戒指、手链、耳饰与生活配饰：实物款式、美元参考价格及年度精选。', content, 'jewelry-hub')
