"""Rebuild static pages and the offline data script. Python standard library only."""
from pathlib import Path
import json, html, re, gzip, base64, hashlib, unicodedata
from urllib.parse import urlsplit
import bag_yearbook
import brand_catalog
import product_gallery
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
SITE=json.loads((ROOT/'tools/site.json').read_text()) if (ROOT/'tools/site.json').exists() else {}
SITE_URL=SITE.get('url','').rstrip('/')+'/' if SITE.get('url') else ''
D=json.loads((ROOT/'tools/content.json').read_text())
GALLERIES=product_gallery.load()
CATALOG=brand_catalog.enrich(D)
C={x['id']:x for x in D['categories']}
B={x['id']:x for x in D['brands']}
I={x['id']:x for x in D['items']}
A={x['id']:x for x in D['articles']}
ALL_ITEMS={x['id']:x for x in CATALOG}
DISCLAIMER='MuseLux 是个人兴趣驱动的非商业内容项目，所有品牌名称与产品名称的权利归其权利人所有；价格信息仅为整理时的公开参考，请以品牌官方渠道为准。'
ABOUT='MuseLux 是一个关于奢侈品的品味网站——把百年工坊的故事，讲成日常的向往。'
e=html.escape
def article_date(article):
    return date.fromisoformat(article['date']).strftime('%Y.%m.%d')

def json_script(value):
    # A product name from an external source must not terminate the JSON-LD tag.
    return json.dumps(value,ensure_ascii=False).replace('<','\\u003c')

def review_span(products):
    dates=sorted({date.fromisoformat(x['checkedAt']).isoformat() for x in products})
    if not dates:raise ValueError('No reviewed products')
    return bag_yearbook.date_label(dates[0]) if len(dates)==1 else bag_yearbook.date_label(dates[0])+'–'+bag_yearbook.date_label(dates[-1])

def icon(name):
    paths={
      'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>',
      'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
      'bags':'<path d="M5 8h14l1 12H4L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
      'necklace':'<path d="M4 4c0 12 16 12 16 0M10 16l2-3 2 3-2 4-2-4Z"/>',
      'jewelry':'<circle cx="12" cy="14" r="6"/><path d="m8 8 1-5h6l1 5M9 3l3 5 3-5"/>',
      'watches':'<rect x="6" y="6" width="12" height="12" rx="4"/><path d="M9 6V2h6v4M9 18v4h6v-4m-3-13v5l3 2"/>',
      'scarves':'<path d="m5 3 14 3-4 6 3 8-6-2-4 3 1-10-4-8Z"/><path d="m5 3 7 8 7-5m-7 5 3 1"/>',
      'fragrance':'<rect x="5" y="8" width="14" height="13" rx="2"/><path d="M8 8V4h8v4M8 4V2h8v2m-7 9h6v4H9z"/>',
      'up':'<path d="M12 20V4m-6 6 6-6 6 6"/>',
      'menu':'<path d="M3 7h18M3 12h18M3 17h18"/>',
      'close':'<path d="m6 6 12 12M6 18 18 6"/>',
    }
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[name]+'</svg>'

LOGO='''<svg class="logo" viewBox="0 0 210 78" role="img" aria-label="MuseLux，品味、工艺、传奇"><path d="M7 42Q60 14 119 37" fill="none" stroke="currentColor" stroke-width=".7"/><text x="12" y="39" font-family="Snell Roundhand,Apple Chancery,cursive" font-style="italic" font-size="35">muse</text><text x="111" y="44" font-family="Georgia,serif" font-size="30" letter-spacing="4">LUX</text><path d="M111 52q45-6 83-2l-65 3 59 2" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="197" cy="38" r="3" fill="#c98a8e"/><text x="33" y="70" font-family="PingFang SC,sans-serif" font-size="8" letter-spacing="4">品味 · 工艺 · 传奇</text></svg>'''

def card(x,kind='article',prefix='',big=False):
    if kind=='article':
        cat=C[x['category']]
        return f'''<article class="story-card reveal{' feature-large' if big else ''}"><a class="card-image" href="{prefix}mag/{x['id']}.html" tabindex="-1" aria-hidden="true"><img src="{prefix}{x['cover']}" width="720" height="480" loading="lazy" alt="{e(x.get('coverAlt') or x['title'].split('｜')[0]+'的原创专题插画')}"></a><div class="card-body"><div class="card-kicker"><a class="tag" href="{prefix}cat/{cat['id']}.html">{cat['nameZh']}</a><span class="eyebrow">THE JOURNAL</span></div><h3><a href="{prefix}mag/{x['id']}.html">{e(x['title'])}</a></h3><p class="card-excerpt">{e(x['excerpt'])}</p><div class="card-meta"><time datetime="{x['date']}">{article_date(x)}</time><span>约 {x['readMins']} 分钟</span><span class="card-arrow">↗</span></div></div></article>'''
    if x.get('styleEdit'):
        return stylecard(x,prefix)
    if x.get('annualEdit'):
        return bag_yearbook.card(x,prefix)
    b=B[x['brand']]
    return f'''<article class="item-card reveal"><a href="{prefix}item/{x['id']}.html"><div class="item-image"><img src="{prefix}assets/img/{x['id']}.svg" width="720" height="480" loading="lazy" alt="{e(b['name']+' '+x['name']+' '+x['nameZh'])}的概念插画，非实物图"></div><div class="item-body"><span class="eyebrow">{e(b['name'])}</span><h3>{e(x['name'])}<span>{e(x['nameZh'])}</span></h3><p>{e(x['oneLiner'])}</p><span class="text-link">打开词条 <span>↗</span></span></div></a></article>'''

def usd(amount):
    return bag_yearbook.price_text({'priceUSD':amount})

def stylecard(x,prefix=''):
    b=B[x['brand']]
    return f'''<article class="item-card product-card reveal" lang="en"><a href="{prefix}item/{x['id']}.html"><div class="product-image"><img src="{prefix}{x['image']}" width="{x['imageWidth']}" height="{x['imageHeight']}" loading="lazy" alt="{e(b['name']+' '+x['name']+' — '+x['color'])}"><span class="product-index">THE STYLE EDIT</span></div><div class="item-body"><span class="eyebrow">{e(b['name'])}</span><h3>{e(x['name'])}</h3><p>{e(x['oneLiner'])}</p><div class="product-card-bottom"><span class="product-price">{usd(x['priceUSD'])}</span><span class="product-open">Explore ↗</span></div><span class="product-price-note">U.S. reference · before tax</span>{'<span class="product-reference">'+e(x["priceContextEn"])+'</span>' if x["priceStatus"]=="official-snapshot" else ""}</div></a></article>'''

