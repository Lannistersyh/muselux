"""Merge dated necklace and jewelry edits, preserving the core catalog and bags."""
from collections import Counter
from datetime import date
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('jewel-years-2022-2023.json','jewel-years-2024-2025.json','jewel-years-2026.json')
CUTOFF='2026-10-19'
CHECKED='2026-10-20'
BOOKS={'necklace':('necklaceYears','The Necklace Yearbook','necklaces-by-year.html'),
       'jewelry':('jewelryYears','The Jewelry Yearbook','jewelry-by-year.html')}

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
            year['yearToDate']=year['year']==2026
            if year['yearToDate']:year['cutoff']=CUTOFF
            for x in year['entries']:
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
                    assert date.fromisoformat(stamp)<=date.fromisoformat(CHECKED),'Future price date'
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
                x['checkedAt']=CHECKED
                for source in x['selectionSources']:
                    stamp=source.get('publishedAt')
                    if stamp and re.fullmatch(r'\d{4}-\d{2}-\d{2}',stamp):
                        assert date.fromisoformat(stamp)<=date.fromisoformat(CUTOFF),'Future source date'
        data[key]=sorted(years,key=lambda y:y['year'])
        merged.extend(entries)
    data['jewelYearbooks']={'checkedAt':CHECKED,'evidenceCutoff':CUTOFF,'currency':'USD','entries':60,'hotPerCategoryYear':4,'editionsPerCategoryYear':2,'limitations':[note for bundle in research for note in bundle.get('limitations',[])]}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    fields=('id','category','year','selection','brandName','name','reference','source','selectionSources','priceUSD','priceBasis','priceAsOf','priceLabelEn','priceNoteEn','priceSource','priceEvidence','editionType','editionLabelEn','editionEvidence','editionNoteEn','editionSource','image','imageSource','imagePageURL','imageCredit','imageRightsNote','checkedAt')
    (ROOT/'reports/jewel-yearbook-sources.json').write_text(json.dumps([{k:x.get(k) for k in fields} for x in merged],ensure_ascii=False,indent=2)+'\n')
    print('Merged necklace and jewelry yearbooks: 30 entries per category, 60 total.')

if __name__=='__main__':main()
