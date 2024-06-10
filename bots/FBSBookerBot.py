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

from playwright.async_api import async_playwright


class FBSBookerBot(StatesGroup): 
    start_of_web_booking = State()
    automating_web_booking = State()

    # booking process
    @booking_router.message(start_of_web_booking)
    async def start_web_booking(message: Message, state: FSMContext):
        logger.info("web booking start")
        await state.set_state(FBSBookerBot.automating_web_booking)
        new_state = await FBSBookerBot.booking_slot(message, state)
        return new_state

    @booking_router.message(automating_web_booking)
    async def booking_slot(message: Message, state: FSMContext):
        # details are in state

        data = await state.get_data()
        
        async with async_playwright() as playwright:
            try: 
                logger.info("web booking is being processed")

                # connect to VPN
                # start 
                browser = await playwright.chromium.launch(headless=False, channel="chrome")
                context = await browser.new_context(http_credentials={
                    'username': utownfbs_login['username'], 
                    'password': utownfbs_login['password']
                })
                page = await context.new_page()

                logger.info("browser has been set up")

                # login to utownfbs
                await page.goto("https://utownfbs.nus.edu.sg/utown/login.aspx")
                await page.wait_for_timeout(5000)
                logger.info("logged into utownfbs")

                # select location and date range 

                
                # select date 

                # select the details 

                # select submit 
                
                # check panel Message, if error throw error

                # close + send confirmation
                
            except Exception as e:
                logger.error(f"Booking Failed due to: {e}")
                raise e
            finally:
                # TO DO: logout
                await browser.close()
                await playwright.stop()
                logger.info("web booking completed on UtownFBS")
                pass
        
        return state
    
    async def cancel_slot(message: Message, state: FSMContext):
        # go to right panel

        # find the slot with the same details 

        # click cancel -> opens new tab

        # enter cancel remarks 

        # click cancel

        # check panel Message 
        pass