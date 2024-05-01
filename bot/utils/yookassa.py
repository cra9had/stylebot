from os import getenv

import yookassa


def create_payment(product_title: str, product_price: int, bot_link: str):
    yookassa.Configuration.account_id = getenv("YOOKASSA_API_ID")
    yookassa.Configuration.secret_key = getenv("YOOKASSA_API_KEY")

    payment = yookassa.Payment().create(
        {
            "amount": {"value": product_price, "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/wbstylist_bot",
            },
            "description": product_title,
            "capture": True,
        }
    )

    url = payment.confirmation.confirmation_url

    return url, payment.id


def check_payment(payment_id):
    return yookassa.Payment.find_one(payment_id).status == "succeeded"
