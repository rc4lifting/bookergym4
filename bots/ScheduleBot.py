import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import caches, config, database_functions, utils
from config import dp, bot, booking_router, logger
from caches import schedule_gsheet_id, schedule_credentials

class ScheduleBot(StatesGroup): 
    
    sheet_format_body = {
    }
    
    # gsheet details 
    scopes = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_info(schedule_credentials, scopes = scopes)
    service = build('sheets', 'v4', credentials=credentials)
    spreadsheets = service.spreadsheets()

    # helper functions 
    async def booking_str_to_cells(booking_date: str, start_time: str, duration: str):
        # returns out a list of cells to fill in
        # booking_date: dd/mm/yyyy, start_time: hhmm, duration: minutes
        start_datetime = datetime.strptime(booking_date + " " + start_time, "%d/%m/%Y %H%M")
        number_of_cells = int(duration) // 30
        day_of_week = start_datetime.date().weekday()

        # find first cell
        column = chr(ord('B') + day_of_week) 
        row = ((start_datetime.hour * 60 + start_datetime.minute) // 30) + 4

        cells = []

        # add the other cells 
        for i in range(0, number_of_cells):
            if row >= 52:
                if column == "H":
                    break

                column = chr(ord(column) + 1)
                row = 4
            cells.append(column + str(row))
            row = row + 1
        
        return cells 


    # bot functions 
    async def update_schedule(message: Message, state: FSMContext):
        logger.info("adding to schedule...")
        data = await state.get_data()

        booking_date = data['booking_date']
        start_time = data['booking_start_time']
        duration = data['booking_duration']

        cells_to_fill = await ScheduleBot.booking_str_to_cells(booking_date, start_time, duration)

        # TODO: get the sheet name for the current week
        sheet_name = "Sheet1!"

        request_body = {
            "valueInputOption": "RAW",
            "data": [{"range": sheet_name + cell, "values": [[data['booker_name']]]} for cell in cells_to_fill] # to change to data['name']
        }

        request = ScheduleBot.spreadsheets.values().batchUpdate(
            spreadsheetId=schedule_gsheet_id,
            body=request_body
        )

        try:
            response = request.execute()
        except Exception as e:
            raise e
        logger.info("successfully added to schedule!")

        return state

    async def remove_from_schedule(message: Message, state: FSMContext):
        logger.info("removing from schedule...")
        data = await state.get_data()

        booking_date = data['cancel_slot_date']
        start_time = data['cancel_slot_start_time']
        duration = data['cancel_slot_duration']
        cells_to_remove = await ScheduleBot.booking_str_to_cells(booking_date, start_time, duration)
        
        # TODO: get the sheet name for the current week
        sheet_name = "Sheet1!"

        request_body = {
            "ranges": [(sheet_name + cell) for cell in cells_to_remove]
        }

        request = ScheduleBot.spreadsheets.values().batchClear(
            spreadsheetId=schedule_gsheet_id,
            body=request_body
        )

        try:
            response = request.execute()
        except Exception as e:
            raise e
        logger.info("successfully removed to schedule!")

        return state
    
    async def create_new_sheet(sheet_name: str):
        # create new sheet
        
        # conditional formatting
        pass
    
    async def delete_old_sheet(sheet_name: str):
        pass