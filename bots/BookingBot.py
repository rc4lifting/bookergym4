import logging
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import booking_router
import database_functions, utils
from bots.FBSBookerBot import FBSBookerBot
from bots.ScheduleBot import ScheduleBot

logger = logging.getLogger(__name__)

class BookingBot(StatesGroup):
    # states in booking form  
    get_booker_name = State()
    get_room_number = State()
    get_buddy_name = State()
    get_buddy_room_number = State()
    get_buddy_telegram_handle = State()
    get_booking_date = State()
    get_booking_time_range = State()
    get_booking_start_time = State()
    get_booking_duration = State()
    end_of_booking = State()

    # form process
    async def start_booking(message: Message, state: FSMContext):
        logger.info("Booking started!")
        await state.set_state(BookingBot.get_booker_name)
        await message.answer("What is your full name?\n (e.g. Jonan Yap)")

    @booking_router.message(get_booker_name)
    async def booker_name(message: Message, state: FSMContext):
        logger.info("Collecting booker name")
        await state.update_data(booker_name=message.text)
        await state.set_state(BookingBot.get_room_number)
        await message.answer("What's your room number? (e.g. 14-12A)")

    @booking_router.message(get_room_number)
    async def room_number(message: Message, state: FSMContext):
        logger.info("Collecting room number")
        await state.update_data(room_number=message.text)
        await state.set_state(BookingBot.get_buddy_name)
        await message.answer("What is your buddy's full name? (e.g. Tan Yong Jun)")

    @booking_router.message(get_buddy_name)
    async def buddy_name(message: Message, state: FSMContext):
        logger.info("Collecting buddy's name")
        await state.update_data(buddy_name=message.text)
        await state.set_state(BookingBot.get_buddy_room_number)
        await message.answer("What's your buddy's room number? (e.g. 17-16)")

    @booking_router.message(get_buddy_room_number)
    async def buddy_room_number(message: Message, state: FSMContext):
        logger.info("Collecting buddy's room number")
        await state.update_data(buddy_room_number=message.text)
        await state.set_state(BookingBot.get_buddy_telegram_handle)
        await message.answer("What is your buddy's telegram handle?")

    @booking_router.message(get_buddy_telegram_handle)
    async def buddy_telegram_handle(message: Message, state: FSMContext):
        logger.info("Collecting buddy's telegram handle")
        await state.update_data(buddy_telegram_handle=message.text)
        await state.set_state(BookingBot.get_booking_date)
        await message.answer("Please select the booking date:", reply_markup=utils.create_inline(
            {"03 June 2024": "03/06/2024", "04 June 2024": "04/06/2024", "05 June 2024": "05/06/2024", "06 June 2024": "06/06/2024", "07 June 2024": "07/06/2024", "08 June 2024": "08/06/2024", "09 June 2024": "09/06/2024", "10 June 2024": "10/06/2024"}, row_width=2))


    @booking_router.callback_query(get_booking_date)
    async def booking_date_callback(callback_query: CallbackQuery, state: FSMContext):
        await state.update_data(booking_date=callback_query.data)
        await state.set_state(BookingBot.get_booking_time_range)
        await callback_query.message.answer("Please select the time range of your booking:", reply_markup=utils.create_inline(
            {"0000 - 0530": "0000-0530", "0600 - 1130": "0600-1130", "1200 - 1730": "1200-1730", "1800 - 2330": "1800-2330"}, row_width=2))

    @booking_router.callback_query(get_booking_time_range)
    async def booking_time_range_callback(callback_query: CallbackQuery, state: FSMContext):
        await state.update_data(booking_time_range=callback_query.data)
        await state.set_state(BookingBot.get_booking_start_time)
        await callback_query.message.answer("Please select the start time of your booking:", reply_markup=utils.create_inline(
            {"1200": "1200", "1230": "1230", "1300": "1300", "1330": "1330", "1400": "1400", "1430": "1430", "1500": "1500", "1530": "1530"}, row_width=4))

    @booking_router.callback_query(get_booking_start_time)
    async def booking_start_time_callback(callback_query: CallbackQuery, state: FSMContext):
        await state.update_data(booking_start_time=callback_query.data)
        await state.set_state(BookingBot.get_booking_duration)
        await callback_query.message.answer("Select the duration of your booking:", reply_markup=utils.create_inline(
            {"1 hour": "60", "1 hour 30 mins": "90"}, row_width=2))

    @booking_router.callback_query(get_booking_duration)
    async def booking_duration_callback(callback_query: CallbackQuery, state: FSMContext):
        await state.update_data(booking_duration=callback_query.data)
        await state.set_state(BookingBot.end_of_booking)
        await BookingBot.end_booking(callback_query.message, state)

    async def end_booking(message: Message, state: FSMContext):
        logger.info("Collected all info, processing booking now")

        data = await state.get_data()
        logger.debug(f"Booking data: {data}")

        booking_details = {
            "bookedUserId": message.chat.id,
            "buddyId": 1233423424,  # Assuming a fixed ID or this should be dynamically set
            "buddyDetails": {
                "name": data.get('buddy_name', ''),
                "telehandle": data.get('buddy_telegram_handle', ''),
                "roomNumber": data.get('buddy_room_number', '')
            },
            "date": data.get('booking_date', ''),
            "startTime": data.get('booking_start_time', ''),
            "duration": int(data.get('booking_duration', 90))
        }
        await state.update_data(booking_details=booking_details)

        # Debug log to show where the data is placed
        logger.debug(f"Buddy details: {booking_details['buddyDetails']}")

        # Storing name and room number into db logic: if inside, replace it, if not add it 
        database_functions.set_data(f"/users/{message.chat.id}/name", data.get('booker_name', ''))

        end_time_string = utils.cal_end_time(booking_details['startTime'], booking_details['duration'])
        booking_time_string = booking_details['startTime'] + " - " + end_time_string
        booking_details_string = f"Date: {booking_details['date']}\nTime: {booking_time_string}"

        # Call FBSBookerBot for booking on FBS
        try: 
            new_state = await FBSBookerBot.start_web_booking(message, state)
            state = new_state
        except Exception as e:
            logger.error(f"Following Error has occurred when automating web booking: {e}")
            await message.answer(f"An error has occurred when booking your slot:\n\n{booking_details_string}\n\nSend /exco to report the issue to us")
            await state.clear()
            
        # Call Schedule for booking on FBS
        try:
            new_state = await ScheduleBot.update_schedule(message, state)
            state = new_state
        except Exception as e:
            logger.error(f"Following Error has occurred when updating schedule: {e}")
            await message.answer(f"Your booking below has been confirmed\n\n{booking_details_string}\n\n" + 
                "However, schedule has failed to update your slot. Send /exco to report the issue to us")
            await state.clear()
        else: 
            slot_id = database_functions.get_booking_counter() + 1
            logger.info("Booking successfully processed!")
            await message.answer(f"Your booking has been successfully processed!\n\nHere are your slot details\n{booking_details_string}")
            await state.clear()

# Register message handlers
booking_router.message(BookingBot.get_booker_name)(BookingBot.booker_name)
booking_router.message(BookingBot.get_room_number)(BookingBot.room_number)
booking_router.message(BookingBot.get_buddy_name)(BookingBot.buddy_name)
booking_router.message(BookingBot.get_buddy_room_number)(BookingBot.buddy_room_number)
booking_router.message(BookingBot.get_buddy_telegram_handle)(BookingBot.buddy_telegram_handle)
booking_router.callback_query(BookingBot.get_booking_date)(BookingBot.booking_date_callback)
booking_router.callback_query(BookingBot.get_booking_time_range)(BookingBot.booking_time_range_callback)
booking_router.callback_query(BookingBot.get_booking_start_time)(BookingBot.booking_start_time_callback)
booking_router.callback_query(BookingBot.get_booking_duration)(BookingBot.booking_duration_callback)
booking_router.message(BookingBot.end_of_booking)(BookingBot.end_booking)





