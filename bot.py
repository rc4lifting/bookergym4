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

import caches, config, database_functions, utils
from config import dp, bot, booking_router, logger
from bots.BookingBot import BookingBot

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# '/start' command 
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    path = f"/users/{message.chat.id}"
    if not database_functions.user_exists(message.chat.id):
        data = {
            "telehandle": f"{user.username}",
        }
        database_functions.create_data(path, data)
        
    await message.answer(
            text=(
                f"Hello, <b>{user.first_name}</b>!\n\n"
                "What can this bot do?\n"
                "Use this bot to book a slot at the RC4 gym!\n"
                "/book - book your gym slot now!\n"
                "/cancel - cancel slots to free them up for others :)\n\n"
                "/register - register your email before booking\n"
                "/verify - verify email for authentication\n"
                "/delete - delete your account and data\n\n"
                "/schedule - view available time slots here\n"
                "/history - view your slots for the week\n\n"
                "/exco - contact the exco on any queries, feedback and damages"
            ),
            parse_mode=ParseMode.HTML
        )

# '/book' command 
@dp.message(Command('book'))
async def book(message: Message, state: FSMContext):
    logger.info("Received /book command")
    await BookingBot.start_booking(message, state)

# '/exco' command
@dp.message(Command('exco'))
async def exco(message: Message) -> None:
    await message.answer(
        text=(
            "These exco will be happy to help!\n"
            "Ben - @benjaminseowww\n"
            "Jedi - @JediKoh\n"
            "Hamzi - @zzimha\n"
            "Justin - @jooostwtk"
        ),
        parse_mode=ParseMode.HTML
    )

# global error handling
@dp.error()
async def global_error_handler(event: ErrorEvent):
    logger.error(f"caught unexpected error in global handler: {event.exception}")
    if event.update.message:
        await event.update.message.answer("unexpected message occurred, send /exco to notify us about the issue")
    return True
    
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())






