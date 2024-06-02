from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

import re

# General Keyboard functions 
# Takes in a dictionary in builder {"display name": "backend value" for each option}
def create_inline(builder, row_width=1):
    inline_keyboard = []

    for idx, (button_text, callback_data) in enumerate(builder.items()):
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        if not idx % row_width:
            inline_keyboard.append([])
        inline_keyboard[-1].append(button)

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard

# Time related functions 
def cal_end_time(start_time: str, duration: str) -> str:
    end_time = (datetime.strptime(start_time, "%H%M") + timedelta(minutes=int(duration))).time()
    return end_time.strftime("%H%M")

def get_formatted_date_from_string(date_str: str) -> str:
    date = datetime.strptime(date_str, "%d/%m/%Y")
    return date.strftime("%A %d %B %Y")

# Room Number Functions 
def is_valid_room_number(room_number: str) -> bool:
    pattern = r"(\d{2})-(\d{2})([A-F]?)"
    match = re.match(pattern, room_number)

    valid = False

    if match:
        floor = int(match.group(1))
        room = int(match.group(2))
        suite_letter = match.group(3)

        print(floor, room, suite_letter)

        if 3 <= floor <= 17 and 1 <= room <= 27 and \
            ((room in [1, 11, 12] and suite_letter != '') or (room not in [1, 11, 12] and suite_letter == '')):
            valid = True
    return valid 

# Specific Keyboards
def create_booking_date_keyboard():
    today = datetime.today()
    date_options = { (today + timedelta(days=i)).strftime("%A %d %B %Y"): (today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(7) }
    return create_inline(date_options, row_width=2)

def create_start_time_keyboard(start_time_str: str, end_time_str: str, interval: int):
    start_time = datetime.strptime(start_time_str, "%H%M")
    end_time = datetime.strptime(end_time_str, "%H%M")
    interval = timedelta(minutes=interval)
    
    start_times = {}

    while start_time <= end_time:
        start_times[start_time.strftime("%H%M")] = start_time.strftime("%H%M")
        start_time += interval

    return create_inline(start_times, row_width=3)


