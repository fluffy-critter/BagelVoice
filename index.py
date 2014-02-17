#!/usr/bin/python

import cgi
import cgitb
import session
import model

user = session.get_user()

print """Content-type: text/html

<!DOCTYPE html>
<html>
<head>
<title>VoiceBox</title>
<link rel="stylesheet" href="style.css">
</head><body class="dashboard">

<h1>Voicebox</h1>

<h2>Messages</h2>

<div class="threads">
"""

for thread in user.threads:
    print '<div class="thread">'

    print '<div class="who">'
    inbox = thread.inbox
    associate = thread.associate
    print '<span class="phone">%s</span>' % associate.phone_number
    if associate.display_name:
        print '<span class="name">%s</span>' % associate.display_name
    locStr = ''
    for part in [associate.from_city, associate.from_state, associate.from_country]:
        if part:
            if locStr: locStr += ', '
            locStr += part
    if locStr:
        print '<span class="location">%s</span>' % locStr
    print '<span class="inbox">%s (%s)</span>' % (inbox.phone_number, inbox.name)
    print '</div>'

    print '''<div class="respond">
<form method="POST" action="sendmsg.py">
<input type="hidden" name="From" value="%s">
<input type="hidden" name="To" value="%s">
<input type="text" size="80" name="Body"></textarea>
<input type="submit" value="Send">
</form>
</div>''' % (inbox.phone_number, associate.phone_number)

    print '<div class="events">'
    for event in thread.events:
        if event.inbound:
            print '<div class="event inbound">'
        else:
            print '<div class="event outbound">'

        if event.status: print '<div class="status stat-%s">%s</div>' % (
                event.status,
                event.status
                )
            
        print '<div class="when">%s</div>' % event.time.strftime('%x %X')

        if event.call_duration:
            print '<div class="call">Call, %d seconds</div>' % event.call_duration
        
        if event.message_body:
            print '<div class="text">%s</div>' % event.message_body
	elif event.type:
            print '<div class="type">%s</div> ' % event.type

        for attach in event.media:
            print '<div class="media">'
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
                print '<div class="attachbody">%s</div>' % attachBody
            print '<a href="%s">original %s</a>' % (attach.url, mimeclass)
            if attach.duration:
                print '<span class="duration">(%d:%02d)</span>' % (int(attach.duration)/60,
                                                                 attach.duration%60)


            print '</div>'
        print '</div>'
    print '</div>'

    print '<div class="footer"></div>'
    print '</div>'
    
print """
</div>


</body></html>
"""

    

