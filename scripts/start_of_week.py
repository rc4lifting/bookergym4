import os 
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from bots.ScheduleBot import ScheduleBot
from config import logger

def start_week_sheet_automate():
    # delete old sheet
    ScheduleBot.delete_sheet_old_week()

if __name__ == "__main__":
    logger.info("START WEEK AUTOMATION - start")
    start_week_sheet_automate()
    logger.info("START WEEK AUTOMATION - end")