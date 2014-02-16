#!/usr/bin/python

from model import *
import cgi
import cgitb
import datetime
import os

cgitb.enable(display=False,format='text')

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
    call_rec = VoiceCall.get(sid == form.getfirst('CallSid'))
except VoiceCall.DoesNotExist:
    call_rec = VoiceCall.create(sid=form.getfirst('CallSid'),
                                account=user,
                                inbox=inbox,
                                starttime=now,
                                msg_new=True
                                )

call_rec.call_from = form.getfirst('From')
call_rec.call_status = status
call_rec.caller_id_string = form.getfirst('CallerName')
call_rec.from_city = form.getfirst('FromCity')
call_rec.from_state = form.getfirst('FromState')
call_rec.from_zip = form.getfirst('FromZip')
call_rec.from_country = form.getfirst('FromCountry')
call_rec.call_duration = form.getfirst('CallDuration')
call_rec.lastevent = now
call_rec.save()

if form.getfirst('RecordingSid'):
    voicemail = Voicemail.create(sid=form.getfirst('RecordingSid'),
                                 duration=form.getfirst('RecordingDuration'),
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
