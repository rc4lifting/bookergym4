import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import caches, config, database_functions, utils
from config import dp, bot, booking_router, logger
from bots.FBSBookerBot import FBSBookerBot
from bots.ScheduleBot import ScheduleBot

class BookingBot(StatesGroup):
    # states in booking form  
    get_booker_name = State()
    get_booking_date = State()  # Added missing state
    get_booking_time = State()  # Added missing state
    end_of_booking = State()

    # form process
    async def start_booking(message: Message, state: FSMContext):
        print("booking started!")
        await state.set_state(BookingBot.get_booker_name)
        await message.answer("What is your full name?\n (e.g. Jonan Yap)")

    @booking_router.message(get_booker_name)
    async def booker_name(message: Message, state: FSMContext):
        await state.update_data(booker_name=message.text)
        await state.set_state(BookingBot.get_booking_date)
        print("booker name collected!")
        await message.answer("Please provide the booking date (DD/MM/YYYY)")

    @booking_router.message(get_booking_date)
    async def booking_date(message: Message, state: FSMContext):
        await state.update_data(booking_date=message.text)
        await state.set_state(BookingBot.get_booking_time)
        await message.answer("Please provide the booking start time (HHMM)")

    @booking_router.message(get_booking_time)
    async def booking_time(message: Message, state: FSMContext):
        await state.update_data(booking_time=message.text)
        await state.set_state(BookingBot.end_of_booking)
        print("Booking date and time collected!")
        await BookingBot.end_booking(message, state)

    @booking_router.message(end_of_booking)
    async def end_booking(message: Message, state: FSMContext):
        print("collected all info, processing booking now")

        data = await state.get_data()
        
        booking_details = {
            "bookedUserId": message.chat.id,
            "buddyId": 1233423424,
            "buddyDetails": {
                "name": "buddy_test",
                "telehandle": "hello123",
                "roomNumber": "19-23"
            },
            "date": data['booking_date'],
            "startTime": data['booking_time'],
            "duration": 90
        }
        await state.update_data(booking_details=booking_details)

        # clear out all unnecessary data in state.data

        # storing name and room number into db logic: if inside, replace it, if not add it 
        database_functions.set_data(f"/users/{message.chat.id}/name", data['booker_name'])

        end_time_string = utils.cal_end_time(booking_details['startTime'], booking_details['duration'])
        booking_time_string = booking_details['startTime'] + " - " + end_time_string
        booking_details_string = f"Date: {booking_details['date']}\nTime: {booking_time_string}"

        # call FBSBookerBot for booking on FBS
        try: 
            new_state = await FBSBookerBot.start_web_booking(message, state)
            state = new_state
        except Exception as e:
            # this part not tested 
            print(f"Following Error has occured when automating web booking: {e}")
            await message.answer(f"An error has occurred when booking your slot:\n\n{booking_details_string}\n\nSend /exco to report the issue to us")
            await state.clear()
            
        # call Schedule for booking on FBS
        try:
            new_state = await ScheduleBot.update_schedule(message, state)
            state = new_state
        except Exception as e:
            print(f"Following Error has occured when updating schedule: {e}")
            await message.answer(f"Your booking below has been confirmed\n\n{booking_details_string}\n\n" + 
                "However, schedule has failed to update your slot. Send /exco to report the issue to us")
            await state.clear()
        else: 
            slot_id = database_functions.get_booking_counter() + 1
            ## database_functions.create_data(f"/slots/{slot_id}", booking)
        
            ## database_functions.increment_booking_counter()

            print("booking successfully processed!")
            await message.answer(f"Your booking has been successfully processed!\n\nHere are your slot details\n{booking_details_string}")
            await state.clear()




        


        