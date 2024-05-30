# to create utilisation functions i.e. creating inline keyboards etc. 
from datetime import datetime, timedelta

def cal_end_time(start_time: str, duration: int) -> str:
    end_time = (datetime.strptime(start_time, "%H%M") + timedelta(minutes = duration)).time()
    return end_time.strftime("%H%M")

