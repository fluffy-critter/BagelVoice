#!/usr/bin/python

import session
from model import *
from cStringIO import StringIO

user = session.get_user()

def renderEvent(event):
    out = StringIO()
    if event.inbound:
        print >>out, '<div class="event inbound">'
    else:
        print >>out, '<div class="event outbound">'

    if event.status:
        print >>out, '<div class="status stat-%s">%s</div>' % (
            event.status,
            event.status
            )

    print >>out, '<div class="when">%s</div>' % event.time.strftime('%x %X')

    if event.call_duration:
        print >>out, '<div class="call">Call, %d seconds</div>' % event.call_duration

    if event.message_body:
        print >>out, '<div class="text">%s</div>' % event.message_body
    elif event.type:
        print >>out, '<div class="type">%s</div> ' % event.type

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
    print >>out, '<div id="thread-%s" class="thread%s">' % (thread.id, thread.unread and ' unread' or '')

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
    print >>out, '</div>'

    print >>out, '''<div class="respond">
<form method="POST" action="sendmsg.py">
<input type="hidden" name="From" value="%s">
<input type="hidden" name="To" value="%s">
<input type="text" size="80" name="Body">
<input type="submit" value="Send">
</form>
</div>''' % (inbox.phone_number, peer.phone_number)

    print >>out, '<div class="events">'
    for event in thread.events.limit(limit):
        print >>out, renderEvent(event)
    if limit and thread.events.count() > limit:
        print >>out, '<div class="more">&hellip;</div>'
    print >>out, '</div>'

    print >>out, '<div class="footer"></div>'

    print >>out, '</div>'
    return out.getvalue()

class NotAuthorized(Exception): pass
class UnknownRequest(Exception): pass

if __name__ == '__main__':
    try:
        form = session.get_form()
        if form.getfirst('t'):
            thread = Conversation.get(Conversation.id == int(form.getfirst('t')))
            if thread.user.id != user.id: # TODO probably a safer way of doing this...
                raise NotAuthorized
            buf = renderThread(thread)
        elif form.getfirst('e'):
            event = Event.get(Event.id == int(form.getfirst('e')))
            if event.conversation.user.id != user.id:
                raise NotAuthorized
            buf = renderEvent(event)
        else:
            raise UnknownRequest
        print "Content-type: text/html;charset=utf-8\n\n"
        print buf
    except NotAuthorized:
        print """Status: 403 Forbidden
Content-type: text/html

You are not authorized to view this resource."""
    except UnknownRequest:
        print """Status: 400 Bad Request
Content-type: text/html

The request was nonsensical."""
    except (Conversation.DoesNotExist,
            Event.DoesNotExist):
        print """Status: 404 Not Found
Content-type: text/html

The requested resource was not found."""
