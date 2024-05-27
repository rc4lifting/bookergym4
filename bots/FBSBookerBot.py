import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import caches, config, database_functions, utils
from config import dp, bot, booking_router, logger
from bots.ScheduleBot import ScheduleBot

class FBSBookerBot(StatesGroup): 
    start_of_web_booking = State()
    end_of_web_booking = State()

    @booking_router.message(start_of_web_booking)
    async def start_web_booking(message: Message, state: FSMContext):
        print("web booking start")
        await state.set_state(FBSBookerBot.end_of_web_booking)
        await FBSBookerBot.end_web_booking(message, state)

    # Check if booking overlaps, 
    
    # TO DO: booking on FBS portal
    @booking_router.message(end_of_web_booking)
    async def end_web_booking(message: Message, state: FSMContext):
        print("web booking is being processed")
        await state.set_state(ScheduleBot.add_to_schedule)
        await ScheduleBot.update_schedule(message, state)
        print("web booking ended")
        
        