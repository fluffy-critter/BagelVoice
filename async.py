#!/usr/bin/python
"""Routines and request handler for getting information about the inbox."""

import session
session.user(doLogin=False)

import os
import control
import json
import render
import calendar
import timeutil
import sys
from model import *
import config

user = session.user()
argv = session.argv()

def lastitem():
    try:
        latest = user.threads.order_by(Conversation.last_update.desc()).get().last_update
    except Conversation.DoesNotExist:
        latest = timeutil.getTime()
    return timeutil.toStamp(latest)

def updatedThreads(since):
    ref = timeutil.fromStamp(since)
    updThreads = user.threads.where(Conversation.last_update > ref)
    return [{'tid' : t.id,
             'events' : [
                {'eid'   : e.id,
                 'html'  : render.renderEvent(e)
                 } for e in t.events.where(Event.last_update > ref)]}
            for t in updThreads]
    return updates

if __name__ == '__main__':
    response = None

    form = session.form()
    if len(argv) == 1:
        response = { 'lastitem': lastitem() }
        if form.getfirst('since'):
            response['threads'] = updatedThreads(form.getfirst('since')) or None
    elif argv[1] == 'mark':
        if len(argv) != 3:
            print "Status: 400 Bad Request\nContent-type: text/html\n\nMissing thread id"
            sys.exit()

        count=0
        for thread in user.threads.where(Conversation.id == int(argv[2])):
            if thread.unread:
                count += 1
                thread.unread = False
                thread.save()
        response = count

    print "Content-type: application/json\n\n"
    print json.dumps(response)
