import ormar


class User(ormar.Model):
    telegram_id: int = ormar.BigInteger(primary_key=True)
    username: str = ormar.String(nullable=True, max_length=64)
