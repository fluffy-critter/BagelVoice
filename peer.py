#!/usr/bin/python

from model import *
import session
import render
import sys

user = session.user()
form = session.form()

if form.getfirst('cmd') == 'edit':
    try:
        p = Peer.get(Peer.user == user, Peer.id == int(form.getfirst('p')))
    except Peer.DoesNotExist:
        print '''Status: 404 Not Found
Content-type: text/html

Unknown peer'''
        sys.exit()
    p.display_name = form.getfirst('name')
    p.blocked = not not form.getfirst('blocked')
    p.send_to_voicemail = not not form.getfirst('vm')
    p.save()

print render.pageHead("Address book")

print '<p class="back"><a href=".">Back to inbox</a></p>'

for p in user.peers:
    print '''
<div class="peer"><form method="POST" action="peer.py">
<input type="hidden" name="cmd" value="edit">
<input type="hidden" name="p" value="{pid}">
<a href=".?p={pid}">{num}</a>
<input type="text" name="name" value="{displayName}" placeholder="Display Name">
<label for="vm">Send to voicemail <input type="checkbox" name="vm" value="1" {vmCheck}"></label>
<label for="block">Block all calls <input type="checkbox" name="block" value="1" {blockCheck}"></label>
</form></div>
'''.format(pid=p.id,
           num=p.phone_number,
           displayName=p.display_name or '',
           vmCheck=p.send_to_voicemail and 'checked' or '',
           blockCheck=p.blocked and 'checked' or '')
