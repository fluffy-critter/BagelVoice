#!/usr/bin/python

import session
from model import *
from cStringIO import StringIO
import timeutil
import sys

user = session.user()
tz = timeutil.get_tz(user)

def renderEvent(event):
    out = StringIO()
    print >>out, '<div class="event %s" id="event-%d">' % (
        event.inbound and 'inbound' or 'outbound',
        event.id)

    if event.status:
        print >>out, '<div class="status stat-%s">%s</div>' % (
            event.status,
            event.status
            )

    print >>out, '<div class="when">%s</div>' % timeutil.convert(event.time,tz).strftime('%x %X')

    if event.call_duration:
        print >>out, '<div class="call">Call, %d seconds</div>' % event.call_duration
    if event.message_body:
        print >>out, '<div class="text">%s</div>' % event.message_body

    for attach in event.media:
        print >>out, '<div class="media">'
        attachBody = None
        mimeclass = attach.mime_type.split('/')[0]
        if mimeclass == 'audio':
            attachBody = '<audio controls="controls"><source src="%s" type="%s"></audio>' % (
                attach.url, attach.mime_type)
        elif mimeclass == 'image':
            attachBody = '<img src="%s">' % attach.url
        elif mimeclass == 'video':
            attachBody = '<video controls="controls"><source src="%s" type="%s"></video>' % (
                attach.url, attach.mime_type)
        if attachBody:
            print >>out, '<div class="attachbody">%s</div>' % attachBody
        print >>out, '<a href="%s">original %s</a>' % (attach.url, mimeclass)
        if attach.duration:
            print >>out, '<span class="duration">(%d:%02d)</span>' % (int(attach.duration)/60,
                                                             attach.duration%60)
        print >>out, '</div>'
    print >>out, '</div>'
    return out.getvalue()

def renderThread(thread, limit=None):
    out = StringIO()
    print >>out, '<div id="thread-%d" class="thread%s">' % (thread.id, thread.unread and ' unread' or '')

    print >>out, '<div class="who">'
    inbox = thread.inbox
    peer = thread.peer
    print >>out, '<span class="phone">%s</span>' % peer.phone_number
    if peer.display_name:
        print >>out, '<span class="name">%s</span>' % peer.display_name
    locStr = ''
    for part in [peer.from_city, peer.from_state, peer.from_country]:
        if part:
            if locStr: locStr += ', '
            locStr += part
    if locStr:
        print >>out, '<span class="location">%s</span>' % locStr
    print >>out, '<span class="inbox">%s (%s)</span>' % (inbox.phone_number, inbox.name)
    print >>out, '<div class="footer"></div>'
    print >>out, '</div>'

    print >>out, '''<div class="respond">
<form method="POST" action="sendmsg.py" class="sms">
<input type="hidden" name="From" value="%s">
<input type="hidden" name="To" value="%s">
<input type="text" class="sms" name="Body" maxlength="1600" placeholder="Respond by text message">
</form>
</div>''' % (inbox.phone_number, peer.phone_number)

    print >>out, '<div class="events">'
    for event in thread.events.limit(limit):
        print >>out, renderEvent(event)
    if limit and thread.events.count() > limit:
        print >>out, '<a class="more" href="?t=%d">&hellip;</a>' % thread.id
    print >>out, '</div>'

    print >>out, '<div class="footer"></div>'

    print >>out, '</div>'
    return out.getvalue()

def renderUserBox():
    out = StringIO()
    print >>out, '<div id="user">Welcome, %s!' % user.username
    print >>out, '<ul class="actions"><li><a href="session.py/logout">log out</a></li></ul>'
    return out.getvalue()

if __name__ == '__main__':
    argv = session.argv()
    if len(argv) < 3:
        print """Status: 400 Bad Request
Content-type: text/html

The request was nonsensical."""
        sys.exit()

    try:
        form = session.form()
        if argv[1] == 't':
            thread = Conversation.get(Conversation.user == user and Conversation.id == int(argv[2]))
            buf = renderThread(thread)
        elif argv[1] == 'e':
            event = Event.get(Event.inbox.user == user and Event.id == int(argv[2]))
            buf = renderEvent(event)
        else:
            raise UnknownRequest
        print "Content-type: text/html;charset=utf-8\n\n"
        print buf
    except (Conversation.DoesNotExist,
            Event.DoesNotExist):
        print """Status: 404 Not Found
Content-type: text/html

The requested resource was not found."""
