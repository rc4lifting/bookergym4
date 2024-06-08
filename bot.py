import asyncio
import logging
import sys
from os import getenv

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types.error_event import ErrorEvent

import caches, config, database_functions, utils, bot_messages
from config import dp, bot, booking_router, logger
from bots.BookingBot import BookingBot

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# '/start' command 
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    logger.info("Received /start command")
    user = message.from_user
    telehandle = user.username

    path = f"/users/{message.chat.id}"
    if not database_functions.user_exists(message.chat.id):
        data = {
            "telehandle": f"{telehandle}",
        }
        database_functions.create_data(path, data)
        
    await message.answer(bot_messages.START_MESSAGE.format(user.first_name), parse_mode=ParseMode.HTML)

# '/help' command
@dp.message(Command('help'))
async def help(message: Message) -> None:
    await message.answer(bot_messages.HELP_MESSAGE, parse_mode=ParseMode.HTML)

# '/book' command 
@dp.message(Command('book'))
async def book(message: Message, state: FSMContext):
    logger.info("Received /book command")
    await BookingBot.start_booking(message, state)

# '/exco' command
@dp.message(Command('exco'))
async def exco(message: Message) -> None:
    await message.answer(bot_messages.EXCO_MESSAGE,parse_mode=ParseMode.HTML)

# '/schedule' command
@dp.message(Command('schedule'))
async def schedule(message: Message) -> None:
    await message.answer(bot_messages.SCHEDULE_MESSAGE,parse_mode=ParseMode.HTML)

# TODO: fix global error handling
@dp.error()
async def global_error_handler(event: ErrorEvent):
    logger.error(f"caught unexpected error in global handler: {event.exception}")
    
    if event.update.message:
        chat_id = event.update.message.chat.id
    elif event.update.callback_query:
        chat_id = event.update.callback_query.message.chat.id

    if chat_id:
        await bot.send_message(chat_id, "unexpected message occurred, send /exco to notify us about the issue")

    return True
    
async def main() -> None:
    logger.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())







