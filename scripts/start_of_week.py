import database_functions
from bots.ScheduleBot import ScheduleBot

def start_week_sheet_automate():
    # delete old sheet
    ScheduleBot.delete_sheet_old_week()

if __name__ == "__main__":
    pass