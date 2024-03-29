import dataclasses
import json
import logging

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.orm import add_favourite_item
from bot.db.orm import get_users
from bot.keyboards import search_kbs as kb
from bot.keyboards.search_kbs import get_search_keyboard
from bot.states import SearchStates
from services.gpt import ChatGPT
from wb.api import WildBerriesAPI
from wb.data import Product

router = Router()


@router.callback_query(F.data == "start_search_clothes")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(SearchStates.prompt)
    await callback.message.answer(
        'Введи запрос для поиска, например: "Подбери образ из белой футбокли и кед"'
    )
    await callback.answer()


# TODO: добавить фильтр цены и оригинальности товара
@router.message(SearchStates.prompt)
async def search_prompt(message: Message, state: FSMContext, session: AsyncSession):
    prompt = message.text
    gpt = ChatGPT()
    user = await get_users(session=session, tg_id=message.chat.id)
    await message.answer("Жду ответа от WildBerrries👀")
    queries = await gpt.get_search_queries(prompt, user.body.sex)
    wb = WildBerriesAPI()
    combinations = wb.get_combinations(*[await wb.search(query) for query in queries])
    await state.set_data({"combinations": combinations, "current_index": 0})
    await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())
    await state.set_state(SearchStates.searching)
    await paginate_search(message, state)


async def paginate_search(message: Message, state: FSMContext):
    current_index = (await state.get_data()).get("current_index")
    combinations = (await state.get_data()).get("combinations")
    products = [Product(**product) for product in combinations[current_index]]
    summary_price = sum([product.price for product in products])
    media_group = MediaGroupBuilder(
        caption=f"\n".join([product.name for product in products])
        + f"\n\n<b>Общая цена: {summary_price}₽</b>"
    )
    for product in products:
        media_group.add(type="photo", media=URLInputFile(product.image_url))

    await message.answer_media_group(media=media_group.build())


@router.message(F.text.in_(["🔍Продолжить поиск", "Следующая комбинация"]), SearchStates.searching)
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
    await message.answer(answer, reply_markup=get_search_keyboard())
