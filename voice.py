#!/usr/bin/python

from model import *
import control
import cgi
import os
import session
import datetime
import pytz

form = session.get_form()

print """\
Content-type: text/xml;charset=utf-8

"""

responseBody = None

argv = session.get_argv()
state = len(argv) > 1 and argv[1]

if not form.getfirst('Direction') or form.getfirst('Direction') == 'inbound':
    inbound=True
else:
    inbound=False
    
event = control.getEvent(form=form,
                         sidField='CallSid',
                         inbound=inbound,
                         type="voice")

if form.getfirst('RecordingSid'):
    Attachment.create(sid=form.getfirst('RecordingSid'),
        duration=int(int(form.getfirst('RecordingDuration') or 0)),
        url='%s.mp3' % form.getfirst('RecordingUrl'),
        mime_type = 'audio/mpeg',
        event=event)

responseBody = None
    
# Blacklist unwanted callers
if event.conversation.peer.blocked:
    responseBody = '<Reject/>'
    event.status = 'rejected'
    event.save()

if not responseBody and state == 'enter-call':
    call_timeout = None
    dialString = ''
    localNow = datetime.datetime.now(tz=pytz.timezone(event.inbox.user.timezone))
    localTime = localNow.time()

    for fwd in event.inbox.routes:

        active = fwd.active
        if active and fwd.rules.count():
            active = False
            for rule in fwd.rules:
                if rule.active_days.find("MTWRFSU"[localNow.weekday()]) < 0:
                    # This rule doesn't fire on this day of the week
                    continue

                if rule.start_time < rule.end_time:
                    if rule.start_time <= localTime and localTime < rule.end_time:
                        active = True
                        break
                else:
                    if localTime < rule.start_time or rule.end_time <= localTime:
                        active = True
                        break

        if active:
            if not call_timeout:
                call_timeout = fwd.max_ring_time
            elif fwd.max_ring_time:
                call_timeout = min(call_timeout, fwd.max_ring_time)
            dialString += '<{type}>{addr}</{type}>'.format(
                type=fwd.dest_type,
                addr=fwd.dest_addr
                )
    if dialString:
        responseBody = '<Dial action="post-call"%s>%s</Dial>' % (
            call_timeout and ' timeout="%d"' % call_timeout or '',
            dialString)
    else:
        state = 'post-call'

if not responseBody and state == 'post-call':
    if event.status == 'completed':
        responseBody = '<Hangup/>'
    else:
        inbox = event.inbox
        if inbox.voicemail_greeting:
            responseBody = '<Play>%s</Play>' % inbox.voicemail_greeting
        else:
            responseBody = '<Say>Please leave a message.</Say>'
        responseBody += '<Record action="post-vm" maxLength="240" />'

if not responseBody and state == 'post-vm':
    responseBody = '<Say>Your voicemail has been recorded. Thank you.</Say>'

if not responseBody:
    responseBody = '<Say>An unknown error occurred. Please try again later. (state=%s)</Say>' % state

print '<Response>'
print responseBody
print '</Response>'
