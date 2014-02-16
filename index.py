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

<table>
<tr><th>From</th><th>To</th><th>Status</th></tr>
"""

for msg in user.

print """
</table>
"""

<h2>Recent Calls</h2>

<table>
<tr><th>From</th><th>To</th><th>Status</th><th>Duration</th></tr>
"""
for call in user.calls.order_by(model.VoiceCall.lastevent.desc()):
    print '<tr class="call%s"><td>%s</td><td>%s</td><td>%s</td><td>%d:%02d</td></tr>' % (
        call.msg_new and " unread",
        call.call_from,
        call.call_to,
        call.call_status,
        int(call.call_duration/60), int(call.call_duration%60)
        )
    for vm in call.recordings:
        print '<tr class="voicemail%s"><td colspan=4>' % (vm.msg_new and " unread")
        print '<a href="%s">voicemail (%d:%02d)' % (
            vm.url, int(vm.duration/60), int(vm.duration%60)
            )
        print '</td></tr>'

print '</table>'

print """
</body></html>
"""

    

