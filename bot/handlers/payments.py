import os.path

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import LabeledPrice
from aiogram.types import Message
from aiogram.types import PreCheckoutQuery

from bot.cbdata import SubTariffFactory
from bot.keyboards.payment_kbs import get_subscription_keyboard, get_payment_main_menu_kb, get_tariffs_kb

router = Router()


async def no_free_searches_left(message: Message):
    await message.answer(
        "Бесплатные комбинации закончились. Приобретите подписку.",
        reply_markup=get_subscription_keyboard(),
    )


@router.callback_query(F.data == 'go_payment_menu')
async def get_subs(callback: CallbackQuery):
    await callback.message.delete()
    user_subs = []
    if user_subs:
        msg_text = '🎟Ваши подписки:\n'
        for sub in user_subs:
            msg_text += f'- {sub}\n'
    else:
        msg_text = 'У вас пока нет подписок.\nЧтобы её получить, нажмите на 🛒<b>Купить подписку</b>'
    await callback.message.answer(text=msg_text,
                                  reply_markup=get_payment_main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == 'go_buy_menu')
async def get_buy_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        """🛒<b>Магазин подписок</b>\n\nНажмите на подписку, чтобы узнать о ней подробнее""",
        reply_markup=get_tariffs_kb()
    )
    await callback.answer()


@router.callback_query(SubTariffFactory.filter())
async def print_tariff_info(callback: CallbackQuery, callback_data: SubTariffFactory, state: FSMContext):

    files = (await state.get_data()).get('files', {})
    if not files or callback_data.name not in files:
        tariff_photo = FSInputFile(path=os.path.join('bot', 'data', f'{callback_data.name}.png'))
        tariff_message = await callback.message.answer_photo(photo=tariff_photo)
        files.update({callback_data.name: tariff_message.photo[-1].file_id})
        await state.update_data(files=files)
    elif callback_data.name in files:
        tariff_photo_id = files.get(callback_data.name)
        await callback.message.answer_photo(photo=tariff_photo_id)

    await callback.message.answer(f"Подписка позволит тебе получать до {callback_data.likes_quantity} комбинаций одежды "
                                  f"в день всего за {callback_data.price} р.")
    await callback.answer()


@router.message(F.text == "/pay")
async def send_payment_invoice(message: Message):
    await message.bot.send_invoice(
        message.chat.id,
        title="Подписка на бота",
        description="Активация подписки на бота на 1 месяц",
        provider_token="381764678:TEST:82262",  # TODO: to .env
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
