# Utility functions for handling time properly

import datetime
import calendar
import pytz

# Get the current timestamp
def getTime():
    return datetime.datetime.utcnow()

def toUnix(time):
    return calendar.timegm(time.utctimetuple())

def fromUnix(time):
    return datetime.datetime.utcfromtimestamp(time)
