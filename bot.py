# main bot file 

import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import caches, config, database_functions, utils
from config import dp, bot, form_router
from bots.BookingBot import BookingBot


# '/start' command 
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    #TO DO 
    await message.answer("hello user")

# '/book' command 
@dp.message(Command('book'))
async def book(message: Message, state: FSMContext):
    await BookingBot.start_booking(message, state)
    

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())