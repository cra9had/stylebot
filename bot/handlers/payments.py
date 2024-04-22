import datetime
import os.path

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import LabeledPrice
from aiogram.types import Message
from aiogram.types import PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.cbdata import SubTariffFactory
from bot.db.constants import Subscriptions
from bot.db.models import Subscription
from bot.db.orm import create_subscription
from bot.db.orm import create_transaction
from bot.db.orm import get_subscriptions
from bot.db.orm import get_transactions
from bot.db.orm import get_user_subscription
from bot.db.orm import SUBSCRIPTION_VITALITY
from bot.keyboards.payment_kbs import get_one_tarif_kb
from bot.keyboards.payment_kbs import get_payment_main_menu_kb
from bot.keyboards.payment_kbs import get_subscription_keyboard
from bot.keyboards.payment_kbs import get_tariffs_kb
from bot.keyboards.search_kbs import return_to_menu_kb

router = Router()


async def no_free_searches_left(message: Message, is_subscribed: bool):
    if not is_subscribed:
        await message.answer(
            "Бесплатные комбинации закончились. Приобретите подписку.",
            reply_markup=get_subscription_keyboard(),
        )
    else:
        await message.answer(
            "Комбинации на сегодня закончились. Возращайся завтра.",
            reply_markup=return_to_menu_kb(),
        )


@router.callback_query(F.data == "go_payment_menu")
async def get_subs(callback: CallbackQuery, session: AsyncSession):
    await callback.message.delete()
    user_sub: Subscription = await get_user_subscription(
        session, callback.message.chat.id
    )
    if user_sub:
        msg_text = "Ваша подписка: "
        sub_name = user_sub.transaction.transaction_type
        msg_text += f"🎟<b>{sub_name.upper()}</b>\n"
        if sub_name != Subscriptions.unlimited.value["name"]:
            msg_text += f'Вам доступно <b>{getattr(Subscriptions, sub_name).value["likes_quantity"]}</b>🔄 ежедневных образов!\n'
        else:
            msg_text += (
                f"Вам доступно <b>безлимитное количество</b> ежедневных образов!\n"
            )

        msg_text += f"Подписка действует до {datetime.datetime.fromtimestamp(user_sub.transaction.date_payment) + datetime.timedelta(seconds=SUBSCRIPTION_VITALITY)}"

    else:
        msg_text = "У вас пока нет подписок.\nЧтобы её получить, нажмите на 🛒<b>Купить подписку</b>"

    await callback.message.answer(
        text=msg_text, reply_markup=get_payment_main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "go_buy_menu")
async def get_buy_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    files = (await state.get_data()).get("files", {})
    await state.clear()
    await state.update_data(files=files)
    await callback.message.answer(
        """🛒<b>Магазин подписок</b>\n\nНажмите на подписку, чтобы узнать о ней подробнее""",
        reply_markup=get_tariffs_kb(),
    )
    await callback.answer()


@router.callback_query(SubTariffFactory.filter())
async def print_tariff_info(
    callback: CallbackQuery, callback_data: SubTariffFactory, state: FSMContext
):
    # files = (await state.get_data()).get("files", {})
    # if not files or callback_data.name not in files:
    #     tariff_photo = FSInputFile(
    #         path=os.path.join("bot", "data", f"{callback_data.name}.png")
    #     )
    #     tariff_message = await callback.message.answer_photo(photo=tariff_photo)
    #     files.update({callback_data.name: tariff_message.photo[-1].file_id})
    #     await state.update_data(files=files)
    # elif callback_data.name in files:
    #     tariff_photo_id = files.get(callback_data.name)
    #     await callback.message.answer_photo(photo=tariff_photo_id)

    if callback_data.name != Subscriptions.unlimited.value["name"]:
        msg_text = (
            f"Подписка ✨<b>{callback_data.name.upper()}</b>✨\n\nДО <b>{callback_data.likes_quantity}</b>🔄 разнообразных комбинаций одежды "
            f"в день\n💳Цена: <b>{callback_data.price} р.</b>"
        )
    else:
        msg_text = (
            f"С <b>БЕЗЛИМИТНОЙ ПОДПИСКОЙ</b> ты можешь перестать считать образы. У тебя сняты все лимиты за день!"
            f"\nВсего за {callback_data.price} р."
        )

    await state.update_data(
        {
            "product_title": callback_data.name,
            "product_price": callback_data.price,
            "product_likes": callback_data.likes_quantity,
        }
    )

    await callback.message.answer(msg_text, reply_markup=get_one_tarif_kb())
    await callback.answer()


@router.callback_query(F.data == "buy_sub_menu")
async def send_payment_invoice(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    await callback.message.bot.send_invoice(
        callback.message.chat.id,
        title=f"Тариф {data['product_title'].upper()}",
        description=f"Месячная подписка на {data['product_likes']} луков в день",
        provider_token=os.getenv("YOOKASSA_TOKEN"),
        currency="rub",
        photo_url="https://yoursticker.ru/wp-content/uploads/2021/12/wildberries.jpg",
        photo_width=800,
        photo_height=600,
        is_flexible=False,
        prices=[
            LabeledPrice(
                label="Подписка на 1 месяц", amount=data["product_price"] * 100
            )
        ],
        start_parameter="one-month-subscription",
        payload=f"{data['product_title']}",
    )

    trx_id = await create_transaction(
        session=session,
        transaction_type=data["product_title"],
        tg_id=callback.message.chat.id,
    )
    await state.update_data(trx_id=trx_id)
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@router.message(F.successful_payment)
async def successful_payment(
    message: Message, session: AsyncSession, state: FSMContext
):
    await create_subscription(
        session, (await state.get_data()).get("trx_id"), message.chat.id
    )

    await message.bot.send_message(
        message.chat.id,
        f"Спасибо за покупку! Подписка уже активна.",
    )
