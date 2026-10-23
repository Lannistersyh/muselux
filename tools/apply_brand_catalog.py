"""Merge sourced brand histories and explicitly associate existing collaborations."""
from pathlib import Path
import json
from brand_catalog import enrich, products

ROOT = Path(__file__).resolve().parents[1]
PARTNERS = {
    'bag-2022-gucci-adidas-large-duffle': ['adidas'],
    'necklace-2022-adidas-gucci-gourmette': ['adidas'],
    'necklace-2022-fendace-chain-necklace': ['versace'],
    'jewelry-2022-fendace-hoop-earrings': ['versace'],
    'bag-2024-fendi-frgmt-pokemon-beaded-baguette': ['fragment-design'],
    'necklace-2024-fendi-frgmt-pokemon-pokeball-necklace': ['fragment-design'],
    'jewelry-2024-fendi-frgmt-ring-gold': ['fragment-design'],
    'jewelry-2024-fendi-frgmt-pokemon-earrings-gold': ['fragment-design'],
}


def main():
    path = ROOT / 'tools/content.json'
    data = json.loads(path.read_text())
    by_id = {brand['id']: brand for brand in data['brands']}
    added = []
    for source in sorted((ROOT/'tools/research').glob('brand-expansion-*.json')):
        research = json.loads(source.read_text())
        for brand in research['brands']:
            if brand['id'] in by_id:
                current = by_id[brand['id']]
                classics = current.get('classicItems', [])
                categories = list(dict.fromkeys(current['categories'] + brand['categories']))
                current.update(brand)
                current['classicItems'] = classics
                current['categories'] = categories
            else:
                data['brands'].append(brand)
                by_id[brand['id']] = brand
                added.append(brand['id'])
    catalog = {product['id']: product for product in products(data)}
    for product_id, partners in PARTNERS.items():
        catalog[product_id]['collaboratorBrands'] = partners
    for brand_id in ('adidas', 'versace', 'fragment-design'):
        by_id[brand_id]['role'] = 'collaborator'
    by_id['fragment-design']['aliases'] = ['FRGMT', 'Fragment', '藤原浩']
    by_id['the-row']['historyNote'] = (
        '成立年份采用 The Row 现行官网所列的 2005 年；'
        'CFDA 的 2021 年回顾使用 2006 年，相关资料存在这一口径差异。'
    )
    # Persist complete categories, but derive product associations during every build.
    enrich(data)
    for brand in data['brands']:
        for field in ('itemIds', 'itemCount', 'primaryItemCount', 'collaborationItemCount'):
            brand.pop(field, None)
    for product in catalog.values():
        product.pop('brandNames', None)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'added': added, 'brands': len(data['brands']),
                      'products': len(catalog), 'collaborations': len(PARTNERS)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
