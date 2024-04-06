from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import LabeledPrice
from aiogram.types import Message
from aiogram.types import PreCheckoutQuery

from bot.keyboards.payment_kbs import get_subscription_keyboard

router = Router()


async def no_free_searches_left(message: Message):
    await message.answer(
        "Бесплатные комбинации закончились. Приобретите подписку.",
        reply_markup=get_subscription_keyboard(),
    )


@router.message(F.text == "/pay")
async def send_payment_invoice(message: Message):
    await message.bot.send_invoice(
        message.chat.id,
        title="Подписка на бота",
        description="Активация подписки на бота на 1 месяц",
        provider_token="381764678:TEST:82090",  # TODO: to .env
        currency="rub",
        photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[LabeledPrice(label="Подписка на 1 месяц", amount=500 * 100)],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload",
    )


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@router.message(F.successful_payment)
async def successful_payment(message: Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment
    for k, v in payment_info:
        print(f"{k} = {v}")

    await message.bot.send_message(
        message.chat.id,
        f"Платеж на сумму {message.successful_payment.total_amount // 100}",
    )
