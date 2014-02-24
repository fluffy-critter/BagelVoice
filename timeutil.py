"""Utility functions for handling time properly.

Within the database, all times must be stored as naive UTC, and should
only be tagged with a specific timezone for display purposes.
"""

import datetime
import calendar
import pytz

""" Format used for asynchronous event timestamps. """
STAMPFORMAT='%Y%m%d%H%M%S'

def getTime():
    """Gets the current datetime record as a naive, UTC time with single-second precision.

    This is necessary to keep dates consistent when going in and out of SQLite.
    """
    return datetime.datetime.utcnow().replace(microsecond=0)

def toStamp(time):
    """Converts a datetime record into a string to be used by async.py."""
    return time.strftime(STAMPFORMAT)

def fromStamp(time_string):
    """Converts a timestamp string from async.py requests into a datetime record.
    
    If the timestamp cannot be parsed, returns the current time instead.
    """
    try:
        return datetime.datetime.strptime(time_string, STAMPFORMAT).replace(microsecond=999999)
    except:
        return getTime()

def get_tz(user):
    """Returns the configured timezone info for the specified user."""
    return pytz.timezone(user.timezone)

def convert(time,tz):
    """Convert a naive UTC time into a specific timezone."""
    return time.replace(tzinfo=pytz.UTC).astimezone(tz)
