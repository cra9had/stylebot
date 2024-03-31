import asyncio
import dataclasses
import json
import logging

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods.answer_callback_query import AnswerCallbackQuery
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.constants import DEFAULT_MAX_PRICE
from bot.db.constants import DEFAULT_MIN_PRICE
from bot.db.models import Body
from bot.db.models import SearchSettings
from bot.db.orm import add_favourite_item
from bot.db.orm import add_settings
from bot.db.orm import get_bodies
from bot.db.orm import get_settings
from bot.db.orm import get_users
from bot.keyboards import search_kbs as kb
from bot.keyboards.search_kbs import get_price_kb
from bot.keyboards.search_kbs import get_product_keyboard
from bot.keyboards.search_kbs import get_search_keyboard
from bot.states import AdjustSettings
from bot.states import SearchStates
from services.gpt import BadClothesException
from services.gpt import ChatGPT
from wb.api import WildBerriesAPI
from wb.data import Product

router = Router()


@router.callback_query(F.data.in_(["start_search_clothes", "restart_search_clothes"]))
async def start_search(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.delete()
    await state.set_state(SearchStates.prompt)
    settings = await get_settings(session, callback.message.chat.id)
    await callback.message.answer(
        'Введи запрос для поиска, например: <b>"Подбери образ из белой футболки и кед"</b>\n\nА ниже ты можешь отфильтровать цены образов, которые я буду выдавать.',
        reply_markup=get_price_kb(settings.min_price, settings.max_price),
    )
    await callback.answer()


@router.message(SearchStates.prompt)
async def search_prompt(message: Message, state: FSMContext, session: AsyncSession):
    body = await get_bodies(session, message.chat.id)

    prompt = message.text
    gpt = ChatGPT()
    temp_msg = await message.answer("Жду ответа от WildBerrries👀")

    try:
        queries = await gpt.get_search_queries(prompt, body.sex)
        print(f"{queries=}")

    except BadClothesException as e:
        await message.answer(
            'Введите запрос, начинающийся с <b>"Подбери мне образ"</b> и содержащий в себе одежду.'
        )
        return

    if not queries:
        await message.answer(
            'Наш бот не совсем понял, что тебе нужно. Начни свой запрос с <b>"Подбери мне образ"</b> и содержащий в себе одежду. '
        )
        return

    settings: SearchSettings = await get_settings(session, message.chat.id)

    wb = WildBerriesAPI()
    combinations = wb.get_combinations(
        *[await wb.search(query) for query in queries],
        min_price=settings.min_price,
        max_price=settings.max_price,
    )
    await state.set_data({"combinations": combinations, "current_index": 0})
    await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())
    await temp_msg.delete()
    await state.set_state(SearchStates.searching)
    await paginate_search(message, state)


async def paginate_search(message: Message, state: FSMContext):
    current_index = (await state.get_data()).get("current_index")
    combinations = (await state.get_data()).get("combinations")
    try:
        products = [Product(**product) for product in combinations[current_index]]
        summary_price = sum([product.price for product in products])
        media_group = MediaGroupBuilder(
            caption=f"\n".join([product.name for product in products])
            + f"\n\n<b>Общая цена: {summary_price}₽</b>"
        )
        for product in products:
            media_group.add(type="photo", media=URLInputFile(product.image_url))
        await message.answer_media_group(media=media_group.build())

    except IndexError:
        await message.answer(
            "Комбинаций больше нет.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Вернуться в меню")]],
                resize_keyboard=True,
            ),
        )


@router.message(
    F.text.in_(["🔍Продолжить поиск", "Следующая комбинация"]), SearchStates.searching
)
async def next_paginate(message: Message, state: FSMContext):
    if message.text == "🔍Продолжить поиск":
        await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())
    await state.update_data(
        {"current_index": (await state.get_data()).get("current_index", 0) + 1}
    )
    await paginate_search(message, state)


@router.message(F.text.in_(["Предыдущая комбинация"]), SearchStates.searching)
async def prev_paginate(message: Message, state: FSMContext):
    if message.text == "🔍Продолжить поиск":
        await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())

    if (await state.get_data()).get("current_index", 0) == 0:
        return

    await state.update_data(
        {"current_index": (await state.get_data()).get("current_index", 0) - 1}
    )
    await paginate_search(message, state)


@router.message(F.text == "👍", SearchStates.searching)
async def next_paginate(message: Message, state: FSMContext, session: AsyncSession):
    current_index = (await state.get_data()).get("current_index")
    combinations = (await state.get_data()).get("combinations")
    products = [Product(**product) for product in combinations[current_index]]
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


@router.callback_query(F.data == "change_min_price")
async def change_min_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(AdjustSettings.adjust_min_price)
    del_msg = await callback.message.answer(
        "Введите значение минимальной цены (в рублях) для следующих образов одежды:"
    )
    await state.update_data(del_msg=del_msg.message_id)
    await callback.answer()


@router.callback_query(F.data == "change_max_price")
async def change_max_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(AdjustSettings.adjust_max_price)
    del_msg = await callback.message.answer(
        "Введите значение максимальной цены (в рублях) для следующих образов одежды:"
    )
    await state.update_data(del_msg=del_msg.message_id)
    await callback.answer()


@router.message(AdjustSettings.adjust_min_price)
async def set_min_price(message: Message, state: FSMContext, session: AsyncSession):
    new_min_price = message.text
    data = await state.get_data()
    del_msg_id = data["del_msg"]

    settings = await get_settings(session, message.chat.id)
    try:
        if settings.max_price > int(new_min_price):
            await message.bot.delete_message(message.chat.id, del_msg_id)
            await add_settings(session, message.chat.id, min_price=new_min_price)

            to_delete = await message.answer("Новое значение записано.")
            await asyncio.sleep(1)
            await to_delete.delete()
            await message.answer(
                "Теперь вы можете вернуться к поиску",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Вернуться к поиску",
                                callback_data="restart_search_clothes",
                            )
                        ]
                    ]
                ),
            )
    except ValueError:
        return


@router.message(AdjustSettings.adjust_max_price)
async def set_max_price(message: Message, state: FSMContext, session: AsyncSession):
    new_max_price = message.text
    data = await state.get_data()
    del_msg_id = data["del_msg"]

    settings = await get_settings(session, message.chat.id)
    try:
        if settings.min_price < int(new_max_price):
            await message.bot.delete_message(message.chat.id, del_msg_id)
            await add_settings(session, message.chat.id, max_price=new_max_price)

            to_delete = await message.answer("Новое значение записано.")
            await asyncio.sleep(1)
            await to_delete.delete()
            await message.answer(
                "Теперь вы можете вернуться к поиску",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Вернуться к поиску",
                                callback_data="restart_search_clothes",
                            )
                        ]
                    ]
                ),
            )
    except ValueError:
        return


@router.callback_query(F.data == "reset_price")
async def reset_price(callback: CallbackQuery, session: AsyncSession):
    await add_settings(
        session,
        callback.message.chat.id,
        min_price=DEFAULT_MIN_PRICE,
        max_price=DEFAULT_MAX_PRICE,
    )

    await callback.message.delete()
    await callback.message.answer(
        "Настройки цен сброшены.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Вернуться к поиску",
                        callback_data="restart_search_clothes",
                    )
                ]
            ]
        ),
    )
    await callback.answer()
