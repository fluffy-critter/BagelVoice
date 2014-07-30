#!/usr/bin/python

from model import *
import config
import control
import cgi
import os
import session
import datetime
import pytz
import sys
import logging

logger = logging.getLogger(__name__)
form = session.form()

responseBody = None

argv = session.argv()
if len(argv) < 2:
    print """Status: 400 Bad Request\nContent-type: text/html\n\nMissing state"""
    sys.exit()

state = argv[1]

if not form.getfirst('Direction') or form.getfirst('Direction') == 'inbound':
    inbound=True
else:
    inbound=False
    
def reject():
    print "Content-type: application/xml\n\n<Response><Reject/></Response>"
    sys.exit()

# Ignore forwarding loops
if form.getfirst('From') == form.getfirst('To'):
    reject()

user = control.getUser(form)

if inbound:
    inbox = control.getInbox(form,user,'To')
    if (form.getfirst('ForwardedFrom')
        and inbox.routes.select().where(CallRoute.dest_addr == form.getfirst('ForwardedFrom')).count()):
        reject()

event = control.getEvent(form=form,
                         sidField='CallSid',
                         inbound=inbound,
                         type="voice")
if state == 'transcribed':
    # Push forward any pending notifications
    for n in event.pending_notifications:
        n.time = datetime.datetime.now()
        n.save()

    sys.exit()

responseBody = None
    
# Blacklist unwanted callers
if event.conversation.peer.blocked:
    event.status = 'rejected'
    event.save()
    reject()

# send voicemail callers directly to voicemail
if event.conversation.peer.send_to_voicemail and state == 'enter-call':
    state = 'post-call'

inbox = event.inbox
user = inbox.user
notifyQuery = None
notifyDelay = None

if not responseBody and state == 'enter-call':
    notifyQuery = user.notifications.where(Notification.notify_call_incoming == True)
    call_timeout = inbox.max_ring_time
    dialString = ''
    localNow = datetime.datetime.now(tz=pytz.timezone(user.timezone))
    localTime = localNow.time()

    for fwd in event.inbox.routes:

        active = (fwd.active
                  and fwd.dest_addr != event.conversation.peer.phone_number
                  and fwd.dest_addr != form.getfirst('ForwardedFrom'))
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
    notifyQuery = user.notifications.where(Notification.notify_call_missed == True)
    notifyDelay = 60
    if event.status == 'completed' or form.getfirst('DialCallStatus') == 'completed':
        responseBody = '<Hangup/>'
    else:
        inbox = event.inbox
        if inbox.voicemail_greeting:
            responseBody = '<Play>%s</Play>' % inbox.voicemail_greeting
        else:
            responseBody = '<Say>Please leave a message.</Say>'
        transcribeTag = ''
        if inbox.transcribe_voicemail:
            transcribeTag = ' transcribe="true" transcribeCallback="transcribed"'
        responseBody += '<Record action="%s/voice.py/post-vm" maxLength="240"%s />' % (config.configuration['root-url'],transcribeTag)

if not responseBody and state == 'post-vm':
    notifyQuery = user.notifications.where(Notification.notify_voicemail == True)
    # give the transcription service a chance to transcribe before notifying
    if event.inbox.transcribe_voicemail and form.getfirst('RecordingDuration'):
        notifyDelay = 60 + int(form.getfirst('RecordingDuration'))
    responseBody = '<Say>Your voicemail has been recorded. Thank you.</Say>'

if not responseBody:
    responseBody = '<Say>An unknown error occurred. Please try again later. (state=%s)</Say>' % state

logger.info("notifyDelay=%d", notifyDelay or 0)
for n in notifyQuery:
    try:
        control.notify(event, n, notifyDelay)
    except:
        logger.exception("Got error trying to notify on call")


print """\
Content-type: text/xml;charset=utf-8

"""

print '<Response>'
print responseBody
print '</Response>'
