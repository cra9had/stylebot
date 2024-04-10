from enum import Enum


class Config(Enum):
    FAVOURITES_IN_PAGE = 5
    DEFAULT_MIN_PRICE = 0
    DEFAULT_MAX_PRICE = 999999


class Subscriptions(Enum):
    light = {'name': "light", "likes_quantity": 300, "price": 199}
    medium = {'name': "medium", "likes_quantity": 500, "price": 299}
    rare = {'name': "rare", "likes_quantity": 1000, "price": 499}
    unlimited = {'name': "unlimited", "likes_quantity": 99999, "price": 999}
