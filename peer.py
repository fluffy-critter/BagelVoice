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

print '''<table id="addressbook">
<tr><th colspan="2">Number</th><th>Display Name</th><th colspan="2">Disposition</th></tr>
'''

for p in user.peers:
    print '''
<tr class="peer" id="peer-{pid}">
<td class="num"><a href=".?p={pid}">{num}</a></td>
<td class="loc">{loc}</td>
<td class="name"><input type="text" name="name" value="{displayName}" placeholder="Unnamed"></td>
<td class="block"><label for="block-{pid}">Block</label> <input type="checkbox" name="blocked" {blockChk} id="block-{pid}"></td>
<td class="vm"><label for="vm-{pid}">VM</label> <input type="checkbox" name="vm" {vmChk} id="vm-{pid}"></td>
</tr>
'''.format(pid=p.id,
           num=p.phone_number,
           loc=render.getPeerLocation(p),
           displayName=p.display_name or '',
           blockChk=p.blocked and 'checked="1"' or '',
           vmChk=p.send_to_voicemail and 'checked="1"' or '')

print '''
</table>
</body>
</html>
'''
