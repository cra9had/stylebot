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
from aiogram.types import Message
from aiogram.types import URLInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import SearchSettings
from bot.db.orm import add_favourite_item, add_settings, get_bodies, get_settings, get_users
from bot.keyboards import search_kbs as kb
from bot.keyboards.search_kbs import get_product_keyboard, get_search_keyboard, return_to_menu_kb, start_search_kb
from bot.states import SearchStates, AdjustSettings
from services.gpt import ChatGPT, BadClothesException
from wb.api import WildBerriesAPI
from wb.data import Product

router = Router()


@router.callback_query(F.data.in_(["go_search_menu"]))
async def start_search(
        callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.delete()
    await state.set_state(AdjustSettings.adjust_min_price)
    await callback.message.answer(
        "Введи минимальную цену за весь образ (в рублях)"
    )

    await callback.answer()


@router.callback_query(F.data.in_(["start_search_clothes", "restart_search_clothes"]))
async def start_search(
        callback: CallbackQuery, state: FSMContext
):
    await callback.message.delete()
    await state.set_state(SearchStates.prompt)
    await callback.message.answer(
         'Введи запрос для поиска, например: <b>"Подбери образ из белой футболки и кед"</b>',
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
        await state.update_data(max_price=max_price)
        min_price = (await state.get_data()).get('min_price', 0)
        if min_price > max_price:
            await message.answer("Максимальная цена должна быть больше, чем минимальная. Начнём ещё раз?", reply_markup=return_to_menu_kb())
            await message.answer("Если хочешь попробовать снова, введи минимальную цену за весь образ (в рублях)")
            await state.set_state(AdjustSettings.adjust_min_price)
        await message.answer("Настройки поиска сохранены.", reply_markup=start_search_kb())
        await add_settings(session=session, tg_id=message.chat.id, min_price=min_price, max_price=max_price)
        await state.set_state(AdjustSettings.adjust_max_price)
    except ValueError:
        await message.answer("Неправильно введённая цена. Введи ещё раз.")
        return




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
        await message.answer("Введите запрос, начинающийся с <b>\"Подбери мне образ\"</b> и содержащий в себе одежду.")
        return

    if not queries:
        await message.answer(
            "Наш бот не совсем понял, что тебе нужно. Начни свой запрос с <b>\"Подбери мне образ\"</b> и содержащий в себе одежду. ")
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
        await message.answer("Комбинаций больше нет.",
                             reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вернуться в меню')]], resize_keyboard=True))


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
    await message.answer(answer, reply_markup=get_product_keyboard())



