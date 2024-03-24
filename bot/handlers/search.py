from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from bot.keyboards import search as kb
from bot.states import SearchStates
from services.gpt import ChatGPT
from wb.api import WildBerriesAPI

router = Router()


@router.message(F.text == "/search")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(SearchStates.prompt)
    await message.answer(
        'Введи запрос для поиска, например: "Подбери образ из белой футбокли и кед"'
    )


# TODO: добавить фильтр цены и оригинальности товара
@router.message(SearchStates.prompt)
async def search_prompt(message: Message, state: FSMContext):
    prompt = message.text
    gpt = ChatGPT()
    queries = await gpt.get_search_queries(
        prompt, "мужчина"
    )  # TODO: подставить из бд пол
    print(queries)
    wb = WildBerriesAPI()
    combinations = wb.get_combinations(*[await wb.search(query) for query in queries])
    await state.set_data({"combinations": combinations, "current_index": 0})
    await message.answer("Загружаю...", reply_markup=kb.get_search_keyboard())
    await state.set_state(SearchStates.searching)
    await paginate_search(message, state)


async def paginate_search(message: Message, state: FSMContext):
    current_index = (await state.get_data()).get("current_index")
    combinations = (await state.get_data()).get("combinations")
    products = [product for product in combinations[current_index]]
    summary_price = sum([product.price for product in products])
    media_group = MediaGroupBuilder(
        caption=f"\n".join([product.name for product in products])
        + f"\n\n<b>Общая цена: {summary_price}₽</b>"
    )
    for product in products:
        media_group.add(type="photo", media=URLInputFile(product.image_url))

    await message.answer_media_group(media=media_group.build())


@router.message(F.text == "👎", SearchStates.searching)
async def next_paginate(message: Message, state: FSMContext):
    await state.update_data(
        {"current_index": (await state.get_data()).get("current_index", 0) + 1}
    )
    await paginate_search(message, state)


@router.message(F.text == "👍", SearchStates.searching)
async def next_paginate(message: Message, state: FSMContext):
    current_index = (await state.get_data()).get("current_index")
    combinations = (await state.get_data()).get("combinations")
    await message.answer(
        f"\n".join(
            *[
                f"<a href='https://www.wildberries.ru/catalog/{product.id}/detail.aspx'>{product.name}</a>: {product.id}"
                for product in combinations[current_index]
            ]
        )
    )
    # await paginate_search(message, state)
