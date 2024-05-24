import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State

import caches, config, database_functions, utils, keyboard_functions
from config import dp, bot, form_router

class ScehduleBot(StatesGroup): 
    async def start_update_schedule(message: Message, state: FSMContext, booking_details: dict):
        # TO DO: update schedule