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
import logging

logger=logging.getLogger("async") 

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
    elif argv[1] == 'editpeer':
        if len(argv) != 3:
            print "Status: 400 Bad Request\nContent-type: text/html\n\nMissing peer id"
            sys.exit()

        for peer in user.peers.where(Peer.id == int(argv[2])):
            if form.getfirst('name'):
                logger.info('name=%s', form.getfirst('name'))
                peer.display_name = form.getfirst('name')
            if form.getfirst('blocked'):
                logger.info('blocked=%s', form.getfirst('blocked'))
                peer.blocked = int(form.getfirst('blocked'))
            if form.getfirst('vm'):
                logger.info('vm=%s', form.getfirst('vm'))
                peer.send_to_voicemail = int(form.getfirst('vm'))
            peer.save()
            logger.info("name=%s blocked=%s vm=%s", peer.display_name, peer.blocked, peer.send_to_voicemail)

    print "Content-type: application/json\n\n"
    print json.dumps(response)
