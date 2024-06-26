import asyncio
import logging
import sys
from os import getenv

from datetime import datetime, timedelta
import pytz
import re

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import caches, config, database_functions, utils
from caches import utownfbs_login
from config import dp, bot, booking_router, logger, SlotTakenException, ExpectedElementNotFound, InvalidBookingTimeException
from bot_messages import DEFAULT_CANCEL_REMARK

from playwright.async_api import async_playwright, expect

class FBSProcessBot(StatesGroup): 
    start_of_web_booking = State()
    automating_web_booking = State()

    ## booking process
    @booking_router.message(start_of_web_booking)
    async def start_web_booking(message: Message, state: FSMContext):
        logger.info("web booking start")
        await state.set_state(FBSProcessBot.automating_web_booking)
        new_state = await FBSProcessBot.booking_slot(message, state)
        return new_state

    @booking_router.message(automating_web_booking)
    async def booking_slot(message: Message, state: FSMContext):
        data = await state.get_data()

        singapore_tz = pytz.timezone('Asia/Singapore')

        # parse data needed for web booking
        booker_name = data['booker_name'] 
        date_obj = datetime.strptime(data['booking_date'], "%d/%m/%Y")
        booking_date = date_obj.strftime('%d-%b-%Y')
        div_avail_date = date_obj.strftime('%m/%d/%Y')
        duration = data['booking_duration']

        # the  1800/01/01 is the date used in the portal's options
        real_start_time_datetime = datetime.strptime(booking_date + " " + data['booking_start_time'], "%d-%b-%Y %H%M").replace(tzinfo=singapore_tz)
        option_start_time_datetime = datetime.strptime("1800/01/01 " + data['booking_start_time'], "%Y/%m/%d %H%M").replace(tzinfo=singapore_tz)
        start_time = option_start_time_datetime.strftime("%Y/%m/%d %H:%M:%S")
        option_end_time_datetime = (option_start_time_datetime + timedelta(minutes=int(duration))).replace(tzinfo=singapore_tz)
        end_time = option_end_time_datetime.strftime("%Y/%m/%d %H:%M:%S")

        # TODO: nusnet id from verification - coded later 

        # TODO: check time here, send resp message if invalid 
        now = datetime.now(singapore_tz)
        if now + timedelta(minutes=30)> real_start_time_datetime:
            raise InvalidBookingTimeException("Caught before booking - Booking time is invalid")

        async with async_playwright() as playwright:
            try: 
                logger.info("booking - web booking has started")

                ## start 
                browser = await playwright.chromium.launch(headless=True, channel="chrome")
                # context = await browser.new_context(http_credentials={
                #     'username': utownfbs_login['username'], 
                #     'password': utownfbs_login['password']
                # })
                # page = await context.new_page()
                page = await browser.new_page()
                logger.info("booking - browser has been set up")

                ## login to utownfbs
                await page.goto("https://utownfbs.nus.edu.sg/utown/loginpage.aspx")
                await page.locator('span[id="StudentLoginButton"]').click()
                await page.wait_for_timeout(10000)

                await page.locator('input[id="userNameInput"]').fill(utownfbs_login['username'])
                await page.locator('input[id="passwordInput"]').fill(utownfbs_login['password'])
                await page.locator('span[id="submitButton"]').click()
                await page.wait_for_timeout(10000)

                logger.info("booking - logged into utownfbs")

                ## select location and date range 
                frame = page.frame(url='https://utownfbs.nus.edu.sg/utown/modules/booking/search.aspx')

                if not frame:
                    raise ExpectedElementNotFound("Frame not found")

                await frame.wait_for_load_state()

                await frame.locator('select[name="FacilityType$ctl02"]').select_option(value="b0b1df78-0e74-4b3c-8033-ced5e3e32413")

                await frame.locator('select[name="Facility$ctl02"]').select_option(value="32ecb2ef-0600-44b9-97b0-dbf2a1c2bfab")

                # Date Range: Very Unrealiable
                # change event may or may not happen because of changing it programmically

                start_input_locator = frame.locator('input[name="StartDate$ctl03"]')
                start_date_script = """ 
                (date) => {
                    const input = document.querySelector('input[name="StartDate$ctl03"]');
                    input.setAttribute('value', date);
                }
                """
                await frame.evaluate(start_date_script, booking_date)
                await frame.wait_for_timeout(1000)

                # frame loading after onchange in start date element is unreliable
                await frame.wait_for_load_state('load')
                await frame.wait_for_timeout(1000)

                end_date_script = """ 
                (date) => {
                    document.querySelector('input[name="StartDate$ctl10"]').setAttribute('value', date)
                }
                """
                await frame.evaluate(end_date_script, booking_date)
                await frame.wait_for_load_state('load') 

                await frame.locator('input[name="btnViewAvailability"]').click()
                await frame.wait_for_load_state()
                logger.info("booking - searched for available slots")

                ## select date box
                create_window = frame.locator('div[id="createWindow_c"]')
                await frame.locator('div[class="divAvailable"]').first.click()
                await expect(create_window).to_be_visible()

                booking_frame = frame.frame_locator('#frmCreate')
                logger.info("booking - created booking frame")
                
                ## fill in the booking details 
                await booking_frame.locator('select[name="UsageType$ctl02"]').select_option(value="d946c992-97e3-4a44-bb11-07ad0440563d")
                await frame.wait_for_load_state('load')

                await booking_frame.locator('select[name="from$ctl02"]').select_option(value=start_time)
                await booking_frame.locator('select[name="to$ctl02"]').select_option(value=end_time)

                await booking_frame.locator('input[name="ExpectedNoAttendees$ctl02"]').fill('2')
                await booking_frame.locator('select[name="ChargeGroup$ctl02"]').select_option(value="1")
                await booking_frame.locator('textarea[name="Purpose$ctl02"]').fill(booker_name)
                await frame.wait_for_load_state('load')
                
                ## TODO: fill up nusnet id, find user id 

                ## select submit 
                await booking_frame.locator('input[id="btnCreateBooking"]').click()
                await frame.wait_for_load_state('load')
                logger.info("booking - submitted web booking")

                await asyncio.sleep(10)

                ## submission
                error_element_count = await booking_frame.locator('span[id="labelMessage1"]').count()

                if error_element_count != 0:
                    error_text = await booking_frame.locator('span[id="labelMessage1"]').text_content()
                    error_text = error_text.strip()

                    if error_text == "Start time must be 30 minutes before currenttime":
                        raise InvalidBookingTimeException("Caught during booking - " + error_text)

                    raise SlotTakenException(error_text if error_text else "This slot has been taken")
                else:
                    booking_id = await booking_frame.locator('table[id="BookingReferenceNumber"]').locator('tbody').locator('tr').locator('td').nth(1).text_content()
                    booking_id = booking_id.strip()
                    await state.update_data(utownfbsBookingId=booking_id)
            except Exception as e:
                logger.error(f"(in fbsbooker) Booking Failed due to: {e}")
                raise e
            finally:
                await browser.close()
                await playwright.stop()
                logger.info("booking - web booking completed on UtownFBS")
        
        return state

    ## cancellation process

    async def cancel_slot(message: Message, state: FSMContext):
        data = await state.get_data()
        #print(data['cancel_utownfbs_id'])

        async with async_playwright() as playwright:
            try: 
                ## start 
                browser = await playwright.chromium.launch(headless=True, channel="chrome")
                # context = await browser.new_context(http_credentials={
                #     'username': utownfbs_login['username'], 
                #     'password': utownfbs_login['password']
                # })
                # page = await context.new_page()
                page = await browser.new_page()
                logger.info("cancellation - browser has been set up")

                ## login to utownfbs
                await page.goto("https://utownfbs.nus.edu.sg/utown/loginpage.aspx")
                await page.locator('span[id="StudentLoginButton"]').click()
                await page.wait_for_timeout(10000)

                await page.locator('input[id="userNameInput"]').fill(utownfbs_login['username'])
                await page.locator('input[id="passwordInput"]').fill(utownfbs_login['password'])
                await page.locator('span[id="submitButton"]').click()
                await page.wait_for_timeout(10000)

                logger.info("cancellation - logged into utownfbs")


                ## click 'manage booking'
                dropdown_menu_locator = page.locator('ul[id="menu_mainMenu:submenu:22"]')
                await page.locator('div[id="menu_mainMenu"]').locator('li[aria-haspopup="menu_mainMenu:submenu:22"]').hover()
                await expect(dropdown_menu_locator).to_be_visible()

                await dropdown_menu_locator.get_by_text("My Personal Booking").click()
                await asyncio.sleep(15)

                search_form_element_count = await page.locator('form[id="form1"]').count()

                if search_form_element_count == 0:
                    raise ExpectedElementNotFound("Search form not found")

                frame = page.frame(name="frameBottom")

                if not frame:
                    raise ExpectedElementNotFound("Frame not found")

                await frame.wait_for_load_state()
                logger.info("cancellation - entered searching frame")

                ## find the slot with utownbookingid
                await frame.locator('input[id="buttonShowAdvance"]').click()
                await page.wait_for_load_state('load')

                new_frame = page.frame(name="frameBottom")

                if not new_frame:
                    raise ExpectedElementNotFound("Frame not found")

                await new_frame.wait_for_load_state()

                await new_frame.locator('input[name="BookingNumber$ctl02"]').fill(data['cancel_utownfbs_id'])
                await new_frame.locator('input[id="buttonSearch"]').click()
                await new_frame.wait_for_load_state()
                logger.info("cancellation - found booking to cancel")

                # click cancel + enter cancel remarks 
                await new_frame.locator('a[id="gridAdhocFacilityBookings_ctl03_btnCancel_0"]').click()
                await asyncio.sleep(10)

                view_form_element_count = await new_frame.locator('form[id="viewbooking"]').count()

                if view_form_element_count == 0:
                    raise ExpectedElementNotFound("View Booking form not found")
                
                await new_frame.locator('form[id="viewbooking"]').locator('input[name="CancelRemarks$ctl02"]').fill(DEFAULT_CANCEL_REMARK)

                # click cancel
                await new_frame.locator('input[name="btnConfirmCancellation"]').click()
                await asyncio.sleep(20)
                logger.info("cancellation - entered reamarks and submitted")

                # check panel Message 
                afterclick_form_element_count = await page.locator('form[id="form1"]').count()

                if afterclick_form_element_count == 0:
                    raise ExpectedElementNotFound("Search form not found")

                afterclick_frame = page.frame(name="frameBottom")

                if not afterclick_frame:
                    raise ExpectedElementNotFound("Frame not found")

                await afterclick_frame.wait_for_load_state()

                panel_message = await afterclick_frame.locator('div[id="panelMessage"]').text_content()
                panel_message = panel_message.strip()

                if panel_message != "Selected booking(s) has been cancelled/updated successfully":
                    raise Exception(f"Error in cancellation: {panel_message}")
            except Exception as e:
                logger.error(f"(in fbsbooker) Cancellation Failed due to: {e}")
                raise e
            finally:
                await browser.close()
                await playwright.stop()
                logger.info("cancellation - web cancellation completed on UtownFBS")
        
        return state