import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import caches, config, database_functions, utils
from config import dp, bot, booking_router, logger
from caches import schedule_gsheet_id, schedule_credentials

class ScheduleBot(StatesGroup): 
    
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
    
    async def generate_time_strings():
        times = []
        start_time = datetime.strptime('12:00 AM', '%I:%M %p')
        end_time = datetime.strptime('11:30 PM', '%I:%M %p')
        current_time = start_time
        
        while current_time <= end_time:
            times.append(current_time.strftime('%-I:%M %p'))
            current_time += timedelta(minutes=30)
    
        return times


    # bot functions 
    async def update_schedule(message: Message, state: FSMContext):
        logger.info("adding to schedule...")
        data = await state.get_data()

        booking_date = data['booking_date']
        start_time = data['booking_start_time']
        duration = data['booking_duration']

        cells_to_fill = await ScheduleBot.booking_str_to_cells(booking_date, start_time, duration)

        # TODO: get the sheet name for the current week
        sheet_name = database_functions.read_data("/sheets/current_sheet/sheet_name")

        request_body = {
            "valueInputOption": "RAW",
            "data": [{"range": sheet_name + "!" +  cell, "values": [[data['booker_name']]]} for cell in cells_to_fill] # to change to data['name']
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
        sheet_name = database_functions.read_data("/sheets/current_sheet/sheet_name")

        request_body = {
            "ranges": [(sheet_name + "!" + cell) for cell in cells_to_remove]
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
    
    async def create_sheet_new_week(sheet_name: str, week_start_dt: datetime):
        logger.info("Automated Script: creating new sheet for the week!")
        
        ## create new sheet
        # freeze pane, up to row 3 column A
        new_sheet_id = int(week_start_dt.strftime('%Y%m%d'))
        
        create_body = {
            "requests": [{
                "addSheet": {
                    "properties": {
                        "sheetId": new_sheet_id,
                        "title": sheet_name,
                        "gridProperties": {
                            "frozenRowCount": 3,
                            "frozenColumnCount": 1
                        }
                    }
                }
            }]
        }
        
        try:
            logger.info("creating the sheet in gsheet!")
            ScheduleBot.spreadsheets.batchUpdate(
                spreadsheetId=schedule_gsheet_id,
                body=create_body
            ).execute()
        except Exception as e:
            logger.error("Automated Script (create_sheet_new_week): failed to create new sheet for the week!")
            
         
        requests_list = []
        date_string_list = [(week_start_dt + timedelta(days=i)).strftime('%-d/%-m/%Y') for i in range(7)]
        time_string_list = await ScheduleBot.generate_time_strings()
        
        ## standard schedule template formatting        
        # A:H resize to 200px
        requests_list.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": new_sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 8
                },
                "properties": {
                    "pixelSize": 200
                },
                "fields": "*"
            }
        })
        
        # merge D1, E1
        requests_list.append({
            "mergeCells": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 3,
                    "endColumnIndex": 5,
                }
            }
        })
        
        # writing title in D1 E1
        requests_list.append({
            "updateCells": {
                "rows": [{
                    "values": [
                        {
                            "userEnteredValue": {"stringValue": "RC4 GYM BOOKING"},
                            "userEnteredFormat": {
                                "textFormat": {
                                    "fontSize": 36,
                                    "bold": True,
                                    "fontFamily": "Calibri"
                                },
                                "horizontalAlignment": "CENTER"
                            }
                        }
                    ]
                    
                }],
                "fields": "*",
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 3,
                    "endColumnIndex": 5,
                }
            }
        })
        
        # writing days of week in A2:H2
        day_values = [{
            "userEnteredValue": {"stringValue": word},
            "userEnteredFormat": {
                "textFormat": {
                    "fontSize": 12,
                    "bold": True,
                    "fontFamily": "Verdana"
                },
                "backgroundColor": {
                "red": 0.561,
                "green": 0.663,
                "blue": 0.859,
                "alpha": 1
                }
            }
        } for word in ["Day", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
        
        requests_list.append({
            "updateCells": {
                "rows": [{
                    "values": day_values
                }],
                "fields": "*",
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 8,
                }
            }
        })
        
        # writing time A3
        requests_list.append({
            "updateCells": {
                "rows": [{
                    "values": [{
                        "userEnteredValue": {"stringValue": "Time"},
                        "userEnteredFormat": {
                            "textFormat": {
                                "fontSize": 12,
                                "fontFamily": "Verdana"
                            },
                            "backgroundColor": {
                                "red": 0.561,
                                "green": 0.663,
                                "blue": 0.859,
                                "alpha": 1
                            },
                            "horizontalAlignment": "LEFT"
                        }
                    }]
                }],
                "fields": "*",
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 2,
                    "endRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                }
            }
        })
        
        # writing dates B3:H3
        requests_list.append({
            "updateCells": {
                "rows": [{
                    "values": [{
                        "userEnteredValue": {"stringValue": word},
                        "userEnteredFormat": {
                            "textFormat": {
                                "fontSize": 12,
                                "fontFamily": "Verdana"
                            },
                            "backgroundColor": {
                                "red": 0.561,
                                "green": 0.663,
                                "blue": 0.859,
                                "alpha": 1
                            },
                            "horizontalAlignment": "RIGHT"
                        }
                    } for word in date_string_list]
                }],
                "fields": "*",
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 2,
                    "endRowIndex": 3,
                    "startColumnIndex": 1,
                    "endColumnIndex": 8,
                }
            }
        })
        
        # writing time (XX:XX AM) A4:A51
        requests_list.append({
            "updateCells": {
                "rows": [{
                    "values": [{
                        "userEnteredValue": {"stringValue": word},
                        "userEnteredFormat": {
                            "horizontalAlignment": "RIGHT",
                            "textFormat": {
                                "fontSize": 11,
                                "fontFamily": "Verdana"
                            }
                        }
                    }]
                } for word in time_string_list],
                "fields": "*",
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 3,
                    "endRowIndex": 4 + len(time_string_list),
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                }
            }
        })
        
        # change formatting of B4:H51
        requests_list.append({
            "repeatCell": {
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "fontSize": 11,
                            "fontFamily": "Verdana"
                        }
                    }
                },
                "fields": "*",
                "range": {
                        "sheetId": new_sheet_id,
                        "startRowIndex": 3,
                        "endRowIndex": 51,
                        "startColumnIndex": 1,
                        "endColumnIndex": 8,
                }
            }
        })
        
        # all borders for A2:H51
        border = {
            "style": "SOLID",
        }
        
        requests_list.append({
            "updateBorders": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 51,
                    "startColumnIndex": 1,
                    "endColumnIndex": 8,
                },
                'top': border,
                'bottom': border,
                'left': border,
                'right': border,
                "innerHorizontal": border,
                "innerVertical": border
            }
        })
        
        ## conditional formatting - red when cells are filled B4:H51
        requests_list.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": new_sheet_id,
                        "startRowIndex": 3,
                        "endRowIndex": 51,
                        "startColumnIndex": 1,
                        "endColumnIndex": 8,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "NOT_BLANK"
                        },
                        "format": {
                            "backgroundColor": {"red": 1}
                        }
                    }
                } 
            }
        })
    
        ## execute requests 
        body = {"requests": requests_list}
        request = ScheduleBot.spreadsheets.batchUpdate(
            spreadsheetId=schedule_gsheet_id,
            body=body
        )
        
        try:
            logger.info("Automated Script: updating the sheet in gsheet with template!")
            response = request.execute()
        except Exception as e:
            logger.error("Automated Script (create_sheet_new_week): failed to create new sheet for the week!")
        else:
            logger.info("Automated Script: created new sheet for the week!")
            sheet_info = {
                "sheet_name": sheet_name,
                "sheet_id": new_sheet_id
            }
            database_functions.set_data("/sheets/new_sheet", sheet_info)
    
    async def delete_sheet_old_week():
        sheet_id = database_functions.read_data("/sheets/current_sheet/sheet_id")
        body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
        request = ScheduleBot.spreadsheets.batchUpdate(
            spreadsheetId=schedule_gsheet_id,
            body=body
        )
        
        try:
            logger.info("Automated Script: deleting old sheet")
            response = request.execute()
        except Exception as e:
            logger.error("Automated Script (delete_sheet_old_week): failed to delete old sheet for the last week!")
        else:
            logger.info("Automated Script: deleted old sheet for the prev week!")
            database_functions.update_data("/sheets/current_sheet", database_functions.read_data("/sheets/new_sheet"))
            database_functions.delete_data("/sheets/new_sheet")