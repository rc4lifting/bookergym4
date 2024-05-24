import asyncio
import logging
import sys
from os import getenv
import caches

from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=caches.api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
form_router = Router()
dp.include_router(form_router)