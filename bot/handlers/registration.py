from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.keyboards.body_kbs import make_sizes_kb, make_sex_kb, make_body_summary, make_city_choice_kb
from bot.states import ProfileParameters
from bot.cbdata import SizeChartFactory, SexPickFactory, BodyConfirmFactory
from bot.db.orm import add_body, get_users, get_bodies

r = Router()


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
    if message.location:
        await message.answer(f'{message.location.latitude}, {message.location.longitude}')
        return
    else:
        await message.answer(f'Москва')
        return

    data = await state.get_data()

    size, age, sex = data['size'], data['age'], data['sex']

    await state.clear()

    await message.answer(f'Ваши параметры:\nРазмер: {size}\nВозраст: {age}\nПол: {sex}',
                                  reply_markup=make_body_summary(size=size, age=age, sex=sex))


@r.callback_query(BodyConfirmFactory.filter())
async def confirm_body(callback: CallbackQuery, session: AsyncSession, callback_data: BodyConfirmFactory):

    sex, size, age = callback_data.sex, callback_data.size, callback_data.age

    await add_body(session=session, tg_id=callback.message.chat.id, sex=sex, age=age, size=size)

    await callback.message.delete()
    await callback.message.answer(f"Параметры добавлены.", reply_markup=None)


# TODO: Remove
@r.message(F.text == 'check')
async def check_body(message: Message, session: AsyncSession):
    # Debug information

    user = await get_users(session, message.from_user.id)
    bodies = await get_bodies(session)

    await message.answer(f'{user}')