from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from config import bot, booking_router, logger, SlotTakenException
import database_functions, utils, bot_messages
from bots.FBSBookerBot import FBSBookerBot
from bots.ScheduleBot import ScheduleBot

class BookingBot(StatesGroup):
    # states in booking form  
    get_booker_name = State()
    get_room_number = State()
    check_room_number = State()
    get_buddy_name = State()
    get_buddy_room_number = State()
    check_buddy_room_number = State()
    get_buddy_telegram_handle = State()
    get_booking_date = State()
    get_booking_time_range = State()
    get_booking_start_time = State()
    get_booking_duration = State()
    confirm_booking_details = State()
    confirm_declaration = State()
    end_of_booking = State()

    # TODO: checking of responses validity

    ## form process
    async def start_booking(message: Message, state: FSMContext):
        logger.info("1: Booking started!")
        await state.set_state(BookingBot.get_booker_name)
        await message.answer("What is your full name?\n (e.g. Jonan Yap)")

    @booking_router.message(get_booker_name)
    async def booker_name(message: Message, state: FSMContext):
        logger.info("2: Booker Name Received!")
        await state.update_data(booker_name=message.text)
        await state.update_data(telehandle=message.from_user.username)
        await state.set_state(BookingBot.get_room_number)
        await message.answer("What's your room number? (e.g. 14-12A)")

    @booking_router.message(get_room_number)
    async def room_number(message: Message, state: FSMContext):
        logger.info("3: Booker Room Number Received!")
        await state.update_data(booker_room_number=message.text)
        await state.set_state(BookingBot.check_room_number)
        await BookingBot.room_number_checking(message, state)

    @booking_router.message(check_room_number)
    async def room_number_checking(message: Message, state: FSMContext):
        if utils.is_valid_room_number(message.text):
            logger.info("4: Booker Room Number Checked!")
            await state.update_data(booker_room_number=message.text)
            await state.set_state(BookingBot.get_buddy_name)
            await message.answer("What is your buddy's full name? (e.g. Tan Yong Jun)")
        else:
            logger.info("Invalid Booker Room Number!")
            await message.answer("Room Number not valid, please re-enter your room number: (e.g. 14-12A)")

    @booking_router.message(get_buddy_name)
    async def buddy_name(message: Message, state: FSMContext):
        logger.info("5: Buddy Name Received")
        await state.update_data(buddy_name=message.text)
        await state.set_state(BookingBot.get_buddy_room_number)
        await message.answer("What's your buddy's room number? (e.g. 17-16)")


    @booking_router.message(get_buddy_room_number)
    async def buddy_room_number(message: Message, state: FSMContext):
        logger.info("6: Buddy Room Number Received")
        await state.update_data(buddy_room_number=message.text)
        await state.set_state(BookingBot.check_buddy_room_number)
        await BookingBot.buddy_room_number_checking(message, state)
    
    @booking_router.message(check_buddy_room_number)
    async def buddy_room_number_checking(message: Message, state: FSMContext):
        if utils.is_valid_room_number(message.text):
            logger.info("7: Buddy Room Number Checked")
            await state.update_data(buddy_room_number=message.text)
            await state.set_state(BookingBot.get_buddy_telegram_handle)
            await message.answer("What is your buddy's telegram handle? (w/o the @ symbol)")
        else:
            logger.info("Invalid Buddy Room Number!")
            await message.answer("Room Number not valid, please re-enter your room number: (e.g. 14-12A)")
    
    # TODO: apply 1-8 days logic here 
    @booking_router.message(get_buddy_telegram_handle)
    async def buddy_telegram_handle(message: Message, state: FSMContext):
        logger.info("8: Buddy Telehandle Received")
        telehandle = message.text

        if telehandle.startswith("@"):
            telehandle = telehandle[1:]

        await state.update_data(buddy_telegram_handle=telehandle)
        await state.set_state(BookingBot.get_booking_date)
        await message.answer("Please select the booking date:", reply_markup=utils.create_inline(
            {
                "21 June 2024": "21/06/2024", 
                "22 June 2024": "22/06/2024", 
                "23 June 2024": "23/06/2024"
                #"24 June 2024": "06/06/2024", 
                #"25 June 2024": "07/06/2024", 
                #"26 June 2024": "08/06/2024", 
                #"27 June 2024": "09/06/2024", 
                #"10 June 2024": "10/06/2024"
            }, row_width=2))

    # TODO: apply time logic here 
    @booking_router.callback_query(get_booking_date)
    async def booking_date_callback(callback_query: CallbackQuery, state: FSMContext):
        logger.info("9: Received Booking Date")
        await state.update_data(booking_date=callback_query.data)
        await state.set_state(BookingBot.get_booking_time_range)
        await callback_query.message.answer(
                "Please select the time range of your booking start time:", 
                reply_markup=utils.create_inline({"0000 - 0530": "0000-0530", "0600 - 1130": "0600-1130", "1200 - 1730": "1200-1730", "1800 - 2330": "1800-2330"}, row_width=2)
            )

    @booking_router.callback_query(get_booking_time_range)
    async def booking_time_range_callback(callback_query: CallbackQuery, state: FSMContext):
        logger.info("10: Received Booking Time Range")
        await state.update_data(booking_time_range=callback_query.data)
        range_extremes = callback_query.data.split("-")

        await state.set_state(BookingBot.get_booking_start_time)
        await callback_query.message.answer(
                "Please select the start time of your booking:", 
                reply_markup=utils.create_start_time_keyboard(range_extremes[0], range_extremes[1], 30)
            )

    @booking_router.callback_query(get_booking_start_time)
    async def booking_start_time_callback(callback_query: CallbackQuery, state: FSMContext):
        logger.info("11: Received Booking Start Time")
        await state.update_data(booking_start_time=callback_query.data)
        await state.set_state(BookingBot.get_booking_duration)
        await callback_query.message.answer("Select the duration of your booking:", reply_markup=utils.create_inline(
            {"1 hour": "60", "1 hour 30 mins": "90"}, row_width=2))

    @booking_router.callback_query(get_booking_duration)
    async def booking_duration_callback(callback_query: CallbackQuery, state: FSMContext):
        logger.info("12: Received Booking Duration")
        await state.update_data(booking_duration=callback_query.data)
        await state.set_state(BookingBot.confirm_booking_details)
        await BookingBot.booking_details_confirmation(callback_query.message, state)

    #confirmation of booking details
    @booking_router.message(confirm_booking_details)
    async def booking_details_confirmation(message: Message, state: FSMContext):
        data = await state.get_data()

        booking_user_details_string = bot_messages.BOOKING_USER_DETAILS_STRING.format(
            data['booker_name'], data['telehandle'], data['booker_room_number'],
            data['buddy_name'], data['buddy_telegram_handle'], data['buddy_room_number']
        )

        end_time_string = utils.cal_end_time(data['booking_start_time'], data['booking_duration'])
        booking_date_string = utils.get_formatted_date_from_string(data['booking_date'])
        booking_datetime_string = bot_messages.BOOKING_DATETIME_STRING.format(booking_date_string, data['booking_start_time'], end_time_string)
        await state.set_state(BookingBot.confirm_declaration)
        await message.answer(
            text=(
                f"<b>Booking Confirmation</b>\n"
                f"{booking_user_details_string}\n\n"
                f"{booking_datetime_string}\n\n"
                "If booking details are correct, please confirm below, otherwise, press /book to restart the booking process."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=utils.create_inline({"Confirm": "Confirm"}, row_width=1)
        )
    
    #declaration 
    @booking_router.callback_query(confirm_declaration)
    async def declaration_confirmation(callback_query: CallbackQuery, state: FSMContext):
        logger.info("14: User confirmed w all info correct!")
        await state.set_state(BookingBot.end_of_booking)
        await callback_query.message.answer(
            text=(
                f"<b>Declaration</b>\n"
                f"{bot_messages.FORM_DECLARATION}"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=utils.create_inline({"Read and Declared": "Declared"}, row_width=1)
        )

    @booking_router.callback_query(end_of_booking)
    async def end_booking(callback_query: CallbackQuery, state: FSMContext):
        logger.info("15: Declared and Ready to Book")

        message = callback_query.message
        await bot.send_message(message.chat.id, "Received your booking! Processing now...")
        data = await state.get_data()

        # TODO: add buddyid if buddy exists in db
        # Storing name and room number into db logic: if inside, replace it, if not add it 
        #database_functions.set_data(f"/users/{message.chat.id}/name", data.get('booker_name', ''))
        #database_functions.set_data(f"/users/{message.chat.id}/roomNumber", data.get('booker_room_number', ''))

        # updating booking details
        booking_details = {
            "bookedUserId": message.chat.id,
            "buddyId": None,  
            "buddyDetails": {
                "name": data.get('buddy_name', ''),
                "telehandle": data.get('buddy_telegram_handle', ''),
                "roomNumber": data.get('buddy_room_number', '')
            },
            "date": data.get('booking_date', ''),
            "startTime": data.get('booking_start_time', ''),
            "duration": int(data.get('booking_duration', 90))
        }

        end_time_string = utils.cal_end_time(booking_details['startTime'], booking_details['duration'])
        booking_date_string = utils.get_formatted_date_from_string(booking_details['date'])
        booking_details_string = bot_messages.BOOKING_DATETIME_STRING.format(booking_date_string, booking_details['startTime'], end_time_string)

        web_booking_success = False

        # Call FBSBookerBot for booking on FBS
        try: 
            #new_state = await FBSBookerBot.start_web_booking(message, state)
            #state = new_state
            print("in web booking try block")
        except SlotTakenException as e: 
            logger.error(f"WEB BOOKING SlotTakenException: {e}")
            await message.answer(f"{e}\n\n{booking_details_string}\n\nSend /book to book another slot")
            await state.clear()
        except Exception as e:
            logger.error(f"WEB BOOKING ERROR: {e}")
            await message.answer(f"An error has occurred when booking your slot:\n\n{booking_details_string}\n\nSend /exco to report the issue to us")
            await state.clear()
        else:
            logger.info("WEB BOOKING SUCCESSFUL!")
            web_booking_success = True
            data = await state.get_data()
            booking_details["utownfbsBookingId"] = data.get('utownfbsBookingId')
            database_functions.create_data(f"/slots", booking_details, True)
            
        # Call Schedule for booking on FBS
        if web_booking_success:
            try:
                #new_state = await ScheduleBot.update_schedule(message, state)
                #state = new_state
                print("in scheduling try block")
            except Exception as e:
                logger.error(f"Update Schedule Error: {e}")
                await message.answer(f"Your booking below has been confirmed\n\n{booking_details_string}\n\n" + 
                    "However, schedule has failed to update your slot. Send /exco to report the issue to us")
                await state.clear()
            else: 
                logger.info("ENITRE BOOKING SUCCESSFUL!")
                await message.answer(f"Your booking has been successfully processed!\n\nHere are your slot details\n{booking_details_string}\n\nSend /schedule to view the updated schedule")
                await state.clear()