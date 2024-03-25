from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove


async def remove_reply_keyboard(bot: Bot, chat_id: int):
    msg_text: str = r"_It is not the message you are looking for\.\.\._"

    msg = await bot.send_message(chat_id=chat_id,
                                 text=msg_text,
                                 reply_markup=ReplyKeyboardRemove(),
                                 parse_mode="MarkdownV2")
    await msg.delete()