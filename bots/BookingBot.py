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
    end_of_booking = State()

    # form process
    async def start_booking(message: Message, state: FSMContext):
        await state.set_state(BookingBot.end_of_booking)
        await message.answer("booking start")

    # TO DO: booking flow in this class
    # data all in state.data

    # restrict start time on sundays until 2300 and only allow 1h

    @booking_router.message(end_of_booking)
    async def end_booking(message: Message, state: FSMContext):
        await message.answer("booking is being processed")

        # sample data
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

        # call FBSBookerBot for booking on FBS
        await FBSBookerBot.start_web_booking(message, state)
        # error thrown by FBSBookerBot will stop this function
        # error thrown by ScheduleBot will not stop function, but output smth

        # update databases
        slot_id = database_functions.get_booking_counter() + 1

        path = f"/slots/{slot_id}"
        database_functions.create_data(path, booking)

        # TO DO: check + update/ add booking user's room number and name 
        
        # increment counter
        database_functions.increment_booking_counter()

        await message.answer("Your booking has been successfully processed.")

        