import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import caches, config, database_functions, utils
from caches import utownfbs_login
from config import dp, bot, booking_router, logger
from bots.ScheduleBot import ScheduleBot

class FBSBookerBot(StatesGroup): 
    start_of_web_booking = State()
    automating_web_booking = State()
    end_of_web_booking = State()

    # booking process
    @booking_router.message(start_of_web_booking)
    async def start_web_booking(message: Message, state: FSMContext):
        print("web booking start")
        await state.set_state(FBSBookerBot.automating_web_booking)
        await FBSBookerBot.booking_slot(message, state)

    @booking_router.message(automating_web_booking)
    async def booking_slot(message: Message, state: FSMContext):
        print("web booking is being processed")
        # details are in state

        data = await state.get_data()
        
        try: 
            # TO DO: selenium automation
            pass
        except Exception as e:
            print(f"Booking Failed due to: {e}")
        finally:
            # TO DO: close browser
            pass
        
        await state.set_state(FBSBookerBot.end_of_web_booking)
        await FBSBookerBot.end_web_booking(message, state)

    
    # TO DO: booking on FBS portal
    @booking_router.message(end_of_web_booking)
    async def end_web_booking(message: Message, state: FSMContext):
        print("web booking completed on UtownFBS, updaing schedule now")
        await state.set_state(ScheduleBot.add_to_schedule)
        try:
            await ScheduleBot.update_schedule(message, state)
        except Exception as e:
            print(f"Following Error has occured when updating schedule: {e}")
            state.clear()
        else:
            print("web booking successfully processed!")
    

    # helper functions 
    async def select_and_set_element():
        # handles selecting of element, output if it is found or not 
        pass
        