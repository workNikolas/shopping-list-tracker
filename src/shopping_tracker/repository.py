from src.shopping_tracker.models import Product, ProductSnapshot
from src.shopping_tracker.database import create_connection

from decimal import Decimal
from datetime import datetime


def add_product(product: Product) -> int:
    product_id = get_product_id(product.provider, product.external_id)

    if product_id is not None:
        return product_id

    connection = create_connection()
    try:
        cursor = connection.execute(
                """
                INSERT INTO products (provider, external_id, name, url)
                VALUES (?, ?, ?, ?)
                """,
                (
                    product.provider,
                    product.external_id,
                    product.name,
                    product.url,
                ),
            ) 


        connection.commit()
        product_id = cursor.lastrowid
    
        return product_id
    finally:
        connection.close()

def add_snapshot(product_id: int, snapshot: ProductSnapshot) -> int:
    connection = create_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO product_snapshots (
                product_id,
                price,
                avg_rating,
                availability,
                shipping_fee,
                observed_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                str(snapshot.price) if snapshot.price is not None else None,
                snapshot.avg_rating,
                snapshot.availability,
                str(snapshot.shipping_fee) if snapshot.shipping_fee is not None else None,
                snapshot.observed_at.isoformat(),
            )
        )
        connection.commit()
        snapshot_id = cursor.lastrowid
    finally:
        connection.close()

    return snapshot_id

def get_product(product_id:int) -> Product | None:
    connection = create_connection()

    try:
        cursor = connection.execute(
            """
            SELECT provider, external_id, name, url
            FROM products
            WHERE id = ?
            """,
            (product_id,)
        )
        row = cursor.fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    return Product(
        provider=row[0], external_id=row[1], name=row[2], url=row[3]
    )

def get_product_id(provider: str, external_id: str) -> int | None:
    connection = create_connection()

    try:
        cursor = connection.execute(
                """
                SELECT id
                FROM products
                WHERE provider = ? and external_id = ?
                """,
                (provider, external_id)
            )

        row = cursor.fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    return row[0]

def get_product_history(product_id: int) -> list[ProductSnapshot]:
    connection = create_connection()
    try:
        cursor = connection.execute(
            """
            SELECT
                price,
                avg_rating,
                availability,
                shipping_fee,
                observed_at
            FROM product_snapshots
            WHERE product_id = ?
            ORDER BY observed_at ASC
            """,
            (product_id,),
            )    
        rows = cursor.fetchall()
    finally:
        connection.close()

    history = []
    for row in rows:
        snapshot = ProductSnapshot(
        price=Decimal(row[0]) if row[0] is not None else None,
        avg_rating=row[1] if row[1] is not None else None,
        availability=bool(row[2]) if row[2] is not None else None,
        shipping_fee=Decimal(row[3]) if row[3] is not None else None,
        observed_at=datetime.fromisoformat(row[4]),
        )

        history.append(snapshot)

    return history

def get_all_products() -> list[tuple[int, Product]]:
    connection = create_connection()
    try:
        cursor = connection.execute(
            """
            SELECT id, provider, external_id, name, url
            FROM products
            ORDER by id 
            """
            )

        rows = cursor.fetchall()
    finally:
        connection.close()

    tracked_products = []
    for row in rows:
        product_id = row[0]
        product = Product(
            provider = row[1],
            external_id = row[2],
            name= row[3],
            url = row[4],
        )

        tracked_products.append((product_id, product))
    
    return tracked_products