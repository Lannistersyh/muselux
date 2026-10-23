"""Merge five evidence-led annual bag edits without changing core Style Edit."""
from collections import Counter
from datetime import date
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('bag-years-2022-2023.json','bag-years-2024-2025.json','bag-years-2026.json')

def iso_date(value,label):
    assert isinstance(value,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',value),label+': expected an ISO date'
    return date.fromisoformat(value)

def checked_date(product):
    return iso_date(product.get('checkedAt'),product['id']+' review date')

def evidence_cutoff(year):
    latest=max(checked_date(x) for x in year['entries'])
    if year['year']==2026:
        assert year.get('yearToDate'), '2026 source must state its year-to-date scope'
        cutoff=iso_date(year.get('cutoff'),'2026 evidence cutoff')
        assert cutoff.year==2026 and cutoff<=latest,'2026 evidence cutoff exceeds the actual review dates'
        return cutoff
    if year.get('evidenceCutoff'):
        cutoff=iso_date(year['evidenceCutoff'],str(year['year'])+' evidence cutoff')
        assert cutoff<=latest,'Evidence cutoff exceeds the actual review dates'
        return cutoff
    # Retrospective annual reports may be published after the selection year.
    return latest

def validate_sources(sources,cutoff,label):
    for source in sources:
        stamp=source.get('publishedAt')
        if stamp and re.fullmatch(r'\d{4}-\d{2}-\d{2}',stamp):
            assert date.fromisoformat(stamp)<=cutoff,label+': evidence after its stated cutoff or review date'

def main():
    path=ROOT/'tools/content.json'
    data=json.loads(path.read_text())
    years=[];limitations=[]
    for name in SOURCES:
        research=json.loads((ROOT/'tools/research'/name).read_text())
        years.extend(research['years'])
        for key in ('limitations','verificationLimitations'):
            limitations.extend(research.get(key,[]))
    assert sorted(y['year'] for y in years)==list(range(2022,2027)), 'Expected 2022–2026 exactly once'
    entries=[x for year in years for x in year['entries']]
    assert len(entries)==30 and len({x['id'] for x in entries})==30
    assert not {x['id'] for x in entries}&{x['id'] for x in data['items']}
    for year in years:
        assert Counter(x['selection'] for x in year['entries'])=={'hot':4,'limited':2}
        assert year['sources'], 'Missing year sources'
        cutoff=evidence_cutoff(year)
        validate_sources(year['sources'],cutoff,str(year['year']))
        for x in year['entries']:
            checked=checked_date(x)
            assert x['year']==year['year']
            assert x['priceCurrency']=='USD'
            assert x['priceUSD'] is None or (isinstance(x['priceUSD'],(int,float)) and x['priceUSD']>0)
            assert (ROOT/x['image']).is_file(), x['image']
            assert x['selectionSources'], 'Missing dated popularity/edition evidence'
            if x['selection']=='limited':
                assert x['editionType'] in ('numbered','limited-edition','seasonal-capsule')
                assert x['editionEvidence'] and x['editionSource'] and x['editionLabelEn']
            if x['priceUSD'] is not None:assert x.get('priceSource')
            assert x.get('priceAsOf'),x['id']+': price date absent'
            for stamp in re.findall(r'\d{4}-\d{2}-\d{2}',x['priceAsOf']):
                assert date.fromisoformat(stamp)<=checked,x['id']+': price date after its review date'
            assert len(x['introEn'].split())>=70 and len(x['featuresEn'])==3
            x['category']='bags';x['annualEdit']=True
            x['oneLiner']=re.split(r'(?<=[.!?])\s+',x['introEn'])[0]
            validate_sources(x['selectionSources'],min(cutoff,checked),x['id'])
    data['bagYears']=sorted(years,key=lambda y:y['year'])
    data['bagYearbook']={'checkedAt':max(checked_date(x) for x in entries).isoformat(),'currency':'USD','years':[2022,2023,2024,2025,2026],'entries':30,'hotPerYear':4,'editionsPerYear':2,'methodology':'Four editorial popular picks per year from dated demand reports and fashion coverage; source rankings retain their stated periods. Edition types are labelled individually.','limitations':limitations}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    fields=('id','year','selection','brandName','name','reference','source','selectionSources','priceUSD','priceBasis','priceAsOf','priceLabelEn','priceNoteEn','priceSource','priceEvidence','editionType','editionLabelEn','editionEvidence','editionNoteEn','editionSource','image','imageSource','imageCredit','imageRightsNote','checkedAt')
    (ROOT/'reports/bag-yearbook-sources.json').write_text(json.dumps([{k:x.get(k) for k in fields} for x in entries],ensure_ascii=False,indent=2)+'\n')
    print('Merged five annual bag edits: four popular picks + two editions per year, 30 entries total.')

if __name__=='__main__':main()
