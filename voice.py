#!/usr/bin/python

from model import *
import cgi
import datetime
import os

form = cgi.FieldStorage()

print """\
Content-type: text/xml;charset=utf-8

"""

print '<Response>'

dispatch = os.getenv('PATH_INFO')
status = form.getfirst('CallStatus')

user = User.get(User.twilio_sid == form.getfirst('AccountSid'))
inbox = Inbox.get(Inbox.phone_number == form.getfirst('To'))

now = datetime.datetime.now()

try:
    call_rec = VoiceCall.get(VoiceCall.sid == form.getfirst('CallSid'))
except VoiceCall.DoesNotExist:
    call_rec = VoiceCall()
    call_rec.sid=form.getfirst('CallSid')
    call_rec.account=user
    call_rec.call_to=inbox
    call_rec.starttime=now

call_rec.lastevent = now
call_rec.call_from = form.getfirst('From') or ''
call_rec.call_status = status
call_rec.from_city = form.getfirst('FromCity') or ''
call_rec.from_state = form.getfirst('FromState') or ''
call_rec.from_zip = form.getfirst('FromZip') or ''
call_rec.from_country = form.getfirst('FromCountry') or ''
call_rec.call_duration = int(form.getfirst('CallDuration') or 0)
call_rec.save()

if form.getfirst('RecordingSid'):
    voicemail = Voicemail.create(call=call_rec,
                                 sid=form.getfirst('RecordingSid'),
                                 duration=int(form.getfirst('RecordingDuration') or 0),
                                 url=form.getfirst('RecordingUrl'),
                                 msg_new=True)



# TODO: blacklisting

handled = False
if dispatch == '/enter-call':
    call_timeout = 30
    forward_string = ''
    for fwd in inbox.forwarding_rules:
        if fwd.active:
            if fwd.max_ring_time:
                call_timeout = min(call_timeout, fwd.max_ring_time)
            forward_string += '<{type}>{addr}</{type}>'.format(type=fwd.dest_type,addr=fwd.dest_addr)
    if len(forward_string):
        print '<Dial action="post-call" timeout="%d">' % call_timeout
        print forward_string
        print '</Dial>'
        handled = True
    else:
        dispatch = '/post-call'

if dispatch == '/post-call':
    if status == 'completed':
        print '<Hangup>'
    else:
        print '<Play>%s</Play><Record action="post-vm" maxLength="240" />' % inbox.voicemail_greeting
    handled = True

if dispatch == '/post-vm':
    print '<Say>Your voicemail has been recorded. Thank you.</Say>'
    handled = True

if not handled:
    print '<Say>An error occurred. Please try again later.</Say>'

print '</Response>'
