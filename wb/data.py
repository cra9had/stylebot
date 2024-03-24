import json
from dataclasses import dataclass, asdict


@dataclass
class Filters:
    dest: float = -1257786  # MOSCOW\


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
        return json.dumps(asdict(self))