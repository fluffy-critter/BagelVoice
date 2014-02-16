#!/usr/bin/python

import cgi
import cgitb
import session
import model

if not session.get_user():
    exit()

print """Content-type: text/html

Hello world
"""

