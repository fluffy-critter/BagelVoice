#!/usr/bin/python

import session
user = session.get_user()

from model import *
import render

print """Content-type: text/html;charset=utf-8

<!DOCTYPE html>
<html>
<head>
<title>VoiceBox</title>
<link rel="stylesheet" href="style.css">

<script src="js/jquery.min.js"></script>
<script src="js/sitefuncs.js"></script>

</head><body class="dashboard">

<h1>VoiceBox</h1>

<div id="status"></div>

<div id="inbox">
"""

form = session.get_form()
if form.getfirst('t'):
    thread = Conversation.get(Conversation.user == user and Conversation.id == int(form.getfirst('t')))
    print '<h2>Viewing thread</h2>'
    print '<div><a class="return" href="?">Back to inbox</a></div>'
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

print '</body></html>'

    

