#!/usr/bin/python
# Routines and request handler for getting information about the inbox

import session
import os
import control
import json
import render
import calendar
import timeutil
from model import *

user = session.get_user(doLogin=False)

def lastitem():
    try:
        latest = user.threads.order_by(Conversation.last_update.desc()).get().last_update
    except Conversation.DoesNotExist:
        latest = timeutil.getTime()
    return timeutil.toUnix(latest) + 1

def updatedThreads(since):
    updThreads = user.threads.select().where(Conversation.last_update > timeutil.fromUnix(since))
    return [{'id'   : t.id,
             'html' : render.renderThread(t)
             } for t in updThreads]

if __name__ == '__main__':
    form = session.get_form()
    response = { 'lastitem': lastitem() }
    if form.getfirst('since'):
        response['updatedThreads'] = updatedThreads(int(form.getfirst('since')))

    print "Content-type: application/json\n\n"
    print json.dumps(response)
