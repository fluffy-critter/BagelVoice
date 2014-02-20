# Utility functions for handling time properly

import datetime
import calendar
import pytz

STAMPFORMAT='%Y%m%d%H%M%S'

# Get the current timestamp
def getTime():
    return datetime.datetime.utcnow().replace(microsecond=0)

def toStamp(time):
    return time.strftime(STAMPFORMAT)

def fromStamp(time):
    try:
        return datetime.datetime.strptime(time, STAMPFORMAT).replace(microsecond=999999)
    except:
        return getTime()

def get_tz(user):
    return pytz.timezone(user.timezone)

def convert(time,tz):
    return time.replace(tzinfo=pytz.UTC).astimezone(tz)
