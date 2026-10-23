"""Content, local-link, asset and delivery contract checks; no third-party deps."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,struct,html,xml.etree.ElementTree as ET,base64,gzip,hashlib,math
from collections import Counter
from datetime import date
from bag_yearbook import BOOKS,price_text,date_label
from brand_catalog import enrich, brand_ids

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'tools/content.json').read_text())
CATALOG=enrich(D)
BRANDS={b['id']:b for b in D['brands']}
PRODUCTS={x['id']:x for x in CATALOG}
issues=[]
def check(condition,message):
    if not condition: issues.append(message)
def cjk(s):return len(re.findall(r'[\u4e00-\u9fff]',re.sub(r'<[^>]*>','',s)))
def iso_date(value,label):
    try:return date.fromisoformat(value)
    except (ValueError,TypeError):
        issues.append(label+': invalid ISO date')
        return None
def image_size(path):
    data=path.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        check(path.suffix.lower()=='.png',str(path)+': incorrect PNG extension')
        return struct.unpack('>II',data[16:24])
    if data[:4]==b'RIFF' and data[8:12]==b'WEBP':
        check(path.suffix.lower()=='.webp',str(path)+': incorrect WebP extension')
        if data[12:16]==b'VP8 ':return tuple(n&0x3fff for n in struct.unpack('<HH',data[26:30]))
        if data[12:16]==b'VP8X':return tuple(int.from_bytes(data[i:i+3],'little')+1 for i in (24,27))
        if data[12:16]==b'VP8L':
            bits=int.from_bytes(data[21:25],'little');return ((bits&0x3fff)+1,((bits>>14)&0x3fff)+1)
        return None
    if data[:2]!=b'\xff\xd8':return None
    check(path.suffix.lower() in ('.jpg','.jpeg'),str(path)+': incorrect JPEG extension')
    offset=2
    while offset+4<len(data):
        if data[offset]!=255:return None
        marker=data[offset+1];offset+=2
        while marker==255:marker=data[offset];offset+=1
        if marker in (0xD8,0xD9):continue
        length=int.from_bytes(data[offset:offset+2],'big')
        if marker in (0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF):
            height,width=struct.unpack('>HH',data[offset+3:offset+7]);return width,height
        offset+=length
    return None
class Document(HTMLParser):
    def __init__(self):
        super().__init__();self.refs=[];self.ids=set();self.h1=0;self.titles=0;self.meta={};self.footer=0;self.images=0;self.jsonld=[];self.json_buffer=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('type')=='application/ld+json':self.json_buffer=''
        if a.get('id'):self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='title':self.titles+=1
        if tag=='footer':self.footer+=1
        if tag=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
        if tag=='img':
            self.images+=1
            check(bool(a.get('alt')),'Missing image alt: '+a.get('src',''))
            check('width'in a and 'height'in a,'Missing intrinsic image dimensions: '+a.get('src',''))
        for attr in ('href','src'):
            if a.get(attr) is not None:self.refs.append(a[attr])
        if a.get('target')=='_blank':check('noopener' in a.get('rel',''),'External link missing noopener')
    def handle_data(self,data):
        if self.json_buffer is not None:self.json_buffer+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.json_buffer is not None:
            try:self.jsonld.append(json.loads(self.json_buffer))
            except ValueError:issues.append('Invalid JSON-LD script')
            self.json_buffer=None

pages={}
for f in sorted(ROOT.rglob('*.html')):
    doc=Document();source=f.read_text();doc.feed(source);pages[f.resolve()]=doc
    check(doc.h1==1,f'{f.relative_to(ROOT)}: expected one h1, got {doc.h1}')
    check(doc.titles==1,f'{f.relative_to(ROOT)}: expected one title')
    check(doc.footer==1,f'{f.relative_to(ROOT)}: missing footer')
    check('所有品牌名称与产品名称的权利归其权利人所有' in source,f'{f}: missing disclaimer')
    check(0<len(doc.meta.get('description',''))<=110,f'{f}: invalid meta description')
    for k in ('og:title','og:description','og:type'):check(k in doc.meta,f'{f}: missing {k}')
    check(len(doc.jsonld)==1 and doc.jsonld[0].get('@context')=='https://schema.org',f'{f}: invalid structured data')
    check('lorem ipsum' not in source.lower(),f'{f}: placeholder text')
    check('<script type="module"' not in source,f'{f}: module dependency')
    for ref in doc.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        check(bool(ref) and ref!='#',f'{f}: empty link')
        target=(f.parent/unquote(u.path)).resolve() if u.path else f.resolve()
        check(target.exists(),f'{f.relative_to(ROOT)}: missing {ref}')
        relative=target.relative_to(ROOT).as_posix() if target.is_relative_to(ROOT) else ''
        if relative in ('assets/css/main.css','assets/js/data.js','assets/js/render.js','assets/js/main.js') and target.is_file():
            check(u.query=='v='+hashlib.sha256(target.read_bytes()).hexdigest()[:12],f'{f}: stale asset digest for '+relative)
manifest=json.loads((ROOT/'reports/page-manifest.json').read_text())
check(len(manifest)==len(set(manifest)),'Duplicate manifest page')
check({str(f.relative_to(ROOT)) for f in pages}==set(manifest),'Generated page manifest differs from delivered HTML (missing or retired page)')
for f,doc in pages.items():
    for ref in doc.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc or not u.fragment:continue
        target=(f.parent/unquote(u.path)).resolve() if u.path else f
        if target in pages:check(u.fragment in pages[target].ids,f'{f.relative_to(ROOT)}: missing anchor {ref}')

check(len(D['brands'])>=8,'Too few brands')
check(len(D['items'])>=12,'Too few items')
check(len(D['articles'])>=12,'Too few articles')
check(len(D['categories'])==6,'Expected six categories')
article_counts={}
for b in D['brands']:
    check(150<=cjk(b['intro'])<=200,b['id']+': intro outside 150–200 CJK characters')
    check(len(b['timeline'])>=6,b['id']+': fewer than six timeline nodes')
    check(b['itemCount']>=1,b['id']+': no linked catalog item')
    check(len(b['itemIds'])==len(set(b['itemIds'])),b['id']+': duplicate catalog association')
    for product_id in b['classicItems']:
        check(product_id in PRODUCTS and PRODUCTS[product_id]['brand']==b['id'],b['id']+': incorrect classic association '+product_id)
    target=(ROOT/'brand'/f'{b["id"]}.html').resolve()
    doc=pages.get(target)
    if doc:
        linked={Path(urlsplit(ref).path).stem for ref in doc.refs if urlsplit(ref).path.startswith('../item/')}
        check(linked==set(b['itemIds']),b['id']+': brand page omits or misattributes catalog products')
        source=target.read_text()
        check(f'本站收录 <strong>{b["itemCount"]}</strong> 项' in source,b['id']+': wrong catalog count')
        for category in {PRODUCTS[k]['category'] for k in b['itemIds']}:
            check(category in b['categories'],b['id']+': represented category absent')
            check('catalog-'+category in doc.ids,b['id']+': category catalog section absent')
        if b.get('role')=='collaborator':check('联名品牌' in source,b['id']+': collaboration role not labelled')
    if b.get('sources'):
        for t in b['timeline']:
            check(urlsplit(t.get('source','')).scheme=='https',b['id']+': sourced history node missing citation')
        check(all(urlsplit(s['url']).scheme=='https' for s in b['sources']),b['id']+': invalid heritage source URL')
for x in CATALOG:
    target=(ROOT/'item'/f'{x["id"]}.html').resolve()
    doc=pages.get(target)
    if doc:
        for brand_id in brand_ids(x):
            check('../brand/'+brand_id+'.html' in doc.refs,x['id']+': no internal link to '+brand_id)
    check(len(brand_ids(x))==1+len(x.get('collaboratorBrands',[])),x['id']+': duplicate brand partner')
for root_page in ('index.html','brands.html'):
    doc=pages.get((ROOT/root_page).resolve())
    if doc:
        indexed={Path(urlsplit(ref).path).stem for ref in doc.refs if urlsplit(ref).path.startswith('brand/')}
        check(indexed==set(BRANDS),root_page+': incomplete brand index')
for x in D['items']:
    for field in ('brand','category','name','nameZh','born','designer','sizes','materials','priceRange','oneLiner','facts','story'):
        check(bool(x.get(field)),x['id']+': missing '+field)
    check('仅供参考' in x['priceRange'] and '官方渠道为准'in x['priceRange'],x['id']+': price disclaimer missing')
    if x.get('styleEdit'):
        for field in ('reference','source','image','imageSource','imageCredit','imageRightsNote','priceContextEn','priceStatus','introEn','featuresEn','stylingEn'):
            check(bool(x.get(field)),x['id']+': missing '+field)
        check(x.get('priceCurrency')=='USD',x['id']+': expected USD')
        check(isinstance(x.get('priceUSD'),(int,float)) and x['priceUSD']>0,x['id']+': invalid USD amount')
        check(x.get('priceStatus') in ('live','official-snapshot'),x['id']+': invalid price provenance')
        if x.get('priceStatus')=='official-snapshot':check(bool(x.get('sourceSnapshotNote')),x['id']+': snapshot qualification missing')
        check(len(x['introEn'].split())>=70,x['id']+': short English introduction')
        check(len(x['featuresEn'])==3,x['id']+': expected three design details')
        image=ROOT/x['image']
        check(image.is_file(),x['id']+': missing product photograph')
        if image.is_file():check(image_size(image)==(x['imageWidth'],x['imageHeight']),x['id']+': photo type/dimensions mismatch')
        source=(ROOT/'item'/f'{x["id"]}.html').read_text()
        check(price_text(x) in source,x['id']+': USD amount absent from detail page')
        reviewed=iso_date(x.get('checkedAt'),x['id']+' review')
        check(reviewed is not None and (reviewed<=date.today()),x['id']+': future review date')
        if reviewed:check(date_label(x['checkedAt']) in source,x['id']+': review date absent from detail page')
        check('Design notes' in source and 'Three details to notice' in source,x['id']+': English description absent')
        check(html.escape(x['imageCredit']) in source,x['id']+': image credit absent')
        check('<html lang="en">' in source,x['id']+': product page language missing')
style_products=[x for x in D['items'] if x.get('styleEdit')]
check(Counter(x['category'] for x in style_products)==Counter({c['id']:4 for c in D['categories']}),'Expected four photographed products in every category')
for c in D['categories']:
    source=(ROOT/'cat'/f'{c["id"]}.html').read_text()
    check(source.count('class="item-card product-card reveal"')==4,c['id']+': expected four photographed cards')
annual_books={category:D.get(cfg['key'],[]) for category,cfg in BOOKS.items()}
annual_entries=[x for years in annual_books.values() for year in years for x in year['entries']]
check(len({x['id'] for x in annual_entries})==len(annual_entries),'Duplicate annual catalog IDs')
check(not {x['id'] for x in annual_entries}&{x['id'] for x in D['items']},'Annual ID collision with core items')
for category,annual_years in annual_books.items():
    if not annual_years:continue
    book_entries=[x for y in annual_years for x in y['entries']]
    check(sorted(y['year'] for y in annual_years)==list(range(2022,2027)),'Yearbook must contain 2022–2026 exactly once')
    check(len(book_entries)==30,category+': expected thirty annual selections')
    for year in annual_years:
        check(Counter(x['selection'] for x in year['entries'])=={'hot':4,'limited':2},str(year['year'])+': expected four hot + two editions')
        check(bool(year.get('sources')),str(year['year'])+': year sources absent')
        cutoff=iso_date(year.get('cutoff'),'Year-to-date cutoff') if year.get('yearToDate') else (iso_date(year['evidenceCutoff'],'Historical evidence cutoff') if year.get('evidenceCutoff') else None)
        if year['year']==2026:
            check(year.get('yearToDate') and cutoff is not None and cutoff.year==2026 and cutoff<=date.today(),'2026 year-to-date scope absent or invalid')
        for x in year['entries']:
            check(x['year']==year['year'] and x['category']==category,x['id']+': incorrect year/category')
            reviewed=iso_date(x.get('checkedAt'),x['id']+' review')
            check(reviewed is not None and reviewed<=date.today(),x['id']+': future review date')
            evidence_cutoff=min(cutoff,reviewed) if cutoff and reviewed else cutoff or reviewed
            for source in x['selectionSources']:
                stamp=source.get('publishedAt','') or ''
                if re.fullmatch(r'\d{4}-\d{2}-\d{2}',stamp):check(evidence_cutoff is not None and date.fromisoformat(stamp)<=evidence_cutoff,x['id']+': evidence after the stated cutoff')
            for field in ('brandName','name','reference','sizes','materials','priceBasis','priceAsOf','priceLabelEn','source','imageSource','imageCredit','imageRightsNote','selectionReasonEn','selectionSources','stylingEn','availabilityEn'):
                check(bool(x.get(field)),x['id']+': annual field absent: '+field)
            check(x.get('priceCurrency')=='USD',x['id']+': annual currency is not USD')
            check(x['priceBasis'] in ('current-retail','release-retail','reported-retail','auction-result','resale-ask','unlisted'),x['id']+': unknown price basis')
            check(x['priceUSD'] is None or isinstance(x['priceUSD'],(int,float)) and x['priceUSD']>0,x['id']+': invalid annual USD value')
            if x['priceUSD'] is not None:check(bool(x.get('priceSource') and x.get('priceEvidence')),x['id']+': numeric price lacks source evidence')
            if isinstance(x['priceUSD'],(int,float)):check(math.isfinite(x['priceUSD']),x['id']+': non-finite price')
            for stamp in re.findall(r'\d{4}-\d{2}-\d{2}',x.get('priceAsOf','')):
                quoted=iso_date(stamp,x['id']+' price date')
                check(quoted is not None and reviewed is not None and quoted<=reviewed,x['id']+': price date after review')
            if x['selection']=='limited':
                check(x.get('editionType') in ('numbered','limited-edition','seasonal-capsule'),x['id']+': unsupported edition type')
                check(bool(x.get('editionEvidence') and x.get('editionSource')),x['id']+': missing edition proof')
                check(x.get('releaseYear')==year['year'],x['id']+': edition release year differs from its selection year')
            check(len(x['introEn'].split())>=70 and len(x['featuresEn'])==3,x['id']+': annual English notes incomplete')
            image=ROOT/x['image']
            check(image.is_file(),x['id']+': annual photo absent')
            if image.is_file():check(image_size(image)==(x['imageWidth'],x['imageHeight']),x['id']+': annual photo type/dimensions mismatch')
            target=ROOT/'item'/f'{x["id"]}.html'
            check(target.is_file(),x['id']+': annual detail page absent')
            if target.is_file():
                source=target.read_text()
                check(html.escape(x['imageCredit']) in source,x['id']+': annual photo credit absent')
                check('WHY IT BELONGS IN '+str(year['year']) in source,x['id']+': dated selection context absent')
                check(html.escape(x['priceLabelEn']) in source,x['id']+': price basis label absent')
                check('<html lang="en">' in source,x['id']+': annual page language absent')
                if reviewed:check('Source reviewed '+date_label(x['checkedAt']) in source,x['id']+': review date mismatch')
                if x['priceUSD'] is not None:
                    amount=x['priceUSD'];label='US$'+(f'{amount:,.0f}' if float(amount).is_integer() else f'{amount:,.2f}')
                    check(label in source,x['id']+': annual numeric price absent')
                else:check('Not publicly listed' in source,x['id']+': unlisted price needs an explicit label')
            urls=[x['source'],x['imageSource']]+[s['url'] for s in x['selectionSources']]
            urls += [u for u in (x.get('priceSource'),x.get('editionSource')) if u]
            check(all(urlsplit(u).scheme=='https' for u in urls),x['id']+': source URL must use HTTPS')
    target=ROOT/BOOKS[category]['path']
    check(target.is_file(),'Yearbook index absent')
    if target.is_file():
        source=target.read_text()
        check(BOOKS[category]['title'] in source,category+': wrong yearbook title')
        check(source.count('class="item-card product-card year-card reveal"')==30,'Yearbook index must include thirty cards')
        for year in range(2022,2027):check(f'id="year-{year}"' in source,'Missing year panel: '+str(year))
for f in pages:
    check(not re.search(r'人民币|[￥¥]|\d[\d,，.]*\s*元',f.read_text()),str(f.relative_to(ROOT))+': legacy RMB price remains')
check(len({a['cover'] for a in D['articles']})==len(D['articles']),'Every journal article needs a separate cover')
if any(a.get('coverScene') for a in D['articles']):
    check(len({a.get('coverScene') for a in D['articles']})==len(D['articles']),'Repeated editorial scene')
    for a in D['articles']:
        check(bool(a.get('coverAlt')),a['id']+': cover description absent')
        cover=(ROOT/a['cover']).read_text()
        check('data-scene="'+a['coverScene']+'"' in cover,a['id']+': cover scene differs from data')
        check('<image' not in cover and '<script' not in cover,a['id']+': journal art must remain a self-contained vector scene')
for a in D['articles']:
    published=iso_date(a['date'],a['id']+' publication')
    check(published is not None and published<=date.today(),a['id']+': future publication')
    if published:
        marker='<time datetime="'+a['date']+'">'+published.strftime('%Y.%m.%d')+'</time>'
        check(marker in (ROOT/'mag'/f'{a["id"]}.html').read_text(),a['id']+': visible article date mismatch')
    article_counts[a['id']]=cjk(a['body'])
    check(article_counts[a['id']]>=800,a['id']+': less than 800 Chinese characters')
    check(a['body'].count('<h2>')>=3,a['id']+': insufficient sections')
    check(bool(a['sources']),a['id']+': no reading sources')
for svg in (ROOT/'assets/img').rglob('*.svg'):
    try:ET.parse(svg)
    except Exception as ex:issues.append(str(svg)+': '+str(ex))
jsbytes=sum(f.stat().st_size for f in (ROOT/'assets/js').glob('*.js'))
check(jsbytes<=80*1024,'JavaScript exceeds 80 KiB')
for f in (ROOT/'assets/js').glob('*.js'):
    source=f.read_text()
    check(not re.search(r'\bfetch\s*\(',source),f.name+': runtime fetch dependency')
    check(not re.search(r'\balert\s*\(',source),f.name+': alert dialog')
try:
    script=(ROOT/'assets/js/data.js').read_text()
    packed=re.search(r'atob\("([A-Za-z0-9+/=]+)"\)',script).group(1)
    runtime=json.loads(gzip.decompress(base64.b64decode(packed)))
    runtime_items={x['id']:x for x in runtime['items']}
    runtime_brands={b['id']:b for b in runtime['brands']}
    check(len(runtime_items)==len(runtime['items']) and set(runtime_items)==set(PRODUCTS),'Runtime search catalog differs from content')
    check(len(runtime_brands)==len(runtime['brands']) and set(runtime_brands)==set(BRANDS),'Runtime brand index differs from content')
    check({a['id'] for a in runtime['articles']}=={a['id'] for a in D['articles']},'Runtime journal index differs from content')
    for brand_id,b in runtime_brands.items():
        check(b['itemCount']==BRANDS[brand_id]['itemCount'],brand_id+': runtime brand count mismatch')
    for product_id,x in runtime_items.items():
        actual=PRODUCTS[product_id]
        for field in ('brand','category','name','image','priceUSD','brandNames'):
            check(x.get(field)==actual.get(field),product_id+': stale runtime '+field)
except (ValueError,AttributeError,KeyError,TypeError) as error:
    issues.append('Cannot verify offline search data: '+str(error))
css=(ROOT/'assets/css/main.css').read_text()
# Catch malformed edit blocks, while ignoring quoted text and comments.
tokens=re.sub(r'/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','',css,flags=re.S)
stack=[];pairs={')':'(',']':'[','}':'{'}
for token in tokens:
    if token in '([{':stack.append(token)
    elif token in ')]}':
        if not stack or stack.pop()!=pairs[token]:issues.append('CSS has unbalanced delimiters');break
check(not stack,'CSS has unclosed delimiters')
check((ROOT/'README.md').exists(),'Missing README')
check((ROOT/'assets/fonts/Oswald-LICENSE.txt').exists(),'Oswald license missing')
check((ROOT/'assets/fonts/Raleway-LICENSE.txt').exists(),'Raleway license missing')
summary=dict(passed=not issues,pages=len(pages),brands=len(D['brands']),items=len(D['items']),
    primaryBrands=len({x['brand'] for x in CATALOG}),
    collaborationBrands=sum(b.get('role')=='collaborator' for b in D['brands']),
    catalogBrandAssociations=sum(b['itemCount'] for b in D['brands']),
    productsWithBrandPage=len(CATALOG),
    annualBagEntries=sum(len(y['entries']) for y in annual_books['bags']),
    annualEntries=len(annual_entries),
    annualEntriesByCategory={c:sum(len(y['entries']) for y in years) for c,years in annual_books.items()},
    annualSelectionCounts={c:{str(y['year']):dict(Counter(x['selection'] for x in y['entries'])) for y in years} for c,years in annual_books.items()},
    annualEditionTypes=dict(Counter(x['editionType'] for x in annual_entries if x['selection']=='limited')),
    annualPriceBasis=dict(Counter(x['priceBasis'] for x in annual_entries)),
    annualSnapshotReferences=sum('snapshot' in x['priceLabelEn'].lower() for x in annual_entries),
    searchableItemPages=len(D['items'])+len(annual_entries),articles=len(D['articles']),categories=len(D['categories']),
    photographedProducts=len(style_products)+len(annual_entries),productsPerCategory=dict(Counter(x['category'] for x in style_products)),
    currency='USD',coreSnapshotPrices=sum(x['priceStatus']=='official-snapshot' for x in style_products),
    unlistedAnnualPrices=sum(x['priceUSD'] is None for x in annual_entries),
    svgAssets=len(list((ROOT/'assets/img').rglob('*.svg'))),runtimeJavaScriptBytes=jsbytes,articleChineseCharacters=article_counts,issues=issues)
(ROOT/'reports/static-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
raise SystemExit(bool(issues))
