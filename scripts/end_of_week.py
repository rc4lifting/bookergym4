import os 
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from bots.ScheduleBot import ScheduleBot
from config import logger
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
    logger.info("END WEEK AUTOMATION - start")
    end_week_sheet_automate()
    logger.info("END WEEK AUTOMATION - end")