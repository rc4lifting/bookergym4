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
from bots.CancellationBot import CancellationBot
from bots.FBSProcessBot import FBSProcessBot

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

# '/cancel' command
@dp.message(Command('cancel'))
async def cancel(message: Message, state: FSMContext):
    logger.info("Received /cancel command")
    await CancellationBot.start_cancellation(message, state)

# '/exco' command
@dp.message(Command('exco'))
async def exco(message: Message, state: FSMContext) -> None:
    await message.answer(bot_messages.EXCO_MESSAGE,parse_mode=ParseMode.HTML)

# '/schedule' command
@dp.message(Command('schedule'))
async def schedule(message: Message, state: FSMContext) -> None:
    await message.answer(bot_messages.SCHEDULE_MESSAGE,parse_mode=ParseMode.HTML)

# # '/web' command: use for testing web automation, delete when all done 
# @dp.message(Command('web'))
# async def web(message: Message, state: FSMContext) -> None:
#     await state.set_state(FBSProcessBot.start_of_web_booking)
#     await bot.send_message(message.chat.id, "Starting web booking process")
#     await state.update_data(
#         booker_name='Benjamin Seow',
#         telehandle='benjaminseowww',
#         booker_room_number= '17-16',
#         buddy_name= 'test',
#         buddy_room_number='04-23',
#         buddy_telegram_handle='abc',
#         booking_date='28/06/2024',
#         booking_time_range='1200-1730',
#         booking_start_time='1600',
#         booking_duration='60'
#     )
#     await FBSProcessBot.start_web_booking(message, state)

# global error handling, for unexpected errors
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







