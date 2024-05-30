import asyncio
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

# '/start' command 
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    path = f"/users/{message.chat.id}"
    if database_functions.user_exists(message.chat.id) == False:
        data = {
            "telehandle": f"{user.username}",
        }
        database_functions.create_data(path, data)
        
    await message.answer(
            text=f"Hello, <b>{user.first_name}</b>! Send /book to start booking now",
            parse_mode=ParseMode.HTML
        )


# '/book' command 
@dp.message(Command('book'))
async def book(message: Message, state: FSMContext):
    await BookingBot.start_booking(message, state)

# global error handling
@dp.error()
async def global_error_handler(event: ErrorEvent):
    print(f"caught unexpected error in global handler: {event.exception}")
    if event.update.message:
        await event.update.message.answer("unexpected message occured, send /exco to notify us about the issue")
    return True
    
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())