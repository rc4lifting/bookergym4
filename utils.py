from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

# Keyboard functions 
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
def cal_end_time(start_time: str, duration: int) -> str:
    end_time = (datetime.strptime(start_time, "%H%M") + timedelta(minutes=duration)).time()
    return end_time.strftime("%H%M")

def create_booking_date_keyboard():
    today = datetime.today()
    date_options = { (today + timedelta(days=i)).strftime("%A %d %B %Y"): (today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(7) }
    return create_inline(date_options, row_width=2)

def create_booking_time_keyboard():
    time_ranges = {
        "0000 - 0530": "0000-0530",
        "0600 - 1130": "0600-1130",
        "1200 - 1730": "1200-1730",
        "1800 - 2330": "1800-2330"
    }
    return create_inline(time_ranges, row_width=1)

def create_start_time_keyboard():
    start_times = { f"{hour:02d}00": f"{hour:02d}00" for hour in range(6, 18) }
    return create_inline(start_times, row_width=3)

def create_duration_keyboard():
    durations = {
        "1 hour": "60",
        "1 hour 30 mins": "90"
    }
    return create_inline(durations, row_width=1)


