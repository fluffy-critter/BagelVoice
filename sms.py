#!/usr/bin/python

from model import *
import control
import cgi
import datetime
import logging
import os

#TODO: switch to twilio.twiml

form = cgi.FieldStorage()

print """\
Content-type: text/xml;charset=utf-8

"""

dispatch = os.getenv('PATH_INFO')

event = control.getEvent(form=form,
                         sidField='MessageSid',
                         inbound=(dispatch == '/incoming'),
                         type="text")

if event.conversation.associate.blocked:
    # TODO: make this do something useful
    event.status = 'rejected'
    event.save()

for a in range(int(form.getfirst('NumMedia'))):
    content_type = form.getfirst('MediaContentType%d' % a)
    content_url = form.getfirst('MediaUrl%d' % a)
    if content_url:
        media = Attachment.create(sid='%s-%d' % (event.sid, a),
                                  url=content_url,
                                  mime_type=content_type,
                                  event=event)

print '''
<Response></Response>
'''
