#!/usr/bin/python

import cgi
import session
import model
import render
import config
import info

user = session.get_user()

print """Content-type: text/html

<!DOCTYPE html>
<html>
<head>
<title>VoiceBox</title>
<link rel="stylesheet" href="style.css">

<script src="js/jquery.min.js"></script>
<script src="js/index.js"></script>

</head><body class="dashboard">

<h1>Voicebox</h1>

<h2>Messages</h2>

<div class="threads">
"""

for thread in user.threads:
    print render.renderThread(thread)

print '<script>pollForUpdates("%s/info.py", %d);</script>' % (config.configuration['root-url'], info.lastitem())
print '</body></html>'

    

