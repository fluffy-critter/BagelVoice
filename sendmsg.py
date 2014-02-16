#!/usr/bin/python

import session
import control
import model
import datetime
from model import Event
from twilio.rest import TwilioRestClient

user = session.get_user()
form = session.get_form()

inbox = control.getInbox(form, user, 'From')
assoc = control.getAssociate(form, user, 'To')

client = TwilioRestClient(user.twilio_sid, user.twilio_auth_token)

with model.transaction():
    body = form.getfirst('Body')
    
    message = client.messages.create(
        body=body,
        from_=form.getfirst('From'),
        to=form.getfirst('To'),
        status_callback='https://vbx.e-snail.us/sms.py/outgoing' #FIXME
    )

    now = datetime.datetime.now()
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
        conversation = control.getConversation(form, inbox, assoc)
        event = Event.create(
            sid=message.sid,
            inbound=False,
            inbox=inbox,
            conversation=conversation,
            message_body=body,
            time=now,
            last_update=now,
            status=message.status)
        conversation.last_update = now
        conversation.save()

print '''Content-type: text/html
Location: .

Redirecting to the app'''