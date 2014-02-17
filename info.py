#!/usr/bin/python
# Routines and request handler for getting information about the inbox

import session
import os
import control
import json
import render
import calendar
from model import *

user = session.get_user()

def lastitem():
    latest = user.threads.order_by(Conversation.last_update.desc()).get().last_update
    return calendar.timegm(latest.utctimetuple())

if __name__ == '__main__':
    item = os.getenv('PATH_INFO')
    response = { 'lastitem': lastitem() }
    print "Content-type: application/json\n\n"
    print json.dumps(response)