def price_note(products=None):
    products=products or [x for x in D['items'] if x.get('styleEdit')]
    return '<p class="edit-price-note" lang="en">USD references for the pictured variants, before tax. Sources reviewed '+e(review_span(products))+'; dated official snapshots are labelled individually. Confirm the latest price and availability with the official U.S. store.</p>'

def style_edit(prefix='',category=None):
    cats=[category] if category else D['categories']
    groups=[];shown=[]
    for c in cats:
        products=[x for x in D['items'] if x.get('styleEdit') and x['category']==c['id']]
        if not products:continue
        shown.extend(products)
        groups.append(f'''<div class="edit-panel" id="edit-{c['id']}" data-edit-panel="{c['id']}"><div class="edit-panel-heading" lang="en"><h3>{e(c['nameEn'].title())}</h3><p>{e(c.get('editIntro','Four considered pieces, with design notes and U.S. reference prices.'))}</p></div><div class="product-grid">{''.join(stylecard(x,prefix) for x in products)}</div></div>''')
    if not groups:return ''
    tabs='' if category else '<div class="edit-tabs" hidden role="group" aria-label="Choose a product category">'+''.join(f'<button type="button" data-edit="{c["id"]}" aria-controls="edit-{c["id"]}" aria-pressed="true">{e(c["nameEn"].title())} <span>{c["nameZh"]}</span></button>' for c in cats)+'</div>'
    return f'''<section class="style-edit{' section' if not category else ''}" id="style-edit">{sectionhead('REAL PIECES. CONSIDERED DETAILS.','The Style Edit')}<p class="section-intro" lang="en">A closer look at beautiful things. Discover the shapes, materials and details behind each piece.</p>{tabs}{''.join(groups)}{price_note(shown)}</section>'''

def edit_hero(cats):
    x=next(x for x in D['items'] if x.get('styleEdit') and x['category']=='bags')
    b=B[x['brand']]
    return f'''<section class="hero hero-with-product"><div class="container hero-inner"><div class="hero-copy" lang="en"><p class="eyebrow rose-text"><span class="little-rule"></span> THE STYLE EDIT / VOL. 01</p><h1>Beautiful things.<br>Closer details<span class="rose-dot">.</span></h1><p class="hero-description">Six categories. {len([x for x in D['items'] if x.get('styleEdit')])} considered pieces.<br>Discover their shape, their story and the details that last.</p><a class="button button-dark" href="#style-edit">Explore the edit {icon('arrow')}</a><span class="hero-reading">A little everyday inspiration.</span></div><a class="hero-product" href="item/{x['id']}.html" lang="en"><img src="{x['image']}" width="{x['imageWidth']}" height="{x['imageHeight']}" alt="{e(b['name']+' '+x['name']+' — '+x['color'])}" fetchpriority="high"><div class="hero-product-caption"><span class="eyebrow">{e(b['name'])} / THE BAG EDIT</span><span>{e(x['name'])}</span><span>{usd(x['priceUSD'])} <small>U.S. reference · before tax</small> ↗</span></div></a><div class="hero-bottom"><div class="hero-pills">{cats}</div><span class="hero-caption">OFFICIAL PRODUCT PHOTOGRAPH · CREDIT ON DETAIL PAGE</span></div></div></section>'''

def productpage(x):
    b=B[x['brand']];c=C[x['category']]
    specs=[('Reference',x['reference']),('Colour / finish',x['color']),('Size / format',' · '.join(x['sizes'])),('Materials / notes',' · '.join(x['materials']))]
    siblings=[i for i in D['items'] if i.get('styleEdit') and i['category']==x['category'] and i['id']!=x['id']]
    archive=f'<a class="text-link" href="{x["parentItem"]}.html">Read the collection story ↗</a>' if x.get('parentItem') else ''
    content=f'''<div class="container product-detail"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../cat/{c['id']}.html">{e(c['nameEn'].title())}</a><span>/</span><span aria-current="page">The Style Edit</span></nav><section class="product-opening" lang="en">{product_gallery.render(x,GALLERIES)}<div class="product-heading"><a class="eyebrow rose-text" href="../brand/{b['id']}.html">{e(b['name'])} ↗</a><h1>{e(x['name'])}</h1><p class="product-subtitle">{e(x['color'])} · Ref. {e(x['reference'])}</p><p class="product-lede">{e(x['oneLiner'])}</p><div class="product-price-box"><span class="eyebrow">U.S. RETAIL REFERENCE</span><p class="product-detail-price">{usd(x['priceUSD'])}</p><p>Before tax · pictured reference only</p><p class="price-context">{e(x['priceContextEn'])}</p></div><a class="button button-dark official-link" href="{e(x['source'])}" target="_blank" rel="noopener">View at {e(b['name'])} ↗</a><p class="official-note">Official source for the pictured variant. Confirm the latest price and availability with the brand.</p></div></section><div class="product-notes" lang="en"><article class="prose product-prose"><p class="eyebrow rose-text">FORM / MATERIAL / EVERYDAY</p><h2>Design notes</h2><p>{e(x['introEn'])}</p><h2>Three details to notice</h2><ul>{''.join('<li>'+e(f)+'</li>' for f in x['featuresEn'])}</ul><h2>{'How to wear it' if x['category']!='fragrance' else 'The mood'}</h2><p>{e(x['stylingEn'])}</p>{archive}</article><aside class="spec-panel product-spec"><p class="eyebrow">THE PARTICULARS</p><h2>At a glance</h2><dl>{''.join(f'<div><dt>{label}</dt><dd>{e(value)}</dd></div>' for label,value in specs)}</dl><p class="product-source-note">Price applies to this reference and format. {e(x['priceLabel'])}. Product specifications and imagery are credited to {e(b['name'])}; the introduction and styling notes are original MuseLux editorial.</p><a class="source-link" href="{e(x['source'])}" target="_blank" rel="noopener">Official product &amp; price source ↗</a><a class="source-link" href="{e(x['imageSource'])}" target="_blank" rel="noopener">Original image source ↗</a></aside></div><section class="section">{sectionhead('CONTINUE THE EDIT','More to discover')}<div class="product-grid">{''.join(stylecard(i,'../') for i in siblings)}</div>{price_note([x]+siblings)}</section></div>'''
    page('item/'+x['id']+'.html',b['name']+' '+x['name'],x['oneLiner'],content,'item',x['id'],product=x)

def brandcard(b,prefix=''):
    label='联名品牌 · ' if b.get('role')=='collaborator' else ''
    return f'''<a class="brand-card reveal" href="{prefix}brand/{b['id']}.html"><span class="eyebrow">{e(b['country'])} · EST. {b['founded']}</span><h3>{e(b['name'])}</h3><span class="brand-zh">{b['nameZh']}</span><p>{b['tagline']}</p><span class="brand-card-bottom">{label}本站收录 {b['itemCount']} 项 <span>↗</span></span></a>'''

def crumbs(parts,prefix):
    return '<nav class="breadcrumbs" aria-label="面包屑"><a href="'+prefix+'index.html">首页</a>'+''.join(' <span>/</span> '+(f'<a href="{url}">{e(label)}</a>' if url else f'<span aria-current="page">{e(label)}</span>') for label,url in parts)+'</nav>'

def headsection(kicker,title,desc,count=''):
    return f'<div class="page-heading"><div><p class="eyebrow">{kicker}</p><h1>{e(title)}</h1><p>{e(desc)}</p></div><span class="heading-number">{count}</span></div>'

def sectionhead(kicker,title,link=None):
    return f'<div class="section-head"><div><p class="eyebrow">{kicker}</p><h2>{title}</h2></div>'+ (f'<a class="text-link" href="{link[1]}">{link[0]} <span>↗</span></a>' if link else '')+'</div>'

pages=[]
asset_versions={}
def asset_url(prefix,path):
    if path not in asset_versions:asset_versions[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]
    return prefix+path+'?v='+asset_versions[path]

def page(path,title,desc,content,pagekind='generic',pageid='',article=None,product=None):
    prefix='../' if '/' in path else ''
    current=pagekind
    canonical=SITE_URL+('' if path=='index.html' else path) if SITE_URL else ''
    hosting_meta=f'<link rel="canonical" href="{e(canonical)}"><meta property="og:url" content="{e(canonical)}">' if canonical else ''
    fallback_base=''
    if pagekind=='404' and SITE_URL:
        fallback_base='<script>(function(){if(location.protocol!=="file:"&&location.hostname==='+json.dumps(urlsplit(SITE_URL).hostname)+'){var b=document.createElement("base");b.href='+json.dumps(SITE_URL)+';document.head.appendChild(b)}})();</script><meta name="robots" content="noindex">'
    annual_category=product['category'] if product and product.get('annualEdit') else pageid if pagekind=='yearbook' else None
    nav=''.join(f'<a class="{"active" if pageid==c["id"] or annual_category==c["id"] else ""}" href="{prefix}cat/{c["id"]}.html">{c["nameZh"]}</a>' for c in D['categories'])
    structured={'@context':'https://schema.org','@type':'Organization','name':'MuseLux','description':ABOUT}
    if pagekind=='yearbook':
        structured={'@context':'https://schema.org','@type':'CollectionPage','name':title,'description':desc,'inLanguage':'en'}
    if article:
        structured={'@context':'https://schema.org','@type':'Article','headline':article['title'],'datePublished':article['date'],'dateModified':article.get('updatedAt',article['date']),'inLanguage':'zh-CN','author':{'@type':'Organization','name':'MuseLux 编辑部'},'publisher':{'@type':'Organization','name':'MuseLux'},'description':article['excerpt']}
    if product:
        structured={'@context':'https://schema.org','@type':'Product','name':product['name'],'sku':product['reference'],'brand':{'@type':'Brand','name':product.get('brandName') or B[product['brand']]['name']},'description':product['oneLiner'],'image':SITE_URL+product['image'] if SITE_URL else '../'+product['image']}
    if canonical:
        structured['url']=canonical
    preview_image=product['image'] if product else (next((x['image'] for x in D['items'] if x.get('styleEdit') and x['category']=='bags'),'assets/img/hero.svg') if pagekind=='home' else 'assets/img/hero.svg')
    if pagekind=='yearbook':
        preview_image=max(D[bag_yearbook.BOOKS[pageid]['key']],key=lambda y:y['year'])['entries'][0]['image']
    og_image=(SITE_URL if SITE_URL else prefix)+preview_image
    footer=f'''<footer class="site-footer" lang="zh-CN"><div class="container footer-grid"><div><a class="footer-logo" href="{prefix}index.html">{LOGO}</a><p>{ABOUT}</p><span class="eyebrow">A LITTLE KNOWLEDGE. A LONG AFFECTION.</span></div><div><h2>慢慢探索</h2><div class="footer-links">{''.join(f'<a href="{prefix}cat/{c["id"]}.html">{c["nameZh"]}</a>' for c in D['categories'])}<a href="{prefix}bags-by-year.html">包袋年份 · 2022–26</a><a href="{prefix}necklaces-by-year.html">项链年份 · 2022–26</a><a href="{prefix}jewelry-by-year.html">首饰年份 · 2022–26</a><a href="{prefix}brands.html">品牌索引</a><a href="{prefix}search.html">站内搜索</a><a href="{prefix}about.html">关于本站</a><a href="{prefix}about.html#sources">资料与来源</a></div></div><div><h2>一份小小的说明</h2><p>{DISCLAIMER}</p><p>实物图来源与署名见各款详情；概念插画另有标注。<br>在这里，先了解，再慢慢喜欢。</p></div></div><div class="container footer-bottom"><span>© 2026 MUSELUX · AN INDEPENDENT JOURNAL</span><span>用好奇心，收藏日常的美。</span></div></footer>'''
    urls={'css':asset_url(prefix,'assets/css/main.css'),**{name:asset_url(prefix,'assets/js/'+name) for name in ('data.js','render.js','main.js')}}
    out=f'''<!doctype html>
<html lang="{'en' if product or pagekind=='yearbook' else 'zh-CN'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#faf8f5"><title>{e(title)}｜MuseLux</title><meta name="description" content="{e(desc[:110])}"><meta property="og:title" content="{e(title)}｜MuseLux"><meta property="og:description" content="{e(desc[:110])}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:image" content="{e(og_image)}">{hosting_meta}{fallback_base}<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{urls['css']}"><script type="application/ld+json">{json_script(structured)}</script><script src="{urls['data.js']}" defer></script><script src="{urls['render.js']}" defer></script><script src="{urls['main.js']}" defer></script></head>
<body data-page="{pagekind}" data-id="{pageid}" data-root="{prefix}"><a class="skip-link" href="#main">跳至正文</a><div class="topline"><div class="container"><span>AN INDEPENDENT JOURNAL OF BEAUTIFUL THINGS</span><span>VOL. 01 — OCTOBER 2026</span></div></div><header class="site-header" lang="zh-CN"><div class="container header-inner"><a class="logo-link" href="{prefix}index.html">{LOGO}</a><nav id="main-nav" class="main-nav" aria-label="主导航">{nav}<a class="nav-brand {'active' if current in ['brands','brand'] else ''}" href="{prefix}brands.html">品牌图鉴</a><a class="nav-about" href="{prefix}about.html">关于</a></nav><div class="header-actions"><a class="search-link" href="{prefix}search.html" aria-label="搜索品牌、单品与文章">{icon('search')}</a><button class="menu-toggle" type="button" aria-controls="main-nav" aria-expanded="false" aria-label="打开导航菜单">{icon('menu')}</button></div></div><div class="reading-progress" aria-hidden="true"></div></header><main id="main">{content}</main>{footer}<button class="back-top" aria-label="返回顶部" type="button">{icon('up')}</button><noscript><p class="noscript-note">全部文章可直接阅读；搜索、筛选与订阅演示需要启用 JavaScript。</p></noscript></body></html>'''
    if pagekind=='404':
        # Error documents can be served at arbitrary nested URLs. Build resource
        # URLs after the base is set, so the speculative preload scanner cannot
        # request assets against the missing URL before the inline base runs.
        out=out.replace(f'<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">','')
        out=out.replace(f'<link rel="stylesheet" href="{urls["css"]}">','')
        for script in ['data.js','render.js','main.js']:
            out=out.replace(f'<script src="{urls[script]}" defer></script>','')
        loader='''<script>(function(){var root=document.baseURI;function link(rel,path,type){var l=document.createElement('link');l.rel=rel;l.href=new URL(path,root).href;if(type)l.type=type;document.head.appendChild(l)}link('stylesheet','assets/css/main.css');link('icon','assets/img/favicon.svg','image/svg+xml');function scripts(){['data.js','render.js','main.js'].forEach(function(name){var s=document.createElement('script');s.async=false;s.src=new URL('assets/js/'+name,root).href;document.head.appendChild(s)})}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scripts,{once:true});else scripts()})();</script>'''
        out=out.replace('</head>',loader+'</head>')
    (ROOT/path).write_text(out)
    pages.append(path)

