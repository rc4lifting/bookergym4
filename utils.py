from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

# keyboard functions 
# takes in a dictionary in builder {"display name": "backend value" for each option}
def create_inline(builder, row_width=1):
    inline_keyboard = []

    for idx, (button_text, callback_data) in enumerate(builder.items()):
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        if not idx % row_width:
            inline_keyboard.append([])
        inline_keyboard[-1].append(button)


    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    return keyboard

# time related functions 
def cal_end_time(start_time: str, duration: int) -> str:
    end_time = (datetime.strptime(start_time, "%H%M") + timedelta(minutes = duration)).time()
    return end_time.strftime("%H%M")

