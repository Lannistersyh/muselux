"""Merge the independently sourced product records into the editable site data.

Idempotent; no network access, downloads or implicit currency conversions.
"""
from pathlib import Path
from collections import Counter
from datetime import date
from bag_yearbook import price_text
from style_policy import PRICE_STATUSES, valid_category_counts, is_resale, validate_resale
import json, re

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tools/content.json'
SOURCES=['bags-scarves.json','necklace-jewelry.json','watches-fragrance.json','chrome-hearts-products.json','perfumery-products.json','bag-edit-expansion.json']

def checked_date(product):
    value=product.get('checkedAt','')
    assert isinstance(value,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',value), product['id']+': missing ISO review date'
    return date.fromisoformat(value)

def validate_price_dates(product):
    checked=checked_date(product)
    for stamp in re.findall(r'\d{4}-\d{2}-\d{2}',product.get('priceAsOf','')):
        assert date.fromisoformat(stamp)<=checked,product['id']+': price date after its review date'
    return checked

def price_context(product):
    reviewed=checked_date(product).strftime('%d %B %Y').lstrip('0')
    if is_resale(product):
        return 'Resale listing · '+product['sellerName']+' · reviewed '+reviewed
    if product['priceStatus']=='live':
        return 'Official U.S. product page · checked '+reviewed
    note=product.get('sourceSnapshotNote','').lower()
    ages=[(r'(?:3|three) months?','3 months earlier'),(r'(?:2|two) weeks?','2 weeks earlier'),(r'(?:last|one|1) week','the previous week'),(r'yesterday|(?:one|1) day','the previous day'),(r'today|same day','the same day')]
    for pattern,label in ages:
        if re.search(pattern,note):
            return 'Official page snapshot · reported crawled '+label+'; reviewed '+reviewed
    return 'Official page snapshot · reviewed '+reviewed+'; live price may differ'

def main():
    data=json.loads(DATA.read_text())
    products=[];notes={};limitations=[]
    for name in SOURCES:
        source=json.loads((ROOT/'tools/research'/name).read_text())
        products.extend(source['products'])
        notes.update(source['categoryNotes'])
        for key in ('limitations','verificationLimitations'):
            limitations.extend(source.get(key,[]))
    categories={x['id'] for x in data['categories']}
    counts=Counter(x['category'] for x in products)
    assert valid_category_counts(counts,categories),'Expected three to five photographed products per category; bags allow up to twelve; necklaces and jewelry allow up to eight; fragrance allows up to nine'
    assert len({x['id'] for x in products})==len(products), 'Duplicate product id'
    brands={x['id']:x for x in data['brands']}
    legacy=[x for x in data['items'] if not x.get('styleEdit')]
    legacy_ids={x['id'] for x in legacy}
    old_style_ids={x['id'] for x in data['items'] if x.get('styleEdit')}
    new_ids={x['id'] for x in products}
    assert not new_ids&legacy_ids,'Style Edit ID collision with the classic catalog'
    for brand in brands.values():
        brand['classicItems']=[key for key in brand['classicItems'] if key not in old_style_ids|new_ids]
    for x in legacy:
        # Previous regional ranges are removed, rather than converted using an
        # unverified exchange rate or presented as a quote for a whole family.
        x['priceRange']='U.S. pricing varies by reference, size and material. Check the official U.S. store for a current quote. 仅供参考，请以品牌官方渠道为准。'
    for x in products:
        assert x['brand'] in brands
        assert not x.get('parentItem') or x['parentItem'] in legacy_ids
        assert isinstance(x['priceUSD'],(int,float)) and x['priceUSD']>0
        assert (ROOT/x['image']).is_file(), x['image']
        assert x['priceStatus'] in PRICE_STATUSES
        validate_resale(x)
        validate_price_dates(x)
        x['styleEdit']=True
        x['priceCurrency']='USD'
        x['oneLiner']=re.split(r'(?<=[.!?])\s+',x['introEn'])[0]
        x['story']=x['introEn']
        x['facts']=x['featuresEn']
        x['priceContextEn']=price_context(x)
        x['priceRange']=(price_text(x)+', resale asking price for this listed example. 仅供参考，商家报价以来源页面为准；品牌价格以官方渠道为准。') if is_resale(x) else price_text(x)+', pictured variant, before tax. 仅供参考，请以品牌官方渠道为准。'
        x['relatedArticles']=[a['id'] for a in data['articles'] if a['category']==x['category']][:3]
        brand=brands[x['brand']]
        brand['classicItems'].insert(0,x['id'])
        if x['category'] not in brand['categories']:brand['categories'].append(x['category'])
    for c in data['categories']:c['editIntro']=notes[c['id']]
    for a in data['articles']:
        if a['id']=='mag-11':
            a['body']=a['body'].replace('一千元以内','US$250 以内').replace('一千到五千','US$250–1,000').replace('一千至五千','US$250–1,000').replace('五千元以上','US$1,000 以上')
    data['items']=legacy+products
    data['styleEdit']={'checkedAt':max(checked_date(x) for x in products).isoformat(),'currency':'USD','products':len(products),'perCategory':dict(counts),'limitations':limitations}
    DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    manifest=[{k:x[k] for k in ('id','brand','reference','source','image','imageSource','imageCredit','imageRightsNote','priceUSD','priceStatus','priceContextEn','checkedAt')} for x in products]
    (ROOT/'reports/product-sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'Merged {len(products)} photographed products; 3–5 per category, up to 12 for bags, 8 for jewelry and necklaces, 9 for fragrance; USD provenance labelled.')

if __name__=='__main__':main()
