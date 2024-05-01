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

from bot.cbdata import SubTariffFactory, CheckPaymentFactory
from bot.db.constants import Subscriptions
from bot.db.models import Subscription
from bot.db.orm import create_subscription
from bot.db.orm import create_transaction
from bot.db.orm import get_subscriptions
from bot.db.orm import get_transactions
from bot.db.orm import get_user_subscription
from bot.db.orm import SUBSCRIPTION_VITALITY
from bot.keyboards.payment_kbs import get_one_tarif_kb, get_payment_kb
from bot.keyboards.payment_kbs import get_payment_main_menu_kb
from bot.keyboards.payment_kbs import get_subscription_keyboard
from bot.keyboards.payment_kbs import get_tariffs_kb
from bot.keyboards.search_kbs import return_to_menu_kb
from bot.utils.yookassa import create_payment, check_payment

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
    product_title = f"Пакет: {data['product_likes']} ЛАЙКОВ"
    product_price = data['product_price']
    url, payment_id = create_payment(product_title, product_price, os.getenv("BOT_TG_URL"))
    print(url, payment_id)
    trx_id = await create_transaction(
         session=session,
         transaction_type=data["product_title"],
         tg_id=callback.message.chat.id,
     )
    await callback.message.answer(
        "Данные к оплате", reply_markup=get_payment_kb(url, payment_id)
    )
    await state.update_data(trx_id=trx_id)
    await callback.answer()


@router.callback_query(CheckPaymentFactory.filter())
async def check_transaction(callback: CallbackQuery, session: AsyncSession, state: FSMContext,
                            callback_data: CheckPaymentFactory):
    if check_payment(callback_data.payment_id):
        await callback.answer("Платёж успешен")
        await create_subscription(
            session=session, trx_id=(await state.get_data()).get("trx_id"), user_id=callback.message.chat.id
        )
        await callback.message.delete()
        await callback.message.answer("Спасибо за покупку! Подписка уже активна.")

    else:
        await callback.answer("Платёж пока не завершён.")
