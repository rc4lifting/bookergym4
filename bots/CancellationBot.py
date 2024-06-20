from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from config import booking_router, logger
import database_functions, utils, bot_messages
from bots.FBSBookerBot import FBSBookerBot
from bots.ScheduleBot import ScheduleBot

class CancellationBot(StatesGroup):
    async def start_cancellation(message: Message, state: FSMContext):
        logger.info("1: Cancellation started!")
        await state.clear()
        await message.answer("you will be able to cancel slots soon")