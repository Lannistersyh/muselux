"""Merge dated necklace and jewelry edits, preserving the core catalog and bags."""
from collections import Counter
from datetime import date
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('jewel-years-2022-2023.json','jewel-years-2024-2025.json','jewel-years-2026.json')
BOOKS={'necklace':('necklaceYears','The Necklace Yearbook','necklaces-by-year.html'),
       'jewelry':('jewelryYears','The Jewelry Yearbook','jewelry-by-year.html')}

def iso_date(value,label):
    assert isinstance(value,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',value),label+': expected an ISO date'
    return date.fromisoformat(value)

def checked_date(product):
    return iso_date(product.get('checkedAt'),product['id']+' review date')

def evidence_cutoff(year):
    latest=max(checked_date(x) for x in year['entries'])
    if year['year']==2026:
        assert year.get('yearToDate'),'2026 source must state its year-to-date scope'
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
    research=[json.loads((ROOT/'tools/research'/name).read_text()) for name in SOURCES]
    used={x['id'] for x in data['items']}|{x['id'] for y in data.get('bagYears',[]) for x in y['entries']}
    merged=[]
    for category,(key,title,book_path) in BOOKS.items():
        years=[y for bundle in research for y in bundle[key]]
        assert sorted(y['year'] for y in years)==list(range(2022,2027)),key+': expected five unique years'
        entries=[x for y in years for x in y['entries']]
        assert len(entries)==len({x['id'] for x in entries})==30
        assert not {x['id'] for x in entries}&used,'Catalog ID collision'
        used.update(x['id'] for x in entries)
        for year in years:
            assert Counter(x['selection'] for x in year['entries'])=={'hot':4,'limited':2}
            assert year['sources'] and year['headlineEn'] and year['introEn']
            cutoff=evidence_cutoff(year)
            validate_sources(year['sources'],cutoff,str(year['year']))
            for x in year['entries']:
                checked=checked_date(x)
                assert x['year']==year['year'] and x['category']==category
                assert x['id'].startswith(category+'-'+str(year['year'])+'-')
                assert x['priceCurrency']=='USD'
                assert x['priceBasis'] in ('current-retail','release-retail','reported-retail','auction-result','resale-ask','unlisted')
                assert x['priceUSD'] is None or (isinstance(x['priceUSD'],(int,float)) and x['priceUSD']>0)
                if x['priceUSD'] is not None:assert x.get('priceSource') and x.get('priceEvidence')
                # Keep the source's precision: a month-level archived snapshot
                # must not acquire an invented capture day during the merge.
                assert x['priceAsOf']
                for stamp in re.findall(r'\d{4}-\d{2}-\d{2}',x['priceAsOf']):
                    assert date.fromisoformat(stamp)<=checked,x['id']+': price date after its review date'
                assert (ROOT/x['image']).is_file(),x['image']
                assert x['selectionSources'] and x['selectionReasonEn']
                if x['selection']=='limited':
                    assert x['editionType'] in ('numbered','limited-edition','seasonal-capsule')
                    assert x['releaseYear']==year['year'],'Edition belongs to another release year'
                    assert x['editionEvidence'] and x['editionSource'] and x['editionLabelEn']
                assert len(x['introEn'].split())>=70 and len(x['featuresEn'])==3
                x['annualEdit']=True
                x['yearbookTitle']=title;x['yearbookPath']=book_path
                x['oneLiner']=re.split(r'(?<=[.!?])\s+',x['introEn'])[0]
                validate_sources(x['selectionSources'],min(cutoff,checked),x['id'])
        data[key]=sorted(years,key=lambda y:y['year'])
        merged.extend(entries)
    cutoff=max(evidence_cutoff(y) for category,(key,_,_) in BOOKS.items() for y in data[key] if y['year']==2026)
    data['jewelYearbooks']={'checkedAt':max(checked_date(x) for x in merged).isoformat(),'evidenceCutoff':cutoff.isoformat(),'currency':'USD','entries':60,'hotPerCategoryYear':4,'editionsPerCategoryYear':2,'limitations':[note for bundle in research for key in ('limitations','verificationLimitations') for note in bundle.get(key,[])]}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    fields=('id','category','year','selection','brandName','name','reference','source','selectionSources','priceUSD','priceBasis','priceAsOf','priceLabelEn','priceNoteEn','priceSource','priceEvidence','editionType','editionLabelEn','editionEvidence','editionNoteEn','editionSource','image','imageSource','imagePageURL','imageCredit','imageRightsNote','checkedAt')
    (ROOT/'reports/jewel-yearbook-sources.json').write_text(json.dumps([{k:x.get(k) for k in fields} for x in merged],ensure_ascii=False,indent=2)+'\n')
    print('Merged necklace and jewelry yearbooks: 30 entries per category, 60 total.')

if __name__=='__main__':main()
