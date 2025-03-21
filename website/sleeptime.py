from datetime import timedelta
from .models import SleepTime

def get_sleep_duration(user_id):
    sleep_entry = SleepTime.query.filter_by(user_id=user_id).first()
    
    if sleep_entry:
        sleep_duration = sleep_entry.sleeptime_to - sleep_entry.sleeptime_from
        
        hours = sleep_duration.total_seconds() // 3600 
        minutes = (sleep_duration.total_seconds() % 3600) // 60 

        return int(hours), int(minutes)
    else:
        return None 