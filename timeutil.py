"""Utility functions for handling time properly."""

import datetime
import calendar
import pytz

STAMPFORMAT='%Y%m%d%H%M%S'

def getTime():
    """Gets the current datetime record."""
    return datetime.datetime.utcnow().replace(microsecond=0)

def toStamp(time):
    """Converts a datetime record into a string."""
    return time.strftime(STAMPFORMAT)

def fromStamp(time_string):
    """Converts a timestamp string into a datetime record.
    
    If the timestamp cannot be parsed, returns the current time instead.
    """
    try:
        return datetime.datetime.strptime(time_string, STAMPFORMAT).replace(microsecond=999999)
    except:
        return getTime()

def get_tz(user):
    return pytz.timezone(user.timezone)

def convert(time,tz):
    return time.replace(tzinfo=pytz.UTC).astimezone(tz)
