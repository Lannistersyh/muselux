"""Static, source-led annual bag edits. No runtime dependencies or requests."""
from datetime import date
from html import escape

e=lambda value:escape(str(value),quote=True)
METHOD_SOURCE='https://www.lyst.com/the-lyst-index/'

def date_label(value):
    try:return date.fromisoformat(str(value)).strftime('%d %B %Y').lstrip('0')
    except (ValueError,TypeError):return str(value or '')

def price_text(x):
    amount=x.get('priceUSD')
    if amount is None:return 'Not publicly listed'
    return 'US$'+(f'{amount:,.0f}' if float(amount).is_integer() else f'{amount:,.2f}')

def price_heading(x):
    return {'current-retail':'CURRENT U.S. REFERENCE','release-retail':'RELEASE RETAIL · USD','reported-retail':'REPORTED RETAIL · USD','auction-result':'DATED AUCTION RESULT · USD','unlisted':'PRICE REFERENCE'}.get(x['priceBasis'],'USD REFERENCE')

def card(x,prefix=''):
    edition=x.get('editionLabelEn') if x['selection']=='limited' else 'Most wanted'
    return f'''<article class="item-card product-card year-card reveal" lang="en">
<a href="{prefix}item/{e(x['id'])}.html"><div class="product-image"><img src="{prefix}{e(x['image'])}" width="{x['imageWidth']}" height="{x['imageHeight']}" loading="lazy" alt="{e(x['brandName']+' '+x['name']+' — '+x['color'])}"><span class="product-index">{x['year']} / {e(edition)}</span></div>
<div class="item-body"><span class="eyebrow">{e(x['brandName'])}</span><h3>{e(x['name'])}</h3><p>{e(x['oneLiner'])}</p><div class="product-card-bottom"><span class="product-price{' price-unlisted' if x.get('priceUSD') is None else ''}">{price_text(x)}</span><span class="product-open">Explore ↗</span></div><span class="product-price-note">{e(x['priceLabelEn'])}</span></div></a></article>'''

def teaser(data,prefix=''):
    years=data.get('bagYears',[])
    if not years:return ''
    latest=max(years,key=lambda y:y['year'])
    cover=next(x for x in latest['entries'] if x['selection']=='hot')
    pills=''.join(f'<a href="{prefix}bags-by-year.html#year-{year}">{year}{" so far" if year==2026 else ""} ↗</a>' for year in range(2026,2021,-1))
    return f'''<aside class="yearbook-teaser" lang="en"><div class="yearbook-teaser-copy"><p class="eyebrow rose-text">THE BAG YEARBOOK / 2022—2026</p><h2>The bags of their year<span class="rose-dot">.</span></h2><p>Five years of changing silhouettes. Four popular picks and two limited or special editions per year, with photographs, design notes and USD references.</p><nav class="yearbook-shortcuts" aria-label="Browse bags by year">{pills}</nav><a class="text-link" href="{prefix}bags-by-year.html">Explore all 30 selections ↗</a></div><a class="yearbook-teaser-image" href="{prefix}bags-by-year.html"><img src="{prefix}{e(cover['image'])}" width="{cover['imageWidth']}" height="{cover['imageHeight']}" loading="lazy" alt="{e(cover['brandName']+' '+cover['name'])}"><span>2026 / YEAR TO DATE</span></a></aside>'''

def source_list(sources):
    return ''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])} ↗</a>'+ (f'<span>{e(date_label(s.get("publishedAt")))}</span>' if s.get('publishedAt') else '')+'</li>' for s in sources)

