import time
import random
from typing import Literal
from datetime import datetime


IMAGES = {
  "TINY": "https://basket-{0}.wbbasket.ru/vol{1}/part{2}/{3}/images/tm/{4}.jpg",
  "BIG": "https://basket-{0}.wbbasket.ru/vol{1}/part{2}/{3}/images/big/{4}.jpg",
  "SMALL": "https://basket-{0}.wbbasket.ru/vol{1}/part{2}/{3}/images/c246x328/{4}.jpg",
  "MEDIUM":"https://basket-{0}.wbbasket.ru/vol{1}/part{2}/{3}/images/c516x688/{4}.jpg",
}
IMAGES_SIZES = Literal["SMALL", "TINY", "BIG", "MEDIUM"]


BASKETS = [
  [0, 143],
  [144, 287],
  [288, 431],
  [432, 719],
  [720, 1007],
  [1008, 1061],
  [1062, 1115],
  [1116, 1169],
  [1170, 1313],
  [1314, 1601],
  [1602, 1655],
  [1656, 1919],
  [1920, 2045],
  [2046, 2189]
]


def gen_new_user_id():
    t = int(time.time())
    e = str(random.randint(0, 2**30)) + str(t)
    return e


def get_query_id_for_search():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    return f"qid{gen_new_user_id()}{formatted_time}"


def image_url(product_id: int, image_type: IMAGES_SIZES = "SMALL", order=1):
    vol = product_id // 100000
    part = product_id // 1000
    basket = get_basket_number(product_id)
    basket_with_zero = f"0{basket}" if basket < 10 else str(basket)
    _random = str(int(datetime.now().timestamp() * 1000))
    url = IMAGES[image_type]

    return f"{url.format(basket_with_zero, vol, part, product_id, order)}?r={_random}"


def get_basket_number(product_id: int):
    vol = product_id // 100000
    for index, basket_range in enumerate(BASKETS):
        if basket_range[0] <= vol <= basket_range[1]:
            return index + 1
    return 1
