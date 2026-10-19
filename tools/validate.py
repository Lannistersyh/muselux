"""Content, local-link, asset and delivery contract checks; no third-party deps."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'tools/content.json').read_text())
issues=[]
def check(condition,message):
    if not condition: issues.append(message)
def cjk(s):return len(re.findall(r'[\u4e00-\u9fff]',re.sub(r'<[^>]*>','',s)))
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
check((ROOT/'README.md').exists(),'Missing README')
check((ROOT/'assets/fonts/Oswald-LICENSE.txt').exists(),'Oswald license missing')
check((ROOT/'assets/fonts/Raleway-LICENSE.txt').exists(),'Raleway license missing')
summary=dict(passed=not issues,pages=len(pages),brands=len(D['brands']),items=len(D['items']),articles=len(D['articles']),categories=len(D['categories']),svgAssets=len(list((ROOT/'assets/img').glob('*.svg'))),runtimeJavaScriptBytes=jsbytes,articleChineseCharacters=article_counts,issues=issues)
(ROOT/'reports/static-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
raise SystemExit(bool(issues))
