from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.db.models import User
from bot.keyboards.body_kbs import make_sizes_kb, make_sex_kb, make_params_sum_kb, make_city_choice_kb
from bot.keyboards.profile_kbs import make_profile_kb
from bot.states import ProfileParameters
from bot.cbdata import SizeChartFactory, SexPickFactory, ParamsConfirmFactory
from bot.db.orm import add_body, get_users, get_bodies, add_geo, get_locations

from wb.api import WildBerriesAPI
from wb.data import Coordinates

r = Router()
wb_api = WildBerriesAPI()

DEFAULT_LATITUDE = 55.86448
DEFAULT_LONGITUDE = 37.59393


def validate_age(age_string: str) -> bool:
    try:
        age = int(age_string)
        if 10 < age < 99:
            return True
        return False
    except ValueError:
        return False


@r.callback_query(F.data.in_(['input_sizes', 're_enter_body_parameters']))
async def input_sizes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileParameters.input_size)

    await callback.message.delete()
    await callback.message.answer(text="Выберите размер:", reply_markup=make_sizes_kb())


@r.callback_query(SizeChartFactory.filter(), ProfileParameters.input_size)
async def pressed_size_btn(callback: CallbackQuery, state: FSMContext, callback_data: SizeChartFactory):
    await callback.message.delete()
    await state.set_state(ProfileParameters.input_age)

    await state.update_data(size=callback_data.size)
    msg = await callback.message.answer(f'Введите свой возраст:', reply_markup=None)

    await state.update_data(msg_delete=msg.message_id)


@r.message(ProfileParameters.input_age)
async def pressed_size_btn(message: Message, state: FSMContext, bot: Bot):
    if not validate_age(message.text):
        return

    await message.delete()

    data = await state.get_data()
    msg = data['msg_delete']
    await message.bot.delete_message(message.chat.id, msg)

    await state.set_state(ProfileParameters.input_sex)
    await state.update_data(age=message.text)
    await message.answer(f'Выберите свой пол:', reply_markup=make_sex_kb())


@r.callback_query(SexPickFactory.filter(), ProfileParameters.input_sex)
async def pressed_sex_btn(callback: CallbackQuery, callback_data: SexPickFactory, state: FSMContext):

    await callback.message.delete()
    await state.update_data(sex=callback_data.gender)

    await state.set_state(ProfileParameters.input_city)
    await callback.message.answer('Вы можете отправить геолокацию \
    чтобы получать актуальные сроки доставки одежды со склада продавца до вашего города.',
                                  reply_markup=make_city_choice_kb())


@r.message(ProfileParameters.input_city)
async def get_city(message: Message, state: FSMContext):
    # TODO: Remove debug info
    # DEBUG INFORMATION
    # if message.location:
    #     await message.answer(f'{message.location.latitude}, {message.location.longitude}')
    # else:
    #     await message.answer(f'Москва')

    if message.location:
        dest_id = await wb_api.get_dist_id(Coordinates(latitude=message.location.latitude, longitude=message.location.longitude))
    else:
        dest_id = await wb_api.get_dist_id(
            Coordinates(latitude=DEFAULT_LATITUDE, longitude=DEFAULT_LONGITUDE))

    data = await state.get_data()
    size, age, sex = data['size'], data['age'], data['sex']

    await state.clear()

    await message.answer(f'Город_number: {dest_id}')

    await message.answer(f'Ваши параметры:\nРазмер: {size}\nВозраст: {age}\nПол: {sex}\n',
                                  reply_markup=make_params_sum_kb(size=size,
                                                                  age=age,
                                                                  sex=sex, dest_id=dest_id))


@r.callback_query(ParamsConfirmFactory.filter())
async def confirm_body(callback: CallbackQuery, session: AsyncSession, callback_data: ParamsConfirmFactory):

    sex, size, age = callback_data.sex, callback_data.size, callback_data.age

    await add_body(session=session, tg_id=callback.message.chat.id, sex=sex, age=age, size=size)
    await add_geo(session=session, tg_id=callback.message.chat.id, dest_id=callback_data.dest_id)
    await callback.message.delete()
    await callback.message.answer(f"Параметры добавлены.", reply_markup=make_profile_kb())


# TODO: Remove
@r.message(F.text == 'check')
async def check_body(message: Message, session: AsyncSession):
    # Debug information

    user: User = await get_users(session, message.chat.id)

    await message.answer(f'{user}, {user.geo}')