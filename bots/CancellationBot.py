from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from config import cancellation_router, logger
import database_functions, utils, bot_messages
from bots.FBSProcessBot import FBSProcessBot
from bots.ScheduleBot import ScheduleBot
from bot_messages import CANCEL_NOSLOTS_MESSAGE, BOOKING_DATETIME_STRING

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
        # TODO: implement get_slots_after_time
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
        slot_id = callback_query.data
        message = callback_query.message

        # get utown booking id 
        utown_booking_id = 'B00858407'
        #database_functions.read_data(f"/slots/{slot_id}/utownfbsBookingId")
        
        if utown_booking_id == None:
            logger.info("no utownfbs id found")
        else:
            await state.update_data({
                "cancel_utownfbs_id": utown_booking_id
            })

            # call FBSProcessBot for cancellation
            try:
                # TODO: implement cancel_slot
                new_state = await FBSProcessBot.cancel_slot(message, state)
                state = new_state
            except Exception as e:
                logger.error(f"Cancellation Error: {e}")
                raise e
                await state.clear()
        
        # update data in state
        await state.update_data({
            "cancel_slot_date": database_functions.read_data(f"/slots/{slot_id}/date"),
            "cancel_slot_start_time": database_functions.read_data(f"/slots/{slot_id}/startTime"),
            "cancel_slot_duration": database_functions.read_data(f"/slots/{slot_id}/duration"),
        })

        # remove slot from db
        #database_functions.delete_data(f"/slots/{slot_id}")

        # call ScheduleBot to remove from sheet
        try:
            new_state = await ScheduleBot.remove_from_schedule(message, state)
        except Exception as e:
            logger.error(f"Removing From Schedule Error: {e}")
            await state.clear()

        data = await state.get_data()
        formatted_date = utils.get_formatted_date_from_string(data['cancel_slot_date'])
        end_time_str = utils.cal_end_time(data['cancel_slot_start_time'], data['cancel_slot_duration'])

        await message.answer(f"The following booking has been cancelled:\n\n{BOOKING_DATETIME_STRING.format(formatted_date, data['cancel_slot_start_time'], end_time_str)}")
        await state.clear()