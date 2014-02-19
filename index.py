#!/usr/bin/python

import cgi
import session
from model import *
import render
import config
import async

user = session.get_user()
form = session.get_form()

print """Content-type: text/html

<!DOCTYPE html>
<html>
<head>
<title>VoiceBox</title>
<link rel="stylesheet" href="style.css">

<script src="js/jquery.min.js"></script>
<script src="js/sitefuncs.js"></script>

</head><body class="dashboard">

<h1>VoiceBox</h1>

<div class="threads">
"""

if form.getfirst('t'):
    thread = Conversation.get(Conversation.user == user and Conversation.id == int(form.getfirst('t')))
    print '<h2>Viewing thread</h2>'
    print '<a class="back" href="?">Back to inbox</a>'
    print render.renderThread(thread)
else:
    count=0
    for thread in user.threads:
        if count == 0: limit=10
        elif count < 5: limit=5
        elif count < 10: limit = 3
        else: limit = 1
        ++count
        print render.renderThread(thread, limit)
print '</div>'

print '<script>pollForUpdates(%d);</script>' % (async.lastitem())
print '</body></html>'

    

