"""Derive brand coverage from the complete static product catalog."""
from bag_yearbook import entries


def products(data):
    return data['items'] + entries(data)


def brand_ids(product):
    return list(dict.fromkeys([product['brand']] + product.get('collaboratorBrands', [])))


def enrich(data):
    """Keep brand counts, categories and search aliases tied to real products.

    classicItems remains the curated dictionary/Style Edit list. itemIds is the
    complete derived association, including every yearbook and named brand partner.
    Unknown brands stop generation so future catalog additions cannot be omitted.
    """
    brands = {brand['id']: brand for brand in data['brands']}
    if len(brands) != len(data['brands']):
        raise ValueError('Duplicate brand ID')
    catalog = products(data)
    if len({product['id'] for product in catalog}) != len(catalog):
        raise ValueError('Duplicate product ID')
    for brand in brands.values():
        brand['itemIds'] = []
        brand['primaryItemCount'] = 0
        brand['collaborationItemCount'] = 0
    for product in catalog:
        names = []
        for brand_id in brand_ids(product):
            if brand_id not in brands:
                raise ValueError(product['id'] + ': brand missing from index: ' + brand_id)
            brand = brands[brand_id]
            brand['itemIds'].append(product['id'])
            key = 'primaryItemCount' if brand_id == product['brand'] else 'collaborationItemCount'
            brand[key] += 1
            if product['category'] not in brand['categories']:
                brand['categories'].append(product['category'])
            names += [brand['id'], brand['name'], brand['nameZh']] + brand.get('aliases', [])
        product['brandNames'] = ' '.join(dict.fromkeys(names))
    for brand in brands.values():
        brand['itemCount'] = len(brand['itemIds'])
    return catalog
