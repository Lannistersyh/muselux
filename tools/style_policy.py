"""Shared scope and price provenance rules for photographed core products."""

PRICE_STATUSES = ('live', 'official-snapshot', 'resale-ask')


def category_limit(category):
    return 8 if category in ('necklace', 'jewelry') else 5


def valid_category_counts(counts, categories):
    return set(counts) == set(categories) and all(3 <= n <= category_limit(c) for c, n in counts.items())


def is_resale(product):
    return product.get('priceStatus') == 'resale-ask'


def price_heading(product):
    return 'RESALE ASKING PRICE' if is_resale(product) else 'U.S. RETAIL REFERENCE'


def card_price_label(product):
    return 'USD resale ask · listed example' if is_resale(product) else 'U.S. reference · before tax'


def validate_resale(product):
    if is_resale(product):
        for key in ('sellerName', 'itemCondition', 'listingReference', 'priceAsOf', 'priceEvidence', 'availabilityEn'):
            assert isinstance(product.get(key), str) and product[key].strip(), product['id'] + ': missing resale ' + key
        assert product['reference'].strip() == product['listingReference'].strip(), product['id'] + ': merchant listing reference mismatch'
