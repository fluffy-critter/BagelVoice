#!/usr/bin/python

import session
import control
import model
import timeutil
from model import Event
from twilio.rest import TwilioRestClient
import twilio
import config
import sys

user = session.get_user()
form = session.get_form()

for check in ['Body', 'From', 'To']:
    if not form.getfirst(check):
        print "Status: 400 Bad Requeset\nContent-type: text/html\n\nMissing parameter: %s" % check
        sys.exit()

inbox = control.getInbox(form, user, 'From')
client = TwilioRestClient(user.twilio_sid, user.twilio_auth_token)

with model.transaction():
    body = form.getfirst('Body')

    try:
        message = client.messages.create(
            body=body,
            from_=form.getfirst('From'),
            to=form.getfirst('To'),
            status_callback=config.configuration['root-url'] + '/sms.py/outgoing'
            )
    except twilio.TwilioRestException as e:
        print "Status: 400 Bad Request\nContent-type: text/html\n\n%s" % str(e)
        sys.exit()

    now = timeutil.getTime()
    try:
        # It's possible that the callback fired before we got here...
        event = Event.get(Event.sid == message.sid)
        event.message_body = body
        event.last_update = now
        event.save()
        conversation = event.conversation
        conversation.last_update = now
        conversation.save()
    except Event.DoesNotExist:
        # ... but not likely
        peer = control.getPeer(form, user, whoValue=message.to)
        conversation = control.getConversation(form, inbox, peer)
        event = Event.create(
            sid=message.sid,
            inbound=False,
            inbox=inbox,
            conversation=conversation,
            message_body=body,
            time=now,
            last_update=now,
            status=message.status,
            type="text")
        conversation.last_update = now
        conversation.save()

print '''Content-type: text/html
Location: .

Redirecting to the app'''
