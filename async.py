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
    ref = timeutil.fromUnix(since)
    updThreads = user.threads.where(Conversation.last_update > ref)
    return [{'tid' : t.id,
             'events' : [
                {'eid'   : e.id,
                 'html'  : render.renderEvent(e)
                 } for e in t.events.where(Event.last_update > ref)]}
            for t in updThreads]
    return updates

if __name__ == '__main__':
    form = session.get_form()
    response = { 'lastitem': lastitem() }
    if form.getfirst('since'):
        response['threads'] = updatedThreads(int(form.getfirst('since')))

    print "Content-type: application/json\n\n"
    print json.dumps(response)
