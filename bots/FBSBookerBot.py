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

class FBSBookerBot(StatesGroup): 
    start_of_web_booking = State()
    automating_web_booking = State()

    # booking process
    @booking_router.message(start_of_web_booking)
    async def start_web_booking(message: Message, state: FSMContext):
        print("web booking start")
        await state.set_state(FBSBookerBot.automating_web_booking)
        new_state = await FBSBookerBot.booking_slot(message, state)
        return new_state

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
            raise e
        finally:
            # TO DO: close browser
            print("web booking completed on UtownFBS")
            pass
        
        return state
    

    # helper functions 
    async def select_and_set_element():
        # handles selecting of element, output if it is found or not 
        pass
        