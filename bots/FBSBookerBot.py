import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import caches, config, database_functions, utils
from config import dp, bot, form_router, logger

class FBSBookerBot(StatesGroup): 
    async def start_web_booking(message: Message, state: FSMContext, booking_details: dict):
        
        # TO DO: booking on FBS portal
        pass