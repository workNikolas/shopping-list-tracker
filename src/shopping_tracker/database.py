import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "shopping_tracker.db"

def create_connection() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_PATH)

def initialize_database() -> None:
    connection = create_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,
            external_id TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            image_url TEXT,

            UNIQUE(provider, external_id)
        )
        """
    )

    connection.execute(
    """
    CREATE TABLE IF NOT EXISTS product_snapshots (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        price TEXT,
        avg_rating REAL,
        availability INTEGER,
        shipping_fee TEXT,
        observed_at TEXT NOT NULL,

        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """
    )
    
    connection.commit()
    connection.close()

def migrate_add_image_url() -> None:
    connection = create_connection()

    try:
        cursor = connection.execute(
            "PRAGMA table_info(products)"
        )
        columns = cursor.fetchall()
        column_names = []

        for column in columns:
            column_names.append(column[1])

        if "image_url" not in column_names:
            connection.execute(
                """
                ALTER TABLE products
                ADD COLUMN image_url TEXT
                """
            )
            connection.commit()
    finally:
        connection.close()
        


if __name__ == "__main__":
    initialize_database()