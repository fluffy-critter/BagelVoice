#!/usr/bin/python

from model import *
import control
import cgi
import logging
import os
import session

#TODO: switch to twilio.twiml

form = session.get_form()

print """\
Content-type: text/xml;charset=utf-8

"""

argv = session.get_argv()

event = control.getEvent(form=form,
                         sidField='MessageSid',
                         inbound=(len(argv) > 1 and argv[1] == '/incoming'),
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
