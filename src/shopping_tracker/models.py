from datetime import datetime
from dataclasses import dataclass, field
from decimal import Decimal

# Immutable data
@dataclass
class Product:
    provider: str
    external_id: str
    name: str
    url: str
    image_url: str
    #language: str
    #national: bool

# Mutable data
@dataclass
class ProductSnapshot:
    price: Decimal | None
    avg_rating: float | None 
    availability: bool | None
    shipping_fee: Decimal | None
    observed_at: datetime = field(default_factory=datetime.now)

@dataclass
class Money:
    amount: Decimal
    currency: str
