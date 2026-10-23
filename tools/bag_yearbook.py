"""Shared static annual edits. No runtime dependencies or requests."""
from datetime import date
from html import escape
import re
import product_gallery

e=lambda value:escape(str(value),quote=True)
METHOD_SOURCE='https://www.lyst.com/the-lyst-index/'
BOOKS={
    'bags':dict(key='bagYears',path='bags-by-year.html',title='The Bag Yearbook',label='Bags',noun='bags',headline='The bags of their year',opening='Five years of changing silhouettes.',sameYear='ANOTHER SHAPE',zh='包袋'),
    'necklace':dict(key='necklaceYears',path='necklaces-by-year.html',title='The Necklace Yearbook',label='Necklaces',noun='necklaces',headline='A year at the neckline',opening='Five years of pendants, chains and changing proportions.',sameYear='ANOTHER LINE',zh='项链'),
    'jewelry':dict(key='jewelryYears',path='jewelry-by-year.html',title='The Jewelry Yearbook',label='Jewelry',noun='jewelry pieces',headline='Jewelry, in its moment',opening='Five years of rings, bracelets and earrings.',sameYear='ANOTHER DETAIL',zh='首饰'),
}

def entries(data):
    return [x for cfg in BOOKS.values() for year in data.get(cfg['key'],[]) for x in year['entries']]

def book_links(data,prefix='',active=None):
    return '<nav class="yearbook-category-links" aria-label="Yearbook categories">'+''.join(f'<a href="{prefix}{cfg["path"]}"'+(' aria-current="page"' if category==active else '')+f'>{cfg["label"]}</a>' for category,cfg in BOOKS.items() if data.get(cfg['key']))+'</nav>'

def hub(data,prefix=''):
    cards=[]
    for cfg in BOOKS.values():
        years=data.get(cfg['key'],[])
        if not years:continue
        cover=next(x for x in max(years,key=lambda y:y['year'])['entries'] if x['selection']=='hot')
        cards.append(f'''<a class="yearbook-hub-card" href="{prefix}{cfg['path']}"><div class="yearbook-hub-image"><img src="{prefix}{e(cover['image'])}" width="{cover['imageWidth']}" height="{cover['imageHeight']}" loading="lazy" alt="{e(cover['brandName']+' '+cover['name'])}"><span>2022—2026</span></div><div><span class="eyebrow">{cfg['label'].upper()} / 30 SELECTIONS</span><h3>{cfg['title']} <span>↗</span></h3><p>{cfg['opening']}</p></div></a>''')
    if not cards:return ''
    return f'''<section class="yearbook-hub" lang="en"><header><p class="eyebrow rose-text">THE ANNUAL EDITS / 2022—2026</p><h2>Objects of their moment<span class="rose-dot">.</span></h2><p>Four popular picks and two limited or special editions per category, per year. Photographs, design notes and dated USD references.</p></header><div class="yearbook-hub-grid">{''.join(cards)}</div></section>'''

def date_label(value):
    try:return date.fromisoformat(str(value)).strftime('%d %B %Y').lstrip('0')
    except (ValueError,TypeError):return str(value or '')

def price_text(x):
    amount=x.get('priceUSD')
    if amount is None:return 'Not publicly listed'
    return 'US$'+(f'{amount:,.0f}' if float(amount).is_integer() else f'{amount:,.2f}')

def price_heading(x):
    return {'current-retail':'CURRENT U.S. REFERENCE','release-retail':'RELEASE RETAIL · USD','reported-retail':'REPORTED RETAIL · USD','auction-result':'DATED AUCTION RESULT · USD','resale-ask':'DATED RESALE ASK · USD','unlisted':'PRICE REFERENCE'}.get(x['priceBasis'],'USD REFERENCE')

def price_date_label(value):
    text=str(value or '')
    if re.match(r'^\d{4}-\d{2}-\d{2}',text):return date_label(text[:10])
    # Preserve month-level precision and put the separate review date below.
    text=text.split(';')[0].replace('~','approximately ')
    return re.sub(r'(?<=[A-Za-z])(?=20\d\d\b)',' ',text).strip()

def card(x,prefix=''):
    edition=x.get('editionLabelEn') if x['selection']=='limited' else 'Most wanted'
    return f'''<article class="item-card product-card year-card reveal" lang="en">
<a href="{prefix}item/{e(x['id'])}.html"><div class="product-image"><img src="{prefix}{e(x['image'])}" width="{x['imageWidth']}" height="{x['imageHeight']}" loading="lazy" alt="{e(x['brandName']+' '+x['name']+' — '+x['color'])}"><span class="product-index">{x['year']} / {e(edition)}</span></div>
<div class="item-body"><span class="eyebrow">{e(x['brandName'])}</span><h3>{e(x['name'])}</h3><p>{e(x['oneLiner'])}</p><div class="product-card-bottom"><span class="product-price{' price-unlisted' if x.get('priceUSD') is None else ''}">{price_text(x)}</span><span class="product-open">Explore ↗</span></div><span class="product-price-note">{e(x['priceLabelEn'])}</span></div></a></article>'''

def teaser(data,prefix='',category='bags'):
    cfg=BOOKS[category]
    years=data.get(cfg['key'],[])
    if not years:return ''
    latest=max(years,key=lambda y:y['year'])
    cover=next(x for x in latest['entries'] if x['selection']=='hot')
    pills=''.join(f'<a href="{prefix}{cfg["path"]}#year-{year}">{year}{" so far" if year==2026 else ""} ↗</a>' for year in range(2026,2021,-1))
    return f'''<aside class="yearbook-teaser" lang="en"><div class="yearbook-teaser-copy"><p class="eyebrow rose-text">{cfg['title'].upper()} / 2022—2026</p><h2>{cfg['headline']}<span class="rose-dot">.</span></h2><p>{cfg['opening']} Four popular picks and two limited or special editions per year, with photographs, design notes and USD references.</p><nav class="yearbook-shortcuts" aria-label="Browse {cfg['label'].lower()} by year">{pills}</nav><a class="text-link" href="{prefix}{cfg['path']}">Explore all 30 selections ↗</a></div><a class="yearbook-teaser-image" href="{prefix}{cfg['path']}"><img src="{prefix}{e(cover['image'])}" width="{cover['imageWidth']}" height="{cover['imageHeight']}" loading="lazy" alt="{e(cover['brandName']+' '+cover['name'])}"><span>2026 / YEAR TO DATE</span></a></aside>'''

def source_list(sources):
    return ''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])} ↗</a>'+ (f'<span>{e(date_label(s.get("publishedAt")))}</span>' if s.get('publishedAt') else '')+'</li>' for s in sources)

def render(data,page,brands,category='bags'):
    cfg=BOOKS[category]
    years=data.get(cfg['key'],[])
    if not years:return
    tabs=''.join(f'<button type="button" data-year="{y["year"]}" aria-controls="year-{y["year"]}" aria-pressed="false">{y["year"]}{" <small>so far</small>" if y["year"]==2026 else ""}</button>' for y in sorted(years,key=lambda y:y['year'],reverse=True))
    panels=[]
    for year in sorted(years,key=lambda y:y['year'],reverse=True):
        number=year['year']
        hot=[x for x in year['entries'] if x['selection']=='hot']
        editions=[x for x in year['entries'] if x['selection']=='limited']
        cutoff=f'<span class="year-cutoff">YEAR TO DATE · {e(date_label(year["cutoff"]))}</span>' if year.get('yearToDate') else '<span class="year-cutoff">THE ANNUAL EDIT</span>'
        panels.append(f'''<section class="yearbook-panel" data-year-panel="{number}" id="year-{number}" aria-labelledby="year-heading-{number}"><header class="yearbook-year-heading"><div><p class="eyebrow rose-text">{number} / FORM &amp; CULTURE</p><h2 id="year-heading-{number}">{e(year['headlineEn'])}</h2><p>{e(year['introEn'])}</p></div><div class="yearbook-year-number"><span>{number}</span>{cutoff}</div></header><div class="yearbook-group-heading"><h3>Most wanted</h3><span>04 / POPULAR PICKS</span></div><div class="product-grid yearbook-hot-grid">{''.join(card(x) for x in hot)}</div><div class="yearbook-group-heading editions-heading"><div><h3>Limited &amp; special editions</h3><p>Numbered editions, limited releases and collaboration capsules are labelled individually.</p></div><span>02 / THE EDITIONS</span></div><div class="product-grid yearbook-limited-grid">{''.join(card(x) for x in editions)}</div><details class="yearbook-sources"><summary>Sources behind the {number} edit</summary><ul>{source_list(year['sources'])}</ul></details></section>''')
    scope=' '.join(f'The {y["year"]} edit covers evidence available by {date_label(y["cutoff"])}.' for y in years if y.get('yearToDate'))
    method_link=f'<a href="{METHOD_SOURCE}" target="_blank" rel="noopener">Read about The Lyst Index ↗</a>' if category=='bags' else ''
    content=f'''<div class="container yearbook-page" lang="en"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="cat/{category}.html">{cfg['label']}</a><span>/</span><span aria-current="page">{cfg['title']}</span></nav><header class="yearbook-opening"><div><p class="eyebrow rose-text">2022—2026 / THE MUSELUX ARCHIVE</p><h1>{cfg['title']}<span class="rose-dot">.</span></h1><p>{cfg['opening']}<br>Explore four popular {cfg['noun']} and two limited or special editions from each year.</p></div><span class="yearbook-total">30 <small>SELECTIONS / 5 YEARS</small></span></header><details class="yearbook-method"><summary>How the edit is selected</summary><div><p>Each year's four popular picks form an editorial shortlist based on dated demand reports and editorial coverage. Source ranks refer to their stated quarter or period; the edit is not a universal annual sales ranking. A current photograph may show a later colour or material variant of a design family that was popular in the selected year; the pictured reference is identified on its detail page.</p><p>Edition labels distinguish numbered editions, explicit limited releases and seasonal capsules. A capsule label does not imply a fixed production quantity. Prices remain in USD, with current retail references, dated reported prices and any unavailable prices clearly identified. {e(scope)}</p>{method_link}</div></details>{book_links(data,active=category)}<div class="year-tabs" hidden role="group" aria-label="Select a {cfg['label'].lower()} year">{tabs}</div>{''.join(panels)}<p class="yearbook-price-note">USD references are labelled by their price date and basis. Archive prices are not live offers; confirm current availability with the brand or the named source.</p></div>'''
    page(cfg['path'],cfg['title']+' · 2022–2026',f"Explore 2022–2026: four popular {cfg['noun']} and two limited or special editions per year, with photographs and USD references.",content,'yearbook',category)
    for year in years:
        for entry in year['entries']:render_entry(entry,year,page,brands,category)

