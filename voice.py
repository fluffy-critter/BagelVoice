#!/usr/bin/python

from model import *
import control
import cgi
import os

form = cgi.FieldStorage()

print """\
Content-type: text/xml;charset=utf-8

"""

responseBody = None

dispatch = os.getenv('PATH_INFO')

if not form.getfirst('Direction') or form.getfirst('Direction') == 'inbound':
    inbound=True
else:
    inbound=False
    
event = control.getEvent(form=form,
                         sidField='CallSid',
                         inbound=inbound)

if form.getfirst('RecordingSid'):
    Attachment.create(sid=form.getfirst('RecordingSid'),
        duration=int(int(form.getfirst('RecordingDuration') or 0)),
        url='%s.mp3' % form.getfirst('RecordingUrl'),
        mime_type = 'audio/mpeg',
        event=event)

responseBody = None
    
# Blacklist unwanted callers
if event.conversation.associate.blocked:
    responseBody = '<Reject>'
    event.status = 'rejected'
    event.save()

if not responseBody and dispatch == '/enter-call':
    call_timeout = 30
    dialString = ''
    for fwd in event.inbox.routes:
        if fwd.active:
            if fwd.max_ring_time:
                call_timeout = min(call_timeout, fwd.max_ring_time)
            dialString += '<{type}>{addr}</{type}>'.format(
                type=fwd.dest_type,
                addr=fwd.dest_addr
                )
    if dialString:
        responseBody = '<Dial action="post-call" timeout="%d">%s</Dial>' % (
            call_timeout,
            dialString)
    else:
        dispatch = '/post-call'

if not responseBody and dispatch == '/post-call':
    if event.status == 'completed':
        responseBody = '<Hangup>'
    else:
        responseBody = '<Play>%s</Play><Record action="post-vm" maxLength="240" />' % inbox.voicemail_greeting

if not responseBody and dispatch == '/post-vm':
    responseBody = '<Say>Your voicemail has been recorded. Thank you.</Say>'

if not responseBody:
    responseBody = '<Say>An unknown error occurred. Please try again later.</Say>'

print '<Response>'
print responseBody
print '</Response>'
