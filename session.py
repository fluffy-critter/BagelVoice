import model
from model import WebSession, User
import cgi
import Cookie
import os
import timeutil
import logging
import bcrypt
import uuid
import sys

logger = logging.getLogger(__name__)

_form = cgi.FieldStorage()
ipAddr = os.getenv('REMOTE_ADDR')

_user = None

def form():
    # Gets the parsed CGI form values. MUST be retrieved from here.
    global _form
    return _form

# Get the page action; argv[0] is a server-relative path to the script handler, argv[1..n] is the verb
# i.e. /larry/foo.py/handleBlah/more -> ['/larry/foo.py', 'handleBlah', 'more']
def argv():
    argv=[os.getenv('SCRIPT_NAME')]
    path=os.getenv('PATH_INFO')
    if path:
        argv.extend(path.split('/')[1:])
    return argv

def request_url():
    # try to reconstruct our URL from what we're given, because a
    # Location header has to be absolute to prevent Apache from
    # short-circuiting incorrectly
    https = (os.getenv('HTTPS') == 'on')
    expectedPort = https and '443' or '80'
    actualPort = os.getenv('SERVER_PORT')
    return '%s://%s%s%s' % (https and 'https' or 'http',
                            os.getenv('SERVER_NAME'),
                            (expectedPort != actualPort) and ':%s'%actualPort or '',
                            os.getenv('REQUEST_URI'))


def user(doLogin=True):
    global _user
    if _user:
        return _user

    # Get the currently logged-in user, or presents a login form and
    # exits if there is none
    cookie = Cookie.SimpleCookie()
    cookie_string = os.environ.get('HTTP_COOKIE')
    if cookie_string:
        cookie.load(cookie_string)

    # check for an existing valid session, and return the user if so
    # TODO also clean up stale cookies at some point
    session_cookie = cookie.get('session', None)
    if session_cookie:
        try:
            sess = WebSession.get(WebSession.session_id == session_cookie.value)
            sess.last_seen = timeutil.getTime()
            sess.last_ip = ipAddr
            sess.save()
            _user = sess.user
            return _user
        except WebSession.DoesNotExist:
            logger.info('Got invalid session id "%s" for request %s', session_cookie.value, os.getenv('REQUEST_URI'))

    login_error_string = None
    if _form.getfirst('username') and _form.getfirst('password'):
        user = User.get(username=_form.getfirst('username'))
        if bcrypt.hashpw(_form.getfirst('password'), user.password) == user.password:
            # Login succeeded
            sess = WebSession.create(session_id=uuid.uuid4().hex,
                                     user=user,
                                     last_ip=ipAddr,
                                     last_seen = timeutil.getTime())
            cookie['session'] = sess.session_id
            cookie['session']['expires'] = 86400*14
            print cookie
            print '''\
Content-type: text/html
Location: %s

Redirecting...''' % request_url()
            sys.exit()
        else:
            # Login failed; set an error string to that effect
            login_error_string = "Username/password did not match our records"

    if (doLogin == False):
        print """Status: 401 unauthorized\nContent-type: text/plain\n\nYou gotta be logged in for this to work"""
        sys.exit()

    print """Content-type: text/html

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="style.css">
<title>Login required</title>
</head><body class="loginForm">

<div id="login">"""
    if login_error_string:
        print '<div class="error">%s</div>' % login_error_string
    else:
        print '<div class="explain">You must log in to continue.</div>'
    print '<form method="POST" action="%s"><ul>' % os.environ.get('REQUEST_URI')
    print '<li><label for="username">Username:</label>'
    print '<input type="text" name="username" value="%s"></li>' % (_form.getfirst('username') or '')
    print """<li><label for="password">Password:</label>
<input type="password" name="password"></li>
</ul><input type="submit" value="Log in"></form>
</div></body></html>"""
    sys.exit()

