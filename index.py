#!/usr/bin/python

import session
user = session.user()

from model import *
import render

print render.pageHead()

print """<body class="dashboard">

<h1>Bagel Voice</h1>

<div id="status"></div>

<div id="inbox">
"""

form = session.form()
if form.getfirst('t'):
    thread = Conversation.get(Conversation.user == user and Conversation.id == int(form.getfirst('t')))
    print '<h2>Viewing thread</h2>'
    print '<div><a class="return" href="?">Back to inbox</a></div>'
    print render.renderThread(thread)
else:
    count=0
    for thread in user.threads.limit(20):
        if count == 0: limit=10
        elif count < 5: limit=5
        elif count < 10: limit = 3
        else: limit = 1
        ++count
        print render.renderThread(thread, limit)
print '</div>'

print '</body></html>'

    

