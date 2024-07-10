from bots.ScheduleBot import ScheduleBot
from datetime import datetime, timedelta
import pytz

def end_week_sheet_automate():
    singapore_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(singapore_tz)
    days_left = (7 - now.weekday()) % 7
    
    # start and end of next sheet (mon - sun)
    upcoming_week_start = (now + timedelta(days=days_left)).replace(hour=0, minute=0, second=0, microsecond=0)
    upcoming_week_end = upcoming_week_start + timedelta(days=6)
    new_sheet_name = upcoming_week_start.strftime("%d %b") + " - " + upcoming_week_end.strftime("%d %b")
    
    # create new sheet
    ScheduleBot.create_sheet_new_week(new_sheet_name, upcoming_week_start)

if __name__ == "__main__":
    end_week_sheet_automate()