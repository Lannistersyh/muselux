"""Photographic covers for design families, selected from their verified galleries."""
from html import escape
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parents[1]
# Optical sizing removes surrounding empty space in the card viewport only.
# Source photographs and the full, uncropped detail galleries remain unchanged.
SCALES={'lady-dior':1.65,'galleria':1.6,'speedy':1.4,'trinity':1.25,'juste-un-clou':.9,
        'classic-box':1.12,'love':1.08,'coco-crush':1.08}
FULL_BLEED={'trinity','chanel-255','classic-flap','boy'}


def selection(data,galleries,root=ROOT):
    covers={}
    for number,product in enumerate((p for p in data['items'] if not p.get('styleEdit')),1):
        record=galleries[product['id']]
        image=record['images'][0]
        path=Path(image['path'])
        if (not path.as_posix().startswith('assets/img/') or '..' in path.parts
                or path.suffix.lower() not in ('.jpg','.jpeg','.png','.webp')
                or not (root/path).is_file()):
            raise ValueError('Classic cover needs an existing product photograph: '+product['id'])
        if min(image['width'],image['height'])<700:
            raise ValueError('Classic cover resolution is too small: '+product['id'])
        covers[product['id']]={**image,'sha256':hashlib.sha256((root/path).read_bytes()).hexdigest(),
            'number':number,'reference':record['reference'],
            'scale':SCALES.get(product['id'],1),
            'fit':'cover' if product['id'] in FULL_BLEED else 'contain'}
    if len({image['sha256'] for image in covers.values()})!=len(covers):
        raise ValueError('Classic covers must depict distinct designs')
    return covers


def card(product,brand,image,prefix=''):
    e=lambda value:escape(str(value),quote=True)
    alt=image['alt']+'；该系列的具体实物参考版本，型号和图源见详情'
    return f'''<article class="item-card archive-card reveal" data-archive-id="{e(product['id'])}" data-house="{e(product['brand'])}"><a href="{prefix}item/{e(product['id'])}.html"><div class="archive-art"><img src="{prefix}{e(image['path'])}" width="{image['width']}" height="{image['height']}" style="--archive-scale:{image['scale']};--archive-fit:{image['fit']}" alt="{e(alt)}" loading="lazy" decoding="async"></div><div class="archive-body"><div class="archive-meta"><span>{e(brand['name'])}</span><span>DESIGN {image['number']:02d}</span></div><h3>{e(product['name'])}</h3><p class="archive-subtitle">{e(product['nameZh'])}</p><p class="archive-description">{e(product['oneLiner'])}</p><span class="archive-explore">探索设计 <span aria-hidden="true">↗</span></span></div></a></article>'''