def home():
    cats=''.join(f'<a class="hero-pill" href="cat/{c["id"]}.html">{c["nameZh"]}</a>' for c in D['categories'])
    band=''.join(f'<a class="category-tile reveal" href="cat/{c["id"]}.html">{icon(c["id"])}<span class="eyebrow">{c["nameEn"]}</span><h3>{c["nameZh"]}</h3><p>{c["blurb"]}</p><span class="tiny-arrow">↗</span></a>' for c in D['categories'])
    wall=''.join(f'<a href="brand/{b["id"]}.html"><span>{e(b["name"])}</span><small>{b["founded"]} · {b["country"]}</small></a>' for b in D['brands'])
    content=f'''{edit_hero(cats)}
<div class="container home-yearbook">{bag_yearbook.hub(D)}</div>
<div class="container">{style_edit()}</div>
<section class="container section features">{sectionhead('THE EDITOR’S LETTER','本周专题',('全部文章','search.html?type=article'))}<div class="feature-grid">{card(A['mag-02'],big=True)}{card(A['mag-03'])}{card(A['mag-06'])}</div></section>
<section class="category-section"><div class="container">{sectionhead('SIX WAYS TO WANDER','从一份好奇开始')}<div class="category-grid">{band}</div></div></section>
<section class="container section brand-section">{sectionhead('THE HOUSES & THEIR STORIES','品牌图鉴',(f'浏览 {len(B)} 个品牌','brands.html'))}<p class="section-intro">每一个名字背后，都有一间值得走近的工坊。</p><div class="brand-wall" aria-label="品牌横向列表，可横向滚动">{wall}</div><div class="scroll-hint">向右探索更多品牌 <span>⟶</span></div></section>
<section class="container section latest" id="journal">{sectionhead('NOTES ON BEAUTIFUL THINGS','慢读日常',('搜索文章','search.html?type=article'))}<div class="article-grid">{''.join(card(x) for x in D['articles'])}</div></section>
<section class="dictionary-section"><div class="container">{sectionhead('A SMALL DICTIONARY OF ICONS','编辑精选 · 经典词典',('全部单品','search.html?type=item'))}<p class="section-intro">先记住一个细节，再打开一段故事。</p><div class="item-rail">{''.join(card(I[k],'item') for k in ['birkin','alhambra','tank','classic-flap','jodie','no5'])}</div></div></section>
<section class="newsletter-section" id="newsletter"><div class="container newsletter-inner"><div><p class="eyebrow">LET’S KEEP A LITTLE INSPIRATION</p><h2>一封信，每月一封<span class="rose-dot">。</span></h2><p>把值得慢读的故事，留给一个有空的午后。</p></div><form class="newsletter-form"><label class="sr-only" for="newsletter-email">你的邮箱地址</label><div class="newsletter-input"><input id="newsletter-email" name="email" type="email" required placeholder="你的邮箱地址" autocomplete="email" maxlength="254"><button type="submit" aria-label="提交订阅演示">{icon('arrow')}</button></div><p class="newsletter-status" aria-live="polite">本地订阅演示 · 不保存邮箱，不发送邮件</p></form></div></section>'''
    page('index.html','品味 · 工艺 · 传奇',ABOUT,content,'home')

