"""Content, local-link, asset and delivery contract checks; no third-party deps."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,struct,html,xml.etree.ElementTree as ET
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'tools/content.json').read_text())
issues=[]
def check(condition,message):
    if not condition: issues.append(message)
def cjk(s):return len(re.findall(r'[\u4e00-\u9fff]',re.sub(r'<[^>]*>','',s)))
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
        super().__init__();self.refs=[];self.ids=set();self.h1=0;self.titles=0;self.meta={};self.footer=0;self.images=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
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

pages={}
for f in sorted(ROOT.rglob('*.html')):
    doc=Document();source=f.read_text();doc.feed(source);pages[f.resolve()]=doc
    check(doc.h1==1,f'{f.relative_to(ROOT)}: expected one h1, got {doc.h1}')
    check(doc.titles==1,f'{f.relative_to(ROOT)}: expected one title')
    check(doc.footer==1,f'{f.relative_to(ROOT)}: missing footer')
    check('所有品牌名称与产品名称的权利归其权利人所有' in source,f'{f}: missing disclaimer')
    check(0<len(doc.meta.get('description',''))<=110,f'{f}: invalid meta description')
    for k in ('og:title','og:description','og:type'):check(k in doc.meta,f'{f}: missing {k}')
    check('application/ld+json' in source,f'{f}: missing structured data')
    check('lorem ipsum' not in source.lower(),f'{f}: placeholder text')
    check('<script type="module"' not in source,f'{f}: module dependency')
    for ref in doc.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        check(bool(ref) and ref!='#',f'{f}: empty link')
        target=(f.parent/unquote(u.path)).resolve() if u.path else f.resolve()
        check(target.exists(),f'{f.relative_to(ROOT)}: missing {ref}')
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
    check(len(b['classicItems'])>=1,b['id']+': no classic item')
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
        check('US$'+f'{x["priceUSD"]:,.0f}' in source,x['id']+': USD amount absent from detail page')
        check('Design notes' in source and 'Three details to notice' in source,x['id']+': English description absent')
        check(html.escape(x['imageCredit']) in source,x['id']+': image credit absent')
        check('<html lang="en">' in source,x['id']+': product page language missing')
style_products=[x for x in D['items'] if x.get('styleEdit')]
check(Counter(x['category'] for x in style_products)==Counter({c['id']:4 for c in D['categories']}),'Expected four photographed products in every category')
for c in D['categories']:
    source=(ROOT/'cat'/f'{c["id"]}.html').read_text()
    check(source.count('class="item-card product-card reveal"')==4,c['id']+': expected four photographed cards')
annual_years=D.get('bagYears',[])
annual_entries=[x for year in annual_years for x in year['entries']]
if annual_years:
    check(sorted(y['year'] for y in annual_years)==list(range(2022,2027)),'Yearbook must contain 2022–2026 exactly once')
    check(len({x['id'] for x in annual_entries})==30,'Expected thirty unique annual selection IDs')
    check(not {x['id'] for x in annual_entries}&{x['id'] for x in D['items']},'Annual ID collision with core items')
    for year in annual_years:
        check(Counter(x['selection'] for x in year['entries'])=={'hot':4,'limited':2},str(year['year'])+': expected four hot + two editions')
        check(bool(year.get('sources')),str(year['year'])+': year sources absent')
        if year['year']==2026:check(year.get('yearToDate') and year.get('cutoff')=='2026-10-19','2026 year-to-date scope absent')
        for x in year['entries']:
            for field in ('brandName','name','reference','sizes','materials','priceBasis','priceAsOf','priceLabelEn','source','imageSource','imageCredit','imageRightsNote','selectionReasonEn','selectionSources','availabilityEn'):
                check(bool(x.get(field)),x['id']+': annual field absent: '+field)
            check(x.get('priceCurrency')=='USD',x['id']+': annual currency is not USD')
            check(x['priceBasis'] in ('current-retail','release-retail','reported-retail','auction-result','unlisted'),x['id']+': unknown price basis')
            check(x['priceUSD'] is None or isinstance(x['priceUSD'],(int,float)) and x['priceUSD']>0,x['id']+': invalid annual USD value')
            if x['priceUSD'] is not None:check(bool(x.get('priceSource')),x['id']+': numeric price lacks a source')
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
                if x['priceUSD'] is not None:
                    amount=x['priceUSD'];label='US$'+(f'{amount:,.0f}' if float(amount).is_integer() else f'{amount:,.2f}')
                    check(label in source,x['id']+': annual numeric price absent')
                else:check('Not publicly listed' in source,x['id']+': unlisted price needs an explicit label')
            urls=[x['source'],x['imageSource']]+[s['url'] for s in x['selectionSources']]
            urls += [u for u in (x.get('priceSource'),x.get('editionSource')) if u]
            check(all(urlsplit(u).scheme=='https' for u in urls),x['id']+': source URL must use HTTPS')
    target=ROOT/'bags-by-year.html'
    check(target.is_file(),'Yearbook index absent')
    if target.is_file():
        source=target.read_text()
        check(source.count('class="item-card product-card year-card reveal"')==30,'Yearbook index must include thirty cards')
        for year in range(2022,2027):check(f'id="year-{year}"' in source,'Missing year panel: '+str(year))
for f in pages:
    check(not re.search(r'人民币|[￥¥]|\d[\d,，.]*\s*元',f.read_text()),str(f.relative_to(ROOT))+': legacy RMB price remains')
for a in D['articles']:
    article_counts[a['id']]=cjk(a['body'])
    check(article_counts[a['id']]>=800,a['id']+': less than 800 Chinese characters')
    check(a['body'].count('<h2>')>=3,a['id']+': insufficient sections')
    check(bool(a['sources']),a['id']+': no reading sources')
for svg in (ROOT/'assets/img').glob('*.svg'):
    try:ET.parse(svg)
    except Exception as ex:issues.append(str(svg)+': '+str(ex))
jsbytes=sum(f.stat().st_size for f in (ROOT/'assets/js').glob('*.js'))
check(jsbytes<=80*1024,'JavaScript exceeds 80 KiB')
for f in (ROOT/'assets/js').glob('*.js'):
    source=f.read_text()
    check(not re.search(r'\bfetch\s*\(',source),f.name+': runtime fetch dependency')
    check(not re.search(r'\balert\s*\(',source),f.name+': alert dialog')
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
summary=dict(passed=not issues,pages=len(pages),brands=len(D['brands']),items=len(D['items']),annualBagEntries=len(annual_entries),annualSelectionCounts={str(y['year']):dict(Counter(x['selection'] for x in y['entries'])) for y in annual_years},annualEditionTypes=dict(Counter(x['editionType'] for x in annual_entries if x['selection']=='limited')),annualPriceBasis=dict(Counter(x['priceBasis'] for x in annual_entries)),annualSnapshotReferences=sum('snapshot' in x['priceLabelEn'].lower() for x in annual_entries),searchableItemPages=len(D['items'])+len(annual_entries),articles=len(D['articles']),categories=len(D['categories']),photographedProducts=len(style_products)+len(annual_entries),productsPerCategory=dict(Counter(x['category'] for x in style_products)),currency='USD',coreSnapshotPrices=sum(x['priceStatus']=='official-snapshot' for x in style_products),unlistedAnnualPrices=sum(x['priceUSD'] is None for x in annual_entries),svgAssets=len(list((ROOT/'assets/img').glob('*.svg'))),runtimeJavaScriptBytes=jsbytes,articleChineseCharacters=article_counts,issues=issues)
(ROOT/'reports/static-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
raise SystemExit(bool(issues))
