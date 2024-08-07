import asyncio

from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.error_event import ErrorEvent

import database_functions, bot_messages
from config import dp, bot, logger
from bots.BookingBot import BookingBot
from bots.CancellationBot import CancellationBot
from bots.OnboardingBot import OnboardingBot


# '/start' command 
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    logger.info("Received /start command")
    await message.answer(bot_messages.START_MESSAGE.format(message.from_user.first_name), parse_mode=ParseMode.HTML)

# '/help' command
@dp.message(Command('help'))
async def help(message: Message, state: FSMContext) -> None:
    await message.answer(bot_messages.HELP_MESSAGE, parse_mode=ParseMode.HTML)

# '/register' command
@dp.message(Command('register'))
async def register(message: Message, state: FSMContext) -> None:
    logger.info("Received /register command")
    await OnboardingBot.start_register(message, state)
    
# '/verify' command
@dp.message(Command('verify'))
async def verify(message: Message, state: FSMContext) -> None:
    await OnboardingBot.start_verify(message, state)

# '/book' command 
@dp.message(Command('book'))
async def book(message: Message, state: FSMContext):
    logger.info("Received /book command")
    if not database_functions.user_exists(message.chat.id):
        await message.answer(bot_messages.NOT_REGISTERED_MESSAGE, parse_mode=ParseMode.HTML)
        await state.clear()
    elif not database_functions.user_is_verified(message.chat.id):
        await message.answer(bot_messages.NOT_VERIFIED_MESSAGE, parse_mode=ParseMode.HTML)
        await state.clear()
    else:
        await BookingBot.start_booking(message, state)

# '/cancel' command
@dp.message(Command('cancel'))
async def cancel(message: Message, state: FSMContext):
    logger.info("Received /cancel command")
    await CancellationBot.start_cancellation(message, state)

# '/exco' command
@dp.message(Command('exco'))
async def exco(message: Message, state: FSMContext) -> None:
    await message.answer(bot_messages.EXCO_MESSAGE, parse_mode=ParseMode.HTML)

# '/schedule' command
@dp.message(Command('schedule'))
async def schedule(message: Message, state: FSMContext) -> None:
    await message.answer(bot_messages.SCHEDULE_MESSAGE, parse_mode=ParseMode.HTML)
    
# '/delete' command
@dp.message(Command('delete'))
async def delete(message: Message, state: FSMContext) -> None:
    database_functions.delete_data(f"/users/{message.chat.id}/email")
    database_functions.delete_data(f"/users/{message.chat.id}/nusnet")
    database_functions.delete_data(f"/users/{message.chat.id}/isVerified")
    await message.answer("User data deleted")
    await state.clear()


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
