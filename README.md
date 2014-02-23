Bagel Voice
===========

What is it?
-----------

A simple telephony/switchboard web app that works with
[Twilio](http://twilio.com) and provides the following:

- Call forwarding with time-based rules

- Text message conversations, with inline MMS attachments

- Voicemail, with optional transcriptions

- A clean, simple user interface

- Configurable push notifications

Why "Bagel Voice?"
------------------

If seagulls fly over the sea, what flies over the bay? I don't want to swim in goo.

Why make this?
--------------

- I wanted to take more ownership in the services that I rely on
  (rather than being stuck with the monolithic existing cellphone,
  landline, or VoIP services)

- The various existing opensource offerings
  (e.g. [OpenVBX](http://openvbx.org)), while very good, don't fit my
  needs

- I also needed an excuse to finally learn Python

I want to and/or need help
--------------------------

For now, you can use the [issue tracker at
GitHub](https://github.com/plaidfluff/BagelVoice/issues).

Installation
============

Requirements
------------

As of right now (2/23/2014) it's very early in development. You will need the following:

- A webserver that is capable of running Python-based CGI scripts
- The following Python modules (all are installable via `pip`:
    - [pytz](http://pytz.sourceforge.net/)
    - [twilio](http://twilio.com/docs/python/install)
    - [peewee](https://github.com/coleifer/peewee)
- A bit of patience (knowing Python doesn't hurt)

Setup
-----

1. Get an account and phone number at [Twilio](http://twilio.com), if
   you haven't already

2. Put the Bagel Voice files into a directory that's servable by an
   httpd.  There is a `.htaccess` file included that will hopefully do
   what you need (namely, sets .py as a CGI-script extension). I also
   highly recommend running it under suexec (and on an SSL server, if
   possible). Also, make sure your db and logs directories are only
   readable by you. (Eventually these should be configurable to be
   outside of the site root directory. But, you know. Early in
   development.)

3. Copy `config.py.dist` to `config.py` and edit accordingly

4. Bootstrap the database; currently there's no UI for user creation or editing so you'll
  need to do something like the following:

    1. Copy bootstrap.py.example to bootstrap.py

    2. Fill in the appropriate information

    3. (Optional) Look at model.py to see what other sorts of things you can add in

    4. Run it with `python bootstrap.py`

5. Map the Twilio number with the following URLs:
    - Voice calls: `http://path/to/voice.py/enter-call`
    - SMS notifications: `http://path/to/sms.py/incoming`

6. Launch the notifier with `./run-notifier.sh` - you should also put
   this into a cron job that runs hourly or whatever

Note that for now, whenever the data model changes you'll have to
delete the database and rebuild it via:

    rm db/bagel.db && python bootstrap.py

Eventually, schema upgrades will be done more automatically (I hope)
but in the meantime, bootstrap does backfill your data from Twilio so
as long as you keep your call routes and rules and such in your
bootstrap script this isn't a huge deal.  (Obviously this will be
addressed later, but this software is just getting started!)

Future plans
============

- Auto-registration with Twilio

- Have an actual UI for user creation, editing, etc. (it should be so
  simple, my parents can use it)

- Replace the notification script with an asynchronous "command
  console" that's accessible via Jabber/XMPP (which will allow
  dialbacks, text conversations, etc. to occur via any IM client)

- Port it to an application framework such as
  [Flask](http://flask.pocoo.org/)