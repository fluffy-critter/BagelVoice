#!/usr/bin/python

import session
user = session.user()

from model import *
import render

print render.pageHead('Inbox')

print """<body class="dashboard">

<h1>Inbox</h1>

<div id="status"></div>

"""

form = session.form()
if form.getfirst('t'):
    thread = Conversation.get(Conversation.user == user and Conversation.id == int(form.getfirst('t')))
    print '<h2>Viewing thread</h2>'
    print '<div><a class="return" href="?">Back to inbox</a></div>'
    print render.renderThread(thread)
else:
    count=0
    threads = user.threads

    if form.getfirst('p'):
        peer = Peer.get(Peer.id == int(form.getfirst('p')))
        print '<h2>Showing conversations with {num}{who}</h2>'.format(
            num=peer.phone_number,
            who=peer.display_name and ' (%s)' % peer.display_name or '')
        print '<div><a class="return" href="?">Back to inbox</a></div>'
        threads = threads.where(Conversation.peer == peer)
    else:
        print '<h2>Showing all conversations</h2>'

    print '<div id="inbox">'
    for thread in threads:
        if count == 0: limit=10
        elif count < 5: limit=5
        elif count < 10: limit = 3
        else: limit = 1
        ++count
        print render.renderThread(thread, limit)
print '</div>'

print '</body></html>'

    