def otherpages():
    letters=''.join(f'<button type="button" data-letter="{x}" aria-pressed="false">{x}</button>' for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    opts=''.join(f'<option value="{c["id"]}">{c["nameZh"]}</option>' for c in D['categories'])
    content=f'''<div class="container">{crumbs([('品牌图鉴',None)],'')}{headsection('AN ATLAS OF THE HOUSES','品牌图鉴','从一间工坊开始，读懂一个名字的来处。',str(len(B)))}<div class="filter-toolbar"><label>按品类 <select id="brand-category"><option value="all">全部品类</option>{opts}</select></label><label class="brand-query-label">查找品牌 <input id="brand-query" type="search" placeholder="品牌中文或外文名" aria-label="查找品牌"></label><span id="brand-count" aria-live="polite">{len(B)} 个品牌</span></div><div class="alphabet" aria-label="品牌首字母筛选"><button type="button" data-letter="all" aria-pressed="true" class="selected">全部</button>{letters}</div><div id="brand-results" class="brand-grid">{''.join(brandcard(b) for b in sorted(D['brands'],key=lambda b:unicodedata.normalize('NFKD',b['name']).casefold()))}</div></div>'''
    page('brands.html','品牌图鉴', f'{len(B)} 个品牌的来处、历史与本站款式，覆盖全部单品及收录的联名品牌。',content,'brands')
    content=f'''<div class="container">{crumbs([('站内搜索',None)],'')}{headsection('FOLLOW YOUR CURIOSITY','寻找一点灵感','一个名字、一种材质，或一份尚未说清的好奇。')}<form id="search-form" class="large-search" role="search"><label class="sr-only" for="search-query">搜索品牌、单品与文章</label><input id="search-query" name="q" type="search" placeholder="试试 Birkin、铂金、珍珠……" autocomplete="off" maxlength="100"><button class="button button-dark" type="submit">搜索 {icon('search')}</button></form><div class="popular-search"><span>从这里开始</span><a href="search.html?q=Birkin">Birkin</a><a href="search.html?q=四叶草">四叶草</a><a href="search.html?q=皮革">皮革</a><a href="search.html?q=礼物">礼物</a></div><div class="filter-toolbar search-filter"><div class="filter-chips" id="search-types"><button data-type="all" type="button" aria-pressed="true" class="selected">全部</button><button data-type="brand" type="button" aria-pressed="false">品牌</button><button data-type="item" type="button" aria-pressed="false">单品</button><button data-type="article" type="button" aria-pressed="false">文章</button></div><label>品类 <select id="search-category"><option value="all">全部</option>{opts}</select></label></div><p id="search-count" class="results-count" aria-live="polite">准备好，开始探索。</p><div id="search-results" class="search-results"></div><nav id="pagination" class="pagination" aria-label="搜索结果分页"></nav></div>'''
    page('search.html','站内搜索','搜索品牌、经典单品与杂志文章，中英文均可检索。',content,'search')
    sources=[]
    for b in D['brands']:
        sources.append((b['name']+' · 品牌与历史',b['source']))
    sources += [('GIA · 珍珠类型','https://www.gia.edu/pearl-description'),('GIA · 珍珠养护','https://www.gia.edu/pearl-care-cleaning'),('Chanel · N°5 创作背景','https://www.chanel.com/us/fragrance/p/125430/n5-eau-de-parfum-spray/'),('Cartier · 经典珠宝设计','https://www.cartier.com/en-us/jewelry/cartier-jewelry/timeless-creations/iconic-designs/'),('Tiffany · 养护服务','https://www.tiffany.com/care-and-repair/')]
    content=f'''<div class="container">{crumbs([('关于本站',None)],'')}<section class="about-opening"><p class="eyebrow">A JOURNAL, AN INVITATION</p>
<h1>好东西的故事，<br>值得慢慢讲<span class="rose-dot">。</span></h1><p>{ABOUT}</p>
<span class="about-mark">muse / a source of inspiration</span></section>
<div class="about-columns"><div class="about-statement"><span class="eyebrow">OUR POINT OF VIEW</span><h2>先了解，<br>再慢慢喜欢。</h2>
</div><article class="prose"><h2>为什么做这本小图鉴</h2>
<p>让我们好奇的，是一条缝线为什么这样走，一只手袋为什么长成这个轮廓，一枚小小的戒指又怎样装下一段时代的想法。价格与热度之外，材料、工艺和人的生活，也值得有一页自己的位置。</p>
<p>这里借鉴生活美学杂志的阅读节奏，以原创文字、实物款式图与概念插画，整理品牌、作品与日常知识。你可以从一个熟悉名字开始，也可以只是因为喜欢一条弧线，翻开下一页。</p>
<h2>我们怎样整理内容</h2>
<p>品牌历史尽量依据官方档案、品牌故事与公开年表；材料知识参考专业机构资料，并在文章后提供阅读入口。历史表述存在差异时保留必要说明，不把设计辨识线索当作真伪鉴定。</p>
<p>The Style Edit 以美元（USD）列出图中具体型号、尺寸与材质的美国零售参考价，逐款注明核对日期与官方来源，未含税费。价格与供应可能变化；经典词条未核实具体美元价格时会直接说明。所有价格仅供参考，请以品牌专柜/官方渠道为准。</p>
<h2>按年份读懂包袋与珠宝</h2>
<p><a href="bags-by-year.html">The Bag Yearbook · 2022–2026</a> 每年收录四款热门精选和两款限量或限定设计。热门依据保留原始季度或报道时期，具体款式附当年来源；限定类型和实际发售年份分别标注。价格使用美元，并说明是当前美国参考价、有出处的历史报价或未公开价格。2026 年收录截止日分别显示在各年度栏目中。</p>
<p>同样的年份规则也用于 <a href="necklaces-by-year.html">The Necklace Yearbook · 项链</a> 与 <a href="jewelry-by-year.html">The Jewelry Yearbook · 首饰</a>，两个栏目各收录 30 条年度记录。首饰页以戒指、手链和耳饰为主，项链单独浏览；当年的热门依据、实际限定发售年份、图中材质和美元价格口径均在详情页注明。</p>
<h2>关于图片与权利</h2>
<p>The Style Edit 的实物照片来自各品牌公开商品页，逐款标注品牌署名、商品链接与原图来源；版权归相应权利人，公开访问不代表图片获得开放许可。原创概念插画保留在经典词条和杂志文章中，均明确标注，不能用于鉴定。本站为独立的非商业内容项目，与所介绍品牌不存在授权或合作关系。</p>
<h2>让阅读保持轻松</h2>
<p>这里可以搜索、筛选和慢慢阅读。订阅区域是本地交互演示，不保存邮箱，也不真实发送邮件。离线时正文、插画与全部站内功能仍可使用；资料外链需要联网。</p>
<blockquote>我们相信，了解一只包背后的工时与一间工坊的历史，会让拥有或仰望都变得更有滋味。</blockquote></article></div><section id="sources" class="sources-section">{sectionhead('READING & REFERENCES','继续阅读 · 资料来源')}<p class="section-intro">资料核验日期见对应品牌与单品页。外部页面由相应品牌或机构维护；编辑建议与原始历史资料分开理解。</p>
<div class="source-grid">{''.join(f'<a href="{e(url)}" target="_blank" rel="noopener">{e(label)} <span>↗</span></a>' for label,url in sources)}</div><h2 class="photo-source-heading">The Style Edit · 商品与图片来源</h2>
<div class="source-grid">{''.join(f'<a href="{e(x["source"])}" target="_blank" rel="noopener">{e(B[x["brand"]]["name"]+" · "+x["name"])} <span>↗</span></a>' for x in D["items"] if x.get("styleEdit"))}</div></section>
</div>'''
    page('about.html','关于 MuseLux','了解 MuseLux 的内容标准、图片来源与非商业定位。',content,'about')
    content='''<section class="not-found container"><p class="eyebrow">A LITTLE DETOUR · 404</p><svg viewBox="0 0 300 210" width="300" height="210" role="img" aria-label="一只忘记带上故事的空手袋"><path d="M75 78h150l16 109H59L75 78Z" fill="#eee3d8" stroke="#a58b74" stroke-width="1.2"/><path d="M112 78V58a38 38 0 0 1 76 0v20" stroke="#a58b74" fill="none" stroke-width="2"/><path d="M90 103h120M150 103v31" stroke="#a58b74" fill="none"/><rect x="139" y="125" width="22" height="13" fill="#b08d57"/><path d="M238 33l8-13m-1 32 17-4M50 55 38 45" stroke="#c98a8e" stroke-width="1.5"/></svg><h1>这一页，暂时出门了。</h1><p>像一只找不到的梦中情包，<br>或许换个方向，就会遇见新的心动。</p><a class="button button-dark" href="index.html">回到首页 <span>⟶</span></a><a class="text-link" href="search.html">或者，找一点新灵感 ↗</a></section>'''
    page('404.html','这一页，暂时出门了','页面未找到，回到 MuseLux 继续探索。',content,'404')

def brandpage(b):
    catalog=[ALL_ITEMS[k] for k in b['itemIds']]
    counts=[(sum(bool(x.get('styleEdit')) for x in catalog),'款 The Style Edit 实物款式'),
            (sum(bool(x.get('annualEdit')) for x in catalog),'条年度精选'),
            (sum(not x.get('styleEdit') and not x.get('annualEdit') for x in catalog),'个经典设计词条')]
    catalog_note='、'.join(f'{number} {label}' for number,label in counts if number)
    related=[a for a in D['articles'] if a['category'] in b['categories']][:3]
    groups=[]
    for c in D['categories']:
        items=[x for x in catalog if x['category']==c['id']]
        if not items:continue
        items.sort(key=lambda x:(bool(x.get('image')),x.get('year',0)),reverse=True)
        groups.append(f'''<section class="brand-catalog-group" id="catalog-{c['id']}">
<div class="brand-catalog-heading"><h3>{c['nameZh']} <span>{len(items):02}</span></h3>
<a class="text-link" href="../cat/{c['id']}.html">探索{c['nameZh']}栏目 ↗</a></div>
<div class="product-grid">{''.join(card(x,'item','../') for x in items)}</div></section>''')
    categories=''.join(f'<a href="#catalog-{c["id"]}">{c["nameZh"]} ↗</a>' for c in D['categories'] if any(x['category']==c['id'] for x in catalog))
    partner=b.get('role')=='collaborator'
    main_names=list(dict.fromkeys(B[x['brand']]['name'] for x in catalog if x['brand']!=b['id']))
    role_note=f'<p class="brand-role-note">联名品牌 · 本站收录与 {e("、".join(main_names))} 合作的款式，单品页分别链接参与品牌。</p>' if partner else ''
    history_note=f'<p class="brand-history-note">{e(b["historyNote"])}</p>' if b.get('historyNote') else ''
    sources=b.get('sources') or [{'label':b['name']+' · 官方品牌与历史','url':b['source']}]
    source_links=''.join(f'<a class="source-link" href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])} ↗</a>' for s in sources)
    timeline=[]
    for t in b['timeline']:
        citation=f' <a href="{e(t["source"])}" target="_blank" rel="noopener" aria-label="{t["year"]} 年资料来源">↗</a>' if t.get('source') else ''
        timeline.append(f'<li><span>{t["year"]}</span><p>{e(t["event"])}{citation}</p></li>')
    content=f'''<div class="container">{crumbs([('品牌图鉴','../brands.html'),(b['name'],None)],'../')}
<section class="brand-opening"><div><p class="eyebrow">{'COLLABORATION PARTNER' if partner else 'THE HOUSE'} / {e(b['country'])} / EST. {b['founded']}</p>
<h1>{e(b['name'])}</h1><p class="brand-subtitle">{e(b['nameZh'])} <span>—</span> {e(b['tagline'])}</p></div>
<span class="brand-year">{b['founded']}</span></section>{role_note}
<div class="brand-index-summary"><a href="#catalog">本站收录 <strong>{b['itemCount']}</strong> 项 ↓</a><nav aria-label="本站品牌款式品类">{categories}</nav></div>
<div class="brand-intro"><p>{e(b['intro'])}</p><div class="signature-box"><span class="eyebrow">A LANGUAGE OF ITS OWN</span>
<h2>一眼识得的细节</h2><div>{''.join(f'<span>{e(s)}</span>' for s in b['signatures'])}</div></div></div>
<section class="timeline-section">{sectionhead('A FEW CHAPTERS IN TIME','时间留下的几个节点')}
<ol class="timeline">{''.join(timeline)}</ol>{history_note}<div class="brand-history-sources">{source_links}</div></section>
<section class="section brand-catalog" id="catalog">{sectionhead('IN THE MUSELUX CATALOG','本站收录 · 从款式继续认识它')}
<p class="section-intro">{b['itemCount']} 项收录：{catalog_note}。{'年度卡片保留入选年份和美元价格口径。' if any(x.get('annualEdit') for x in catalog) else ''}</p>{''.join(groups)}</section>
<section class="section">{sectionhead('KEEP READING','从相关品类，继续慢读')}
<div class="article-grid">{''.join(card(a,prefix='../') for a in related)}</div></section></div>'''
    page('brand/'+b['id']+'.html',b['name']+' '+b['nameZh'],b['tagline']+'。阅读品牌历史、设计细节与本站收录款式。',content,'brand',b['id'])


def detailpages():
    for c in D['categories']:
        articles=[a for a in D['articles'] if a['category']==c['id']]
        items=[i for i in D['items'] if i['category']==c['id'] and not i.get('styleEdit')]
        extra='<p class="category-extension">也留一点目光给鞋履与墨镜，让日常造型更完整。生活配件一并收录在下方词典。</p>' if c['id']=='jewelry' else ''
        content=f'''<div class="container">{crumbs([(c['nameZh'],None)],'../')}{headsection(c['nameEn']+' / THE CATEGORY',c['nameZh'],c['note'],str(len(items)+len(articles)).zfill(2))}<div class="category-summary"><span>{len(articles)} 篇慢读文章</span><span>{len(items)} 个经典词条</span><span>一种好奇，无限种入口</span></div>{bag_yearbook.teaser(D,"../",c["id"]) if c["id"] in bag_yearbook.BOOKS else ""}{style_edit("../",c)}{extra}<section class="category-editorials">{sectionhead('STORIES TO BEGIN WITH','从这里读起')}<div class="article-grid">{''.join(card(a,prefix='../') for a in articles)}</div></section><section class="section">{sectionhead('THE ILLUSTRATED ARCHIVE','经典单品词典 · 概念插画')}<div class="article-grid">{''.join(card(i,'item','../') for i in items)}</div></section><section class="related-brand-strip"><h2>继续走近这些品牌</h2>{''.join(f'<a href="../brand/{b["id"]}.html">{e(b["name"])} ↗</a>' for b in D['brands'] if c['id'] in b['categories'])}</section></div>'''
        page('cat/'+c['id']+'.html',c['nameZh']+'图鉴',c['note'],content,'category',c['id'])
    for b in D['brands']:
        brandpage(b)
    for x in D['items']:
        if x.get('styleEdit'):
            productpage(x)
            continue
        b=B[x['brand']];c=C[x['category']]
        itemSource=x.get('source',b['source'])
        specs=[('品牌',b['name']+' · '+b['nameZh']),('诞生',str(x['born'])),('创作背景',x['designer']),('常见尺寸 / 形式',' / '.join(x['sizes'])),('常见材质 / 香调',' / '.join(x['materials']))]
        detailNote={'bags':'看包不只看正面：也看看侧面体积、开口宽度与提手落点。尺寸名称是认识作品的起点，实际容量、触感与重量仍需结合具体款式。','necklace':'佩戴时，链长、吊坠比例与领口会共同改变观感。不同子系列与材质的养护方式各有要求，别只凭系列名想象所有细节。','jewelry':'留意环宽、开合结构与日常动作。不同子系列、戒围与镶嵌会影响佩戴感觉，具体刻印也会因时期和型号而变化。','watches':'参考编号决定具体机芯、材质与规格。阅读时把系列历史和具体型号分开；日常操作、防水与维护请依对应说明。','scarves':'同一图案有不同配色与尺寸，折叠后露出的部分也会改变表情。轻轻检查卷边，清洁与熨烫按具体洗护标签进行。','fragrance':'容量、浓度与演绎版本需要分别确认。香调是帮助描述气味的语言，不代表完整配方；先试闻，再观察与自己日常的相处。'}[x['category']]
        if x.get('subtype')=='lifestyle':
            detailNote='鞋履请留意尺码、脚背、后跟与鞋底；墨镜请留意镜框贴合、镜片说明与鼻托位置。不同适配版本的体验有差异，实际试穿或试戴比单独尺寸数字更具体。'
        content=f'''<div class="container">{crumbs([(c['nameZh'],'../cat/'+c['id']+'.html'),(x['name'],None)],'../')}<section class="item-opening">{product_gallery.render(x,GALLERIES)}<div class="item-heading"><a class="eyebrow rose-text" href="../brand/{b['id']}.html">{e(b['name'])} ↗</a><h1>{e(x['name'])}</h1><p class="item-zh">{x['nameZh']}</p><p class="item-definition">{x['oneLiner']}</p><a class="text-link" href="#item-story">读一读它的故事 ↓</a></div></section><div class="item-detail-grid"><article class="prose" id="item-story"><h2>它的故事</h2><p>{e(x['story'])}</p><h2>值得细看的地方</h2><ul>{''.join('<li>'+e(f)+'</li>' for f in x['facts'])}</ul><p>{detailNote}</p><h2>常见尺寸与材质</h2><p>{e('、'.join(x['sizes']))}；{e('、'.join(x['materials']))}。以上为常见形式与历史材质线索，不构成当前供应承诺。尺寸、材质、内衬、刻印与五金配置均以具体型号为准。</p><h2>参考价，读的是量级</h2><p class="price-range">{e(x['priceRange'])}</p><p>不同地区、尺寸、材质、年份和状态可能带来明显差异。本站不提供实时报价、交易或转售收益保证。</p><blockquote><span class="eyebrow">ONE LITTLE DETAIL</span><br>{e(x['facts'][0])}。一个细节，就是继续了解它的入口。</blockquote><p class="source-note">本页介绍设计语言，不提供真伪鉴定。<a href="{e(itemSource)}" target="_blank" rel="noopener">继续阅读品牌公开资料 ↗</a></p></article><aside class="spec-panel"><p class="eyebrow">THE QUICK NOTES</p><h2>单品速写</h2><dl>{''.join(f'<div><dt>{label}</dt><dd>{e(value)}</dd></div>' for label,value in specs)}</dl><a class="text-link" href="../brand/{b['id']}.html">走近 {e(b['name'])} ↗</a></aside></div><section class="section">{sectionhead('THE STORY CONTINUES','把好奇，再延伸一点')}<div class="article-grid">{''.join(card(A[k],prefix='../') for k in x['relatedArticles'][:3])}</div></section></div>'''
        page('item/'+x['id']+'.html',x['name']+' '+x['nameZh'],x['oneLiner']+'了解来处、辨识细节、常见尺寸与材质。',content,'item',x['id'])
    for x in D['articles']:
        c=C[x['category']]
        body=x['body']
        headings=re.findall(r'<h2>(.*?)</h2>',body)
        n=[0]
        def heading(m):
            n[0]+=1
            return f'<h2 id="chapter-{n[0]}">{m[1]}</h2>'
        body=re.sub(r'<h2>(.*?)</h2>',heading,body)
        related=[a for a in D['articles'] if a['id']!=x['id'] and a['category']==x['category']]
        related=(related+[a for a in D['articles'] if a['id']!=x['id'] and a not in related])[:3]
        prev=D['articles'][(D['articles'].index(x)-1)%len(D['articles'])]
        nxt=D['articles'][(D['articles'].index(x)+1)%len(D['articles'])]
        content=f'''<div class="container">{crumbs([(c['nameZh'],'../cat/'+c['id']+'.html'),('慢读文章',None)],'../')}<header class="article-heading"><a class="tag" href="../cat/{c['id']}.html">{c['nameZh']}</a><p class="eyebrow">THE MUSELUX JOURNAL / VOL. 01</p><h1>{e(x['title'])}</h1><p>{e(x['excerpt'])}</p><div class="article-byline"><span class="author-monogram">m.</span><span>MuseLux 编辑部</span><time datetime="{x['date']}">{article_date(x)}</time><span>约 {x['readMins']} 分钟</span></div></header><figure class="article-cover"><img src="../{x['cover']}" width="1200" height="800" alt="{e(x.get('coverAlt') or x['title'].split('｜')[0]+'的原创专题插画')}"><figcaption>插画 / MUSELUX · 图像表达设计概念，不代表产品实物。</figcaption></figure><div class="reading-layout"><aside class="toc"><span class="eyebrow">IN THIS STORY</span><h2>这篇慢慢读</h2><nav aria-label="文章目录">{''.join(f'<a href="#chapter-{i+1}"><span>{i+1:02}</span>{e(h)}</a>' for i,h in enumerate(headings))}</nav><a class="toc-category" href="../cat/{c['id']}.html">探索更多{c['nameZh']}故事 ↗</a></aside><article class="prose article-body">{body}<div class="article-sources"><p class="eyebrow">READING NOTES</p><h2>资料与延伸阅读</h2><p>历史与材料资料见以下官方公开页面；搭配与选择建议为本站编辑整理。</p>{''.join(f'<a href="{e(url)}" target="_blank" rel="noopener">{e(__import__("urllib.parse",fromlist=["urlsplit"]).urlsplit(url).netloc)} · 延伸阅读 ↗</a>' for url in x['sources'])}<p>涉及价格时，仅供参考，请以品牌专柜/官方渠道为准。</p></div><nav class="article-pagination" aria-label="前后文章"><a href="{prev['id']}.html"><span>← 上一篇</span>{e(prev['title'].split('｜')[0])}</a><a href="{nxt['id']}.html"><span>下一篇 →</span>{e(nxt['title'].split('｜')[0])}</a></nav></article></div><section class="section">{sectionhead('ONE MORE BEAUTIFUL THING','还想慢慢读')}<div class="article-grid">{''.join(card(a,prefix='../') for a in related)}</div></section></div>'''
        page('mag/'+x['id']+'.html',x['title'],x['excerpt'],content,'article',x['id'],x)

def data_script():
    # Long stories and research records already live in static HTML. Only ship
    # fields used by browser filtering/search, keeping mobile memory use small.
    fields={'brands':('id','name','nameZh','country','founded','categories','tagline','itemCount','role','aliases'),'items':('id','brand','category','name','nameZh','oneLiner','reference','color','materials','styleEdit','priceUSD','priceStatus','image','brandNames','collaboratorBrands'),'articles':('id','category','title','excerpt','cover')}
    runtime={'categories':D['categories']}
    for key,keys in fields.items():
        runtime[key]=[{k:x[k] for k in keys if k in x} for x in D[key]]
    annual_fields=('id','brand','brandName','category','name','nameZh','oneLiner','reference','color','materials','annualEdit','year','selection','editionLabelEn','priceUSD','priceLabelEn','image','brandNames','collaboratorBrands')
    for x in bag_yearbook.entries(D):
        row={k:x[k] for k in annual_fields if k in x}
        row['yearbookTitle']=bag_yearbook.BOOKS[x['category']]['title']
        runtime['items'].append(row)
    raw=json.dumps(runtime,ensure_ascii=False,separators=(',',':')).encode()
    packed=base64.b64encode(gzip.compress(raw,compresslevel=9,mtime=0)).decode()
    # DecompressionStream is available in the target browsers. No fetch, imports,
    # server or local-file CORS access is used. Pages are fully pre-rendered too.
    script='''/* Canonical editable data: tools/content.json. Rebuild: python3 tools/generate.py. */
window.MUSELUX_READY=(async function(){var b=atob("'''+packed+'''"),a=Uint8Array.from(b,function(c){return c.charCodeAt(0)}),s=new Blob([a]).stream().pipeThrough(new DecompressionStream("gzip"));window.MUSELUX_DATA=JSON.parse(await new Response(s).text());return window.MUSELUX_DATA})();
'''
    (ROOT/'assets/js/data.js').write_text(script)

def retire_pages(previous,current,root=ROOT):
    retired=[]
    for name in set(previous)-set(current):
        relative=Path(name)
        target=(root/relative).resolve()
        if (relative.is_absolute() or not re.fullmatch(r'(?:brand/|cat/|item/|mag/)?[a-z0-9][a-z0-9-]*\.html',name)
                or not target.is_relative_to(root.resolve())):
            raise ValueError('Unsafe generated page path: '+str(name))
        retired.append(root/relative)
    for target in retired:
        if target.is_file():target.unlink()


if __name__=='__main__':
    manifest=ROOT/'reports/page-manifest.json'
    previous=json.loads(manifest.read_text()) if manifest.exists() else []
    data_script();home();otherpages();detailpages()
    for category in bag_yearbook.BOOKS:bag_yearbook.render(D,page,B,category)
    retire_pages(previous,pages)
    if SITE_URL:
        sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+e(SITE_URL+('' if p=='index.html' else p))+'</loc></url>' for p in pages if p not in ['404.html','search.html'])+'</urlset>'
        (ROOT/'sitemap.xml').write_text(sitemap+'\n')
    (ROOT/'reports/page-manifest.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n')
    print('Generated',len(pages),'pages; data.js', (ROOT/'assets/js/data.js').stat().st_size,'bytes')
