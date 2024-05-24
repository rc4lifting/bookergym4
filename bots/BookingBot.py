import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State

import caches, config, database_functions, utils, keyboard_functions
from config import dp, bot, form_router
from bots.FBSBookerBot import FBSBookerBot
from bots.ScehduleBot import ScehduleBot

class BookingBot(StatesGroup): 
    end_of_booking = State()

    async def start_booking(message: Message, state: FSMContext):
        await state.set_state(BookingBot.end_of_booking)
        await message.answer("test")

    # TO DO: booking flow in this class
    # data all in state.data

    @form_router.message(end_of_booking)
    async def end_booking(message: Message, state: FSMContext):
        example_booking = {}

        # update database 
        

        # call ScehduleBot for google sheets 
        await ScehduleBot.start_update_schedule(message, state, example_booking)

        # call FBSBookerBot for booking on FBS
        await FBSBookerBot.start_web_booking(message, state, example_booking)