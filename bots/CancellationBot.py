from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from config import cancellation_router, logger
import database_functions, utils, bot_messages
from bots.FBSProcessBot import FBSProcessBot
from bots.ScheduleBot import ScheduleBot
from bot_messages import CANCEL_NOSLOTS_MESSAGE

from playwright.async_api import async_playwright, expect
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


class CancellationBot(StatesGroup):
    web_cancellation_start = State()

    async def start_cancellation(message: Message, state: FSMContext):
        logger.info("1: Cancellation started!")
        await state.clear()

        # get current time 
        curr_datetime = datetime.now(ZoneInfo("Asia/Singapore"))

        # query database on slots after the current time, in format of {"display string": "slot_id", ...}
        slots = database_functions.get_slots_after_time(curr_datetime, message.chat.id)

        # display slots to user
        if len(slots) == 0:
            await message.answer(CANCEL_NOSLOTS_MESSAGE)
            await state.clear()
        else:
            keyboard_dict = {}
            for slot_id, slot_info in slots.items():
                formatted_date = utils.get_formatted_date_from_string(slot_info['date'])
                end_time_str = utils.cal_end_time(slot_info['startTime'], slot_info['duration'])
                booking_option_str = f"{formatted_date} {slot_info['startTime']} - {end_time_str}"
                keyboard_dict[booking_option_str] = slot_id
            await state.set_state(CancellationBot.web_cancellation_start)
            await message.answer("Which slot would you like to cancel?", reply_markup=utils.create_inline(keyboard_dict))

    @cancellation_router.callback_query(web_cancellation_start)
    async def cancel_slot(callback_query: CallbackQuery, state: FSMContext):
        logger.info("2: Slot Selected")
        print(callback_query.data)

        # get utown booking id 

        # call FBSProcessBot for cancellation

        # remove slot from db

        # call ScheduleBot to remove from sheet

        await callback_query.message.answer("Slot cancelled!")
        await state.clear()