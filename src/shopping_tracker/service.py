from src.shopping_tracker.models import Product, ProductSnapshot
from src.shopping_tracker.amazon import AmazonFetcher, AmazonParser, get_asin
from src.shopping_tracker.repository import (
    add_product, 
    add_snapshot, 
    get_product, 
    get_product_history,
    get_all_products,
    )
from dataclasses import dataclass

@dataclass
class TrackingResult:
    product_id: int
    product: Product
    snapshot: ProductSnapshot

@dataclass
class ProductDetails:
    product_id: int
    product: Product
    latest_snapshot: ProductSnapshot
    history: list[ProductSnapshot]

def track_amazon_product(url: str) -> TrackingResult:

    asin = get_asin(url)
    if asin is None:
        raise ValueError("Invalid Amazon product URL")
    
    fetcher = AmazonFetcher(url)
    html = fetcher.fetch()
    parser = AmazonParser(html)

    title = parser.parse_title()

    if title is None:
        raise ValueError("Could not extract product title")

    # Instantiate objects
    product = Product(
        provider="amazon",
        external_id=asin,
        name=title,
        url=url,
    )

    snapshot = ProductSnapshot(
        price=parser.parse_price(),
        avg_rating=parser.parse_rating(),
        availability=None,
        shipping_fee=None
    )

    # Persists to database
    product_id = add_product(product)
    print("PRODUCT ID:", product_id)
    print("PRODUCT:", product)
    add_snapshot(product_id, snapshot)

    return TrackingResult(
        product_id=product_id,
        product=product,
        snapshot=snapshot,
    )

def get_product_details(product_id) -> ProductDetails | None:
    product = get_product(product_id)
    if product is None:
        return None
    
    history = get_product_history(product_id)
    if not history:
        return None
    
    return ProductDetails(
        product_id=product_id,
        product=product,
        latest_snapshot=history[-1],
        history=history
    )

def list_tracked_products() -> list[tuple]:
    return get_all_products()