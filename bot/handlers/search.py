import asyncio
import dataclasses
import json
import logging
from typing import List

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import SearchSettings
from bot.db.orm import add_favourite_item
from bot.db.orm import add_settings
from bot.db.orm import get_bodies
from bot.db.orm import get_settings
from bot.db.orm import get_users
from bot.keyboards import search_kbs as kb
from bot.keyboards.search_kbs import get_product_keyboard
from bot.keyboards.search_kbs import get_search_keyboard
from bot.keyboards.search_kbs import return_to_menu_kb
from bot.keyboards.search_kbs import start_search_kb
from bot.states import AdjustSettings
from bot.states import SearchStates
from bot.utils.user_search_counter import search_counter
from services.gpt import BadClothesException
from services.gpt import ChatGPT
from wb.api import WildBerriesAPI
from wb.data import Filters
from wb.data import Product

router = Router()


@dataclasses.dataclass
class PinnedProduct:
    product: Product
    index: int

    def to_json(self):
        return dataclasses.asdict(self)


@router.callback_query(F.data.in_(["go_search_menu"]))
async def start_search(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.delete()
    await state.set_state(AdjustSettings.adjust_min_price)
    await callback.message.answer("Введи минимальную цену за весь образ (в рублях)")

    await callback.answer()


@router.callback_query(F.data.in_(["start_search_clothes", "restart_search_clothes"]))
async def start_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(SearchStates.prompt)
    await callback.message.answer(
        'Введи запрос для поиска, например: "<code>Подбери образ из белой футболки и кед</code>"',
        reply_markup=None,
    )
    await callback.answer()


@router.message(AdjustSettings.adjust_min_price)
async def get_min_price(message: Message, state: FSMContext):
    try:
        min_price = int(message.text)
        await state.update_data(min_price=min_price)
        await message.answer("Отлично. Теперь введи максимальную.")
        await state.set_state(AdjustSettings.adjust_max_price)
    except ValueError:
        await message.answer("Неправильно введённая цена. Введи ещё раз.")
        return


@router.message(AdjustSettings.adjust_max_price)
async def get_max_price(message: Message, state: FSMContext, session: AsyncSession):
    try:
        max_price = int(message.text)
        min_price = (await state.get_data()).get("min_price", 0)
        if min_price > max_price:
            await message.answer(
                "MAX⬆️ цена <b>должна быть больше</b>, чем MIN⬇️.\n\nЧтобы всё заработало, введи минимальную заново:",
                reply_markup=return_to_menu_kb()
            )

            await state.clear()
            await state.set_state(AdjustSettings.adjust_min_price)
            return

        await state.update_data(max_price=max_price)
        await state.set_state(AdjustSettings.adjust_is_original)
        await message.answer(
            "Формируем комбинации только из оригинальных вещей?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Да ✅", callback_data="original_yes"
                        ),
                        InlineKeyboardButton(
                            text="Нет ❌", callback_data="original_no"
                        ),
                    ]
                ]
            ),
        )
    except ValueError:
        await message.answer("Неправильно введённая цена. Введи ещё раз.")
        return


@router.callback_query(
    F.data.startswith("original_"), AdjustSettings.adjust_is_original
)
async def change_is_original(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    data = await state.get_data()

    await callback.message.delete()

    await callback.message.answer(
        "Настройки поиска сохранены.", reply_markup=start_search_kb()
    )

    await add_settings(
        session=session,
        tg_id=callback.message.chat.id,
        min_price=data["min_price"],
        max_price=data["max_price"],
        is_original=1 if callback.data == "original_yes" else 0,
    )

    await state.clear()
    await callback.answer()


@router.message(SearchStates.prompt)
async def search_prompt(
    message: Message, state: FSMContext, redis: Redis, session: AsyncSession
):
    body = await get_bodies(session, message.chat.id)

    prompt = message.text
    gpt = ChatGPT()
    temp_msg = await message.answer("Жду ответа от WildBerrries👀")

    try:
        queries = await gpt.get_search_queries(prompt, body.sex)
        print(f"{queries=}")

    except BadClothesException as e:
        await message.answer(
            'Введите запрос, начинающийся с "<code>Подбери мне образ</code>" и содержащий в себе как минимум <b>два</b> элемента одежды.'
        )
        return

    if not queries:
        await message.answer(
            'Наш бот не совсем понял, что тебе нужно. Начни свой запрос с "<code>Подбери мне образ</code>" и содержащий в себе одежду. '
        )
        return

    settings: SearchSettings = await get_settings(session, message.chat.id)
    wb = WildBerriesAPI()
    combinations = wb.get_combinations(
        *[
            await wb.search(query, filters=Filters(is_original=settings.is_original))
            for query in queries
        ],
        min_price=settings.min_price,
        max_price=settings.max_price,
    )
    await state.set_data(
        {"combinations": combinations, "current_index": 0, "pinned_products": []}
    )
    await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())
    await temp_msg.delete()
    await state.set_state(SearchStates.searching)
    await paginate_search(message, state, redis)


async def _get_current_products(state: FSMContext) -> List[Product]:
    combination = await _get_products(state)
    pinned = await _get_pinned_products(state)
    for product in pinned:
        combination[product.index] = Product(**product.product)
    print(combination)
    return combination


async def _pin_product_by_id(state: FSMContext, product_id: int, index: int) -> None:
    products = await _get_products(state)
    product = [
        PinnedProduct(product=product, index=index)
        for product in products
        if product.id == product_id
    ][0]
    await state.update_data(
        pinned_products=[
            *(await state.get_data()).get("pinned_products"),
            product.to_json(),
        ]
    )


async def _unpin_product_by_id(state: FSMContext, product_id: int) -> None:
    products = (await state.get_data()).get("pinned_products")
    await state.update_data(
        pinned_products=[
            product
            for product in products
            if product.get("product").get("id") != product_id
        ]
    )


async def _get_pinned_products(state: FSMContext):
    products = (await state.get_data()).get("pinned_products")
    return [PinnedProduct(**product) for product in products]


async def _get_pinned_products_id(state: FSMContext) -> List[int]:
    products = (await state.get_data()).get("pinned_products")
    return [product.get("product").get("id") for product in products]


async def _get_products(state: FSMContext) -> List[Product]:
    current_index = (await state.get_data()).get("current_index")
    combinations = (await state.get_data()).get("combinations")
    return [Product(**product) for product in combinations[current_index]]


async def paginate_search(message: Message, state: FSMContext, redis: Redis):
    try:
        products = await _get_current_products(state)
        summary_price = sum([product.price for product in products])
        media_group = MediaGroupBuilder(
            caption=f"\n".join([product.name for product in products])
            + f"\n\n<b>Общая цена: {summary_price}₽</b>"
        )

        for product in products:
            media_group.add(type="photo", media=URLInputFile(product.image_url))
        await message.answer_media_group(media=media_group.build())

    except IndexError:
        curr_ind = (await state.get_data()).get('current_index', 0)
        if not curr_ind:
            text = "С такими ценами собрать комбо с Wildberries не получится ;("
        else:
            text = "Комбинаций больше нет."

        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Вернуться в меню")]],
                resize_keyboard=True,
            ),
        )


@router.callback_query(F.data == "back_to_search")
async def back_to_search(
    call: CallbackQuery, state: FSMContext, redis: Redis, session: AsyncSession
):
    await call.message.delete()
    await next_paginate(call.message, state, redis, session)


@router.message(F.text.in_(["🔍Продолжить поиск", "👉"]), SearchStates.searching)
@search_counter
async def next_paginate(
    message: Message, state: FSMContext, redis: Redis, session: AsyncSession
):
    if message.text == "🔍Продолжить поиск":
        await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())
    await state.update_data(
        {"current_index": (await state.get_data()).get("current_index", 0) + 1}
    )
    await paginate_search(message, state, redis)


@router.message(F.text.in_(["👈"]), SearchStates.searching)
async def prev_paginate(message: Message, state: FSMContext, redis: Redis):
    if message.text == "🔍Продолжить поиск":
        await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())

    if (await state.get_data()).get("current_index", 0) == 0:
        return

    await state.update_data(
        {"current_index": (await state.get_data()).get("current_index", 0) - 1}
    )
    await paginate_search(message, state, redis)


@router.message(F.text == "Закрепить элемент")
async def pin_element(message: Message, state: FSMContext):
    products = await _get_current_products(state)
    text = "Выбери элементы одежды которые нужно закрепить:\n"
    for i, product in enumerate(products):
        text += f"{i + 1}. {product.name}\n"
    print(f"{products=}")
    await message.answer(
        text,
        reply_markup=kb.get_pin_keyboard(
            products, await _get_pinned_products_id(state)
        ),
    )


@router.callback_query(F.data.startswith("pin-product/"))
async def element_pin_switcher(call: CallbackQuery, state: FSMContext):
    all_products = await _get_current_products(state)
    products_id = await _get_pinned_products_id(state)
    product_id = int(call.data.replace("pin-product/", ""))
    print(products_id, product_id)
    if product_id in products_id:
        await _unpin_product_by_id(state, product_id)
    else:
        await _pin_product_by_id(
            state,
            product_id,
            [product.id for product in all_products].index(product_id),
        )
    await call.message.delete()
    await pin_element(call.message, state)


@router.message(F.text == "Показать артикулы", SearchStates.searching)
async def show_products_id_handler(
    message: Message, state: FSMContext, session: AsyncSession
):
    products = await _get_current_products(state)
    for product in products:
        await add_favourite_item(session, tg_id=message.chat.id, product=product)

    answer = "Артикулы:\n" + f"\n".join(
        [
            f"<a href='https://www.wildberries.ru/catalog/{product.id}/detail.aspx'>{product.name}</a>: "
            f"<code>{product.id}</code>"
            for product in products
        ]
    )
    await message.answer(answer, reply_markup=get_product_keyboard())
