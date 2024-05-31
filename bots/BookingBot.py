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

class BookingBot(StatesGroup):
    # states in booking form  
    get_booker_name = State()
    end_of_booking = State()

    # form process
    async def start_booking(message: Message, state: FSMContext):
        print("booking started!")
        await state.set_state(BookingBot.get_booker_name)
        await message.answer("What is your full name?\n (e.g. Jonan Yap)")

    @booking_router.message(get_booker_name)
    async def booker_name(message: Message, state: FSMContext):
        await state.update_data(booker_name=message.text)
        await state.set_state(BookingBot.end_of_booking) 
        print("booker name collected!")
        await BookingBot.end_booking(message, state)

    # TO DO: booking flow in this class
    # data all in state.data

#hamziadded
     @booking_router.message(get_booking_time)

    async def booking_time(message: Message, state: FSMContext):

        await state.update_data(booking_time=message.text)

        await state.set_state(BookingBot.end_of_booking)

        print("Booking date and time collected!")

        await BookingBot.end_booking(message, state)

#hamziadded
    @booking_router.message(get_booking_date)

    async def booking_date(message: Message, state: FSMContext):

        await state.update_data(booking_date=message.text)

        await state.set_state(BookingBot.get_booking_time)

        await message.answer("Please provide the booking start time (HHMM)

    # restrict start time on sundays until 2300 and only allow 1h

    @booking_router.message(end_of_booking)
    async def end_booking(message: Message, state: FSMContext):
        await message.answer("booking is being processed")
        print("collected all info, processing booking now")

        # sample data - ideally this is alr in data['booking_details']
        booking = {
            "bookedUserId": message.chat.id,
            "buddyId": 1233423424,
            "buddyDetails": {
                "name": "buddy_test",
                "telehandle": "hello123",
                "roomNumber": "19-23"
            },
            "date": "02/06/2024",
            "startTime": "2330",
            "duration": 60
        }
        await state.update_data(booking_details=booking)

        data = await state.get_data()

        # storing name and room number into db logic: if inside, replace it, if not add it 
        database_functions.set_data(f"/users/{message.chat.id}/name", data['booker_name'])

        # call FBSBookerBot for booking on FBS
        try: 
            await FBSBookerBot.start_web_booking(message, state)
        except Exception as e:
            print(f"Following Error has occured when automating web booking: {e}")

        # error thrown by FBSBookerBot will stop this function
        # error thrown by ScheduleBot will not stop function, but output smth

        slot_id = database_functions.get_booking_counter() + 1
        ## database_functions.create_data(f"/slots/{slot_id}", booking)
        
        ## database_functions.increment_booking_counter()

        print("booking successfully processed!")
        await message.answer("Your booking has been successfully processed.")




        


        