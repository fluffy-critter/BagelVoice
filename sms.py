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

msg = TextMessage.create(sid=form.getfirst('MessageSid'),
                         inbox=inbox,
                         time=datetime.datetime.now(),
                         msg_with=form.getfirst('From'),
                         msg_from=form.getfirst('From'),
                         msg_to=form.getfirst('To'),
                         msg_body=form.getfirst('Body'),
                         from_city=form.getfirst('FromCity'),
                         from_state=form.getfirst('FromState'),
                         from_zip=form.getfirst('FromZip'),
                         from_country=form.getfirst('FromCountry'))

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
