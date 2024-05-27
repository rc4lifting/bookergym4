import asyncio
import logging
import sys
from os import getenv
import caches

from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# logger
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=caches.api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# for booking form route
booking_router = Router() 
dp.include_router(booking_router)





