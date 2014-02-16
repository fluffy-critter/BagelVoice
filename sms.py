#!/usr/bin/python

from model import *
import cgi
import datetime
import logging

form = cgi.FieldStorage()

print """\
Content-type: text/xml;charset=utf-8

"""

user = User.get(User.twilio_sid == form.getfirst('AccountSid'))
inbox = Inbox.get(Inbox.phone_number == form.getfirst('To'))

try:
    msg = TextMessage.get(TextMessage.sid == form.getfirst('MessageSid'))
except TextMessage.DoesNotExist:
    # brand-new incoming text message
    msg = TextMessage()
    msg.sid = form.getfirst('MessageSid')
    msg.inbox = inbox
    msg.time = datetime.datetime.now()
    # since this is new it's probably incoming; if it's a callback
    # from an unrecorded outgoing one then we'll fail due to the
    # missing body (TODO: is this really the best approach?)
    msg.msg_with=form.getfirst('From')

# TODO surely there's a better way...
if form.getfirst('From'): msg.msg_from=form.getfirst('From')
if form.getfirst('To'): msg.msg_to=form.getfirst('To')
if form.getfirst('Body'): msg.msg_body=form.getfirst('Body')
if form.getfirst('FromCity'): msg.from_city=form.getfirst('FromCity')
if form.getfirst('FromState'): msg.from_state=form.getfirst('FromState')
if form.getfirst('FromZip'): msg.from_zip=form.getfirst('FromZip')
if form.getfirst('FromCountry'): msg.from_country=form.getfirst('FromCountry')
if form.getfirst('MessageStatus'): msg.send_status=form.getfirst('MessageStatus')
msg.save()

for a in range(int(form.getfirst('NumMedia'))):
    content_type = form.getfirst('MediaContentType%d' % a)
    content_url = form.getfirst('MediaUrl%d' % a)
    if content_url:
        media = TextAttachment.create(message=msg,
                                      content_type=content_type,
                                      content_url=content_url)
        media.save()

print '''
<Response></Response>
'''
