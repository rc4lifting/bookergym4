from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import cancellation_router, logger, bot, ExpectedElementNotFound
import database_functions, utils
from bots.FBSProcessBot import FBSProcessBot
from bots.ScheduleBot import ScheduleBot
from bot_messages import CANCEL_NOSLOTS_MESSAGE, BOOKING_DATETIME_STRING

from datetime import datetime
import pytz


class CancellationBot(StatesGroup):
    web_cancellation_start = State()

    async def start_cancellation(message: Message, state: FSMContext):
        logger.info("1: Cancellation started!")
        
        # get current time 
        singapore_tz = pytz.timezone('Asia/Singapore')
        curr_datetime = datetime.now(singapore_tz)

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

        await bot.send_message(message.chat.id, "Received your cancellation! Processing now...\nThis process may take up to 5 minutes")
        web_cancel_success = False

        # get utown booking id 
        utown_booking_id = database_functions.read_data(f"/slots/{slot_id}/utownfbsBookingId")
        
        if utown_booking_id == None:
            logger.info("no utownfbs id found")
        else:
            # update data in state
            cancel_slot_date = database_functions.read_data(f"/slots/{slot_id}/date")
            cancel_slot_start_time = database_functions.read_data(f"/slots/{slot_id}/startTime")
            cancel_slot_duration = database_functions.read_data(f"/slots/{slot_id}/duration")
                
            formatted_date = utils.get_formatted_date_from_string(cancel_slot_date)
            end_time_str = utils.cal_end_time(cancel_slot_start_time, cancel_slot_duration)
            
            booking_details_string = BOOKING_DATETIME_STRING.format(formatted_date, cancel_slot_start_time, end_time_str)
            
            await state.update_data({
                "cancel_utownfbs_id": utown_booking_id,
                "booking_details_string": booking_details_string,
                "cancel_slot_date": cancel_slot_date,
                "cancel_slot_start_time": cancel_slot_start_time,
                "cancel_slot_duration": cancel_slot_duration
            })
            
            # call FBSProcessBot for cancellation
            try:
                # TODO: implement cancel_slot
                print("in web cancelltation try block")
                new_state = await FBSProcessBot.cancel_slot(message, state)
                state = new_state
            except ExpectedElementNotFound as e: 
                logger.error(f"WEB CANCELLATION ExpectedElementNotFound: {e}")
                await message.answer(f"An error has occurred when cancelling your slot:\n\n{booking_details_string}\n\nSend /exco to report the issue to us")
                await state.clear()
            except Exception as e:
                logger.error(f"Cancellation Error: {e}")
                await state.clear()
                raise e
            else: 
                logger.info("WEB CANCELLATION SUCCESSFUL!")
                web_cancel_success = True
            
                # remove slot from db
                database_functions.delete_data(f"/slots/{slot_id}")
        
        if web_cancel_success:
            # call ScheduleBot to remove from sheet
            try:
                print("in remove from schedule try block")
                #new_state = await ScheduleBot.remove_from_schedule(message, state)
                #state = new_state
            except Exception as e:
                logger.error(f"Removing From Schedule Error: {e}")
                data = await state.get_data()
                await message.answer(f"Your booking below has been cancelled\n\n{data['booking_details_string']}\n\n" + 
                    "However, schedule has failed to remove your slot. Send /exco to report the issue to us")
                await state.clear()
            else:
                logger.info("ENITRE CANCELLATION SUCCESSFUL!")
                data = await state.get_data()
                await message.answer(f"The following booking has been successfully cancelled:\n\n{data['booking_details_string']}")
                await state.clear()