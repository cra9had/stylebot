from dataclasses import asdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Filters:
    is_original: Optional[int] = None  # 1 - ORIGINAL
    dest: float = -1257786  # MOSCOW


@dataclass
class Coordinates:
    latitude: float
    longitude: float  # TODO: Maybe Decimal?


@dataclass
class Product:
    id: int  # Артикул товара WildBerries
    price: int
    name: str
    image_url: str

    def to_json(self):
        return asdict(self)
