"""Source-backed product views, kept separate from dated product/price records."""
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load(root=ROOT):
    records = {}
    for path in sorted((root/'tools/research').glob('product-views-*.json')):
        for record in json.loads(path.read_text())['records']:
            if record['id'] in records:
                raise ValueError('Duplicate gallery: '+record['id'])
            records[record['id']] = record
    return records


def views(product, record):
    """Existing exact-reference photograph stays first; family entries name a variant."""
    result = []
    if product.get('image'):
        result.append(dict(path=product['image'], source=product['imageSource'],
                           pageSource=product.get('imagePageURL', product['source']),
                           credit=product['imageCredit'], width=product['imageWidth'],
                           height=product['imageHeight'], viewLabel='Original view',
                           alt=product.get('brandName', '')+' '+product['name']+' — '+product['color']))
    result.extend(record.get('images', []))
    return result


def render(product, records, prefix='../'):
    record = records.get(product['id'])
    if not record:
        return ''
    images = views(product, record)
    esc = lambda text: escape(str(text), quote=True)
    figures, buttons = [], []
    for index, image in enumerate(images):
        target = 'view-'+product['id']+'-'+str(index+1)
        source = esc(image['pageSource'])
        source_note = '<small class="gallery-image-note">'+esc(image['sourceNote'])+'</small>' if image.get('sourceNote') else ''
        figures.append(f'''<figure class="product-photo gallery-view" data-gallery-view id="{target}"><a href="{prefix}{esc(image['path'])}" target="_blank" rel="noopener" aria-label="Open full photograph: {esc(image['viewLabel'])}"><img src="{prefix}{esc(image['path'])}" width="{image['width']}" height="{image['height']}" alt="{esc(image['alt'])}" {'fetchpriority="high"' if index==0 else 'loading="lazy"'}></a><figcaption><span>{index+1:02d} / {len(images):02d} · {esc(image['viewLabel'])}</span><a href="{source}" target="_blank" rel="noopener">{esc(image['credit'])} ↗</a>{source_note}</figcaption></figure>''')
        buttons.append(f'''<button type="button" data-gallery-index="{index}" aria-controls="{target}" aria-pressed="{'true' if index==0 else 'false'}"><img src="{prefix}{esc(image['path'])}" width="{image['width']}" height="{image['height']}" loading="lazy" alt="" aria-hidden="true"><span>{esc(image['viewLabel'])}</span></button>''')
    note = '<p class="gallery-variant">'+esc(record['note'])+' · Ref. '+esc(record['reference'])+'</p>' if record.get('note') else ''
    return f'''<div class="product-gallery" data-product-gallery lang="en"><p class="eyebrow rose-text">A CLOSER LOOK / {len(images):02d} VIEWS</p>{note}<div class="gallery-stage">{''.join(figures)}</div><div class="gallery-controls" data-gallery-controls hidden role="group" aria-label="Choose a product view">{''.join(buttons)}</div><p class="gallery-status sr-only" data-gallery-status aria-live="polite" aria-atomic="true"></p></div>'''
