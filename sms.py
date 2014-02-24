#!/usr/bin/python

from model import *
import control
import cgi
import logging
import os
import session
import sys
import timeutil

logger=logging.getLogger(__name__)

form = session.form()
argv = session.argv()

if not form.getfirst('MessageSid'):
    print "Status: 400 Bad Request\nContent-type: text/html\n\nMissing message SID"
    sys.exit()

user = control.getUser(form)
event = control.getEvent(form=form,
                         sidField='MessageSid',
                         inbound=(len(argv) > 1 and argv[1] == 'incoming'),
                         type="text")

for a in range(int(form.getfirst('NumMedia') or 0)):
    content_type = form.getfirst('MediaContentType%d' % a)
    content_url = form.getfirst('MediaUrl%d' % a)
    if content_url:
        media = Attachment.create(sid='%s-%d' % (event.sid, a),
                                  url=content_url,
                                  mime_type=content_type,
                                  event=event)

if event.conversation.peer.blocked:
    # TODO: make this do something useful
    event.status = 'rejected'
    event.save()
    sys.exit()

if argv[1] == 'incoming':
    for n in user.notifications.where(Notification.notify_sms == True):
        try:
            control.notify(event, n)
        except:
            logger.exception("Got error trying to notify on SMS")

print """Content-type: text/xml;charset=utf-8

<Response></Response>
"""