def render(data,page,brands):
    years=data.get('bagYears',[])
    if not years:return
    tabs=''.join(f'<button type="button" data-year="{y["year"]}" aria-controls="year-{y["year"]}" aria-pressed="false">{y["year"]}{" <small>so far</small>" if y["year"]==2026 else ""}</button>' for y in sorted(years,key=lambda y:y['year'],reverse=True))
    panels=[]
    for year in sorted(years,key=lambda y:y['year'],reverse=True):
        number=year['year']
        hot=[x for x in year['entries'] if x['selection']=='hot']
        editions=[x for x in year['entries'] if x['selection']=='limited']
        cutoff=f'<span class="year-cutoff">YEAR TO DATE · {e(date_label(year["cutoff"]))}</span>' if year.get('yearToDate') else '<span class="year-cutoff">THE ANNUAL EDIT</span>'
        panels.append(f'''<section class="yearbook-panel" data-year-panel="{number}" id="year-{number}" aria-labelledby="year-heading-{number}"><header class="yearbook-year-heading"><div><p class="eyebrow rose-text">{number} / FORM &amp; CULTURE</p><h2 id="year-heading-{number}">{e(year['headlineEn'])}</h2><p>{e(year['introEn'])}</p></div><div class="yearbook-year-number"><span>{number}</span>{cutoff}</div></header><div class="yearbook-group-heading"><h3>Most wanted</h3><span>04 / POPULAR PICKS</span></div><div class="product-grid yearbook-hot-grid">{''.join(card(x) for x in hot)}</div><div class="yearbook-group-heading editions-heading"><div><h3>Limited &amp; special editions</h3><p>Numbered editions, limited releases and time-bound capsules are labelled individually.</p></div><span>02 / THE EDITIONS</span></div><div class="product-grid yearbook-limited-grid">{''.join(card(x) for x in editions)}</div><details class="yearbook-sources"><summary>Sources behind the {number} edit</summary><ul>{source_list(year['sources'])}</ul></details></section>''')
    content=f'''<div class="container yearbook-page" lang="en"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="cat/bags.html">Bags</a><span>/</span><span aria-current="page">The Bag Yearbook</span></nav><header class="yearbook-opening"><div><p class="eyebrow rose-text">2022—2026 / THE MUSELUX ARCHIVE</p><h1>The Bag Yearbook<span class="rose-dot">.</span></h1><p>Some shapes capture a moment. Others change what comes next.<br>Explore four popular bags and two limited or special editions from each year.</p></div><span class="yearbook-total">30 <small>SELECTIONS / 5 YEARS</small></span></header><details class="yearbook-method"><summary>How the edit is selected</summary><div><p>Each year's four popular picks form an editorial shortlist based on dated demand reports and fashion coverage. Source ranks refer to their stated quarter or period; the edit is not a universal annual sales ranking. A current photograph may show a later colour or material variant of a family that was popular in the selected year; the pictured reference is identified on its detail page.</p><p>Edition labels distinguish numbered editions, explicit limited releases and seasonal capsules. A capsule label does not imply a fixed production quantity. Prices remain in USD, with current retail references, dated reported prices and any unavailable prices clearly identified. The 2026 edit covers evidence available by 19 October 2026.</p><a href="{METHOD_SOURCE}" target="_blank" rel="noopener">Read about The Lyst Index ↗</a></div></details><div class="year-tabs" hidden role="group" aria-label="Select a bag year">{tabs}</div>{''.join(panels)}<p class="yearbook-price-note">USD references are labelled by their price date and basis. Archive prices are not live offers; confirm current availability with the brand or the named source.</p></div>'''
    page('bags-by-year.html','The Bag Yearbook · 2022–2026','Explore 2022–2026: four popular bags and two limited or special editions per year, with photographs and USD references.',content,'yearbook')
    for year in years:
        for entry in year['entries']:render_entry(entry,year,page,brands)