def render_entry(x,year,page,brands,category='bags'):
    cfg=BOOKS[category]
    galleries=product_gallery.load()
    number=x['year']
    edition=x['selection']=='limited'
    group=x.get('editionLabelEn') if edition else 'Popular pick'
    brand=brands[x['brand']]
    brand_link=f'<a class="eyebrow rose-text" href="../brand/{brand["id"]}.html">{e(brand["name"])} ↗</a>'
    partners=[brands[brand_id] for brand_id in x.get('collaboratorBrands',[])]
    if partners:
        brand_link+='<p class="product-collaborators">In collaboration with '+', '.join(f'<a href="../brand/{b["id"]}.html">{e(b["name"])} ↗</a>' for b in partners)+'</p>'
    specs=[('Pictured reference',x['reference']),('Colour / finish',x['color']),('Size / format',' · '.join(x['sizes'])),('Materials',' · '.join(x['materials'])),('Yearbook selection',str(number)+(' · year to date' if number==2026 else ''))]
    if edition and x.get('releaseYear'):specs.append(('Edition release year',str(x['releaseYear'])))
    edition_note=f'''<section class="edition-note"><p class="eyebrow">THE EDITION</p><h2>{e(x['editionLabelEn'])}</h2><p>{e(x.get('editionNoteEn',x['editionEvidence']))}</p><a class="source-link" href="{e(x['editionSource'])}" target="_blank" rel="noopener">Edition source ↗</a></section>''' if edition else ''
    price_source=f'<a class="source-link" href="{e(x["priceSource"])}" target="_blank" rel="noopener">Price source ↗</a>' if x.get('priceSource') else ''
    price_caveat=f'<p class="year-price-caveat">{e(x["priceNoteEn"])}</p>' if x.get('priceNoteEn') else ''
    photo_listing=f'<a class="source-link" href="{e(x["imagePageURL"])}" target="_blank" rel="noopener">Photographed example ↗</a>' if x.get('imagePageURL') else ''
    related=[i for i in year['entries'] if i['id']!=x['id']][:4]
    content=f'''<div class="container product-detail yearbook-detail" lang="en"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../{cfg['path']}#year-{number}">{number} {cfg['label']} Yearbook</a><span>/</span><span aria-current="page">{e(group)}</span></nav><section class="product-opening">{product_gallery.render(x,galleries)}<div class="product-heading">{brand_link}<span class="year-entry-label">{number} / {e(group)}</span><h1>{e(x['name'])}</h1><p class="product-subtitle">{e(x['color'])} · Ref. {e(x['reference'])}</p><p class="product-lede">{e(x['oneLiner'])}</p><div class="product-price-box"><span class="eyebrow">{price_heading(x)}</span><p class="product-detail-price{' price-unlisted' if x.get('priceUSD') is None else ''}">{price_text(x)}</p><p>{e(x['priceLabelEn'])}</p><p>Price date: {e(price_date_label(x['priceAsOf']))} · Source reviewed {e(date_label(x.get('checkedAt','2026-10-19')))}</p>{price_caveat}</div><a class="button button-dark official-link" href="{e(x['source'])}" target="_blank" rel="noopener">View the product source ↗</a><p class="official-note">{e(x['availabilityEn'])}</p></div></section><section class="year-selection-note"><span class="eyebrow rose-text">WHY IT BELONGS IN {number}</span><h2>{'An edition of its moment' if edition else 'The year’s attention'}</h2><p>{e(x['selectionReasonEn'])}</p><ul class="year-evidence">{source_list(x['selectionSources'])}</ul></section><div class="product-notes"><article class="prose product-prose"><p class="eyebrow rose-text">FORM / MATERIAL / EVERYDAY</p><h2>Design notes</h2><p>{e(x['introEn'])}</p><h2>Three details to notice</h2><ul>{''.join('<li>'+e(f)+'</li>' for f in x['featuresEn'])}</ul><h2>How to wear it</h2><p>{e(x['stylingEn'])}</p>{edition_note}<a class="text-link" href="../{cfg['path']}#year-{number}">Return to the {number} edit ↗</a></article><aside class="spec-panel product-spec"><p class="eyebrow">THE PARTICULARS</p><h2>At a glance</h2><dl>{''.join(f'<div><dt>{label}</dt><dd>{e(value)}</dd></div>' for label,value in specs)}</dl><p class="product-source-note">The selection year describes the cultural context. The price label identifies the date and basis of the quoted USD amount. Product names and photographs belong to their respective rights holders.</p>{price_source}{photo_listing}<a class="source-link" href="{e(x['imageSource'])}" target="_blank" rel="noopener">Original photograph source ↗</a></aside></div><section class="section"><div class="section-head"><div><p class="eyebrow">THE SAME YEAR, {cfg['sameYear']}</p><h2>More from {number}</h2></div></div><div class="product-grid">{''.join(card(i,'../') for i in related)}</div></section></div>'''
    page('item/'+x['id']+'.html',x['brandName']+' '+x['name']+' · '+str(number),x['oneLiner'],content,'year-entry',x['id'],product=x)