def render_entry(x,year,page,brands):
    number=x['year']
    edition=x['selection']=='limited'
    group=x.get('editionLabelEn') if edition else 'Popular pick'
    brand=brands.get(x['brand'])
    brand_link=f'<a class="eyebrow rose-text" href="../brand/{brand["id"]}.html">{e(x["brandName"])} ↗</a>' if brand else f'<a class="eyebrow rose-text" href="{e(x["source"])}" target="_blank" rel="noopener">{e(x["brandName"])} ↗</a>'
    specs=[('Pictured reference',x['reference']),('Colour / finish',x['color']),('Size / format',' · '.join(x['sizes'])),('Materials',' · '.join(x['materials'])),('Yearbook selection',str(number)+(' · year to date' if number==2026 else ''))]
    if edition and x.get('releaseYear'):specs.append(('Edition release year',str(x['releaseYear'])))
    edition_note=f'''<section class="edition-note"><p class="eyebrow">THE EDITION</p><h2>{e(x['editionLabelEn'])}</h2><p>{e(x.get('editionNoteEn',x['editionEvidence']))}</p><a class="source-link" href="{e(x['editionSource'])}" target="_blank" rel="noopener">Official edition source ↗</a></section>''' if edition else ''
    price_source=f'<a class="source-link" href="{e(x["priceSource"])}" target="_blank" rel="noopener">Price source ↗</a>' if x.get('priceSource') else ''
    price_caveat=f'<p class="year-price-caveat">{e(x["priceNoteEn"])}</p>' if x.get('priceNoteEn') else ''
    related=[i for i in year['entries'] if i['id']!=x['id']][:4]
    content=f'''<div class="container product-detail yearbook-detail" lang="en"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../bags-by-year.html#year-{number}">{number} Bag Yearbook</a><span>/</span><span aria-current="page">{e(group)}</span></nav><section class="product-opening"><figure class="product-photo"><img src="../{e(x['image'])}" width="{x['imageWidth']}" height="{x['imageHeight']}" alt="{e(x['brandName']+' '+x['name']+' — '+x['color'])}" fetchpriority="high"><figcaption>{e(x['imageCredit'])} · Pictured reference identified below</figcaption></figure><div class="product-heading">{brand_link}<span class="year-entry-label">{number} / {e(group)}</span><h1>{e(x['name'])}</h1><p class="product-subtitle">{e(x['color'])} · Ref. {e(x['reference'])}</p><p class="product-lede">{e(x['oneLiner'])}</p><div class="product-price-box"><span class="eyebrow">{price_heading(x)}</span><p class="product-detail-price{' price-unlisted' if x.get('priceUSD') is None else ''}">{price_text(x)}</p><p>{e(x['priceLabelEn'])}</p><p>Price date: {e(date_label(x['priceAsOf']))} · Source reviewed 19 October 2026</p>{price_caveat}</div><a class="button button-dark official-link" href="{e(x['source'])}" target="_blank" rel="noopener">View the product source ↗</a><p class="official-note">{e(x['availabilityEn'])}</p></div></section><section class="year-selection-note"><span class="eyebrow rose-text">WHY IT BELONGS IN {number}</span><h2>{'An edition of its moment' if edition else 'The year’s attention'}</h2><p>{e(x['selectionReasonEn'])}</p><ul class="year-evidence">{source_list(x['selectionSources'])}</ul></section><div class="product-notes"><article class="prose product-prose"><p class="eyebrow rose-text">FORM / MATERIAL / EVERYDAY</p><h2>Design notes</h2><p>{e(x['introEn'])}</p><h2>Three details to notice</h2><ul>{''.join('<li>'+e(f)+'</li>' for f in x['featuresEn'])}</ul><h2>How to wear it</h2><p>{e(x['stylingEn'])}</p>{edition_note}<a class="text-link" href="../bags-by-year.html#year-{number}">Return to the {number} edit ↗</a></article><aside class="spec-panel product-spec"><p class="eyebrow">THE PARTICULARS</p><h2>At a glance</h2><dl>{''.join(f'<div><dt>{label}</dt><dd>{e(value)}</dd></div>' for label,value in specs)}</dl><p class="product-source-note">The selection year describes the cultural context. The price label identifies the date and basis of the quoted USD amount. Product names and photographs belong to their respective rights holders.</p>{price_source}<a class="source-link" href="{e(x['imageSource'])}" target="_blank" rel="noopener">Original photograph source ↗</a></aside></div><section class="section"><div class="section-head"><div><p class="eyebrow">THE SAME YEAR, ANOTHER SHAPE</p><h2>More from {number}</h2></div></div><div class="product-grid">{''.join(card(i,'../') for i in related)}</div></section></div>'''
    page('item/'+x['id']+'.html',x['brandName']+' '+x['name']+' · '+str(number),x['oneLiner'],content,'bag-entry',x['id'],product=x)
