#!/usr/bin/python

"""A notifier mechanism that sends notifications about stuff.

Eventually this module will be replaced by the notifier bot/jabber console.
"""

from config import configuration
import model
from model import NotificationQueue, CnamLookupQueue
import os
import datetime
import time
import timeutil
import logging
import smtplib
import opencnam

# TODO make the background notifier not write to one old logfile in perpetuity
logger = logging.getLogger(__name__)

threads = {}

def sendEmail(msg):
    logger.info("Sending email from %s to %s", msg['fromName'], msg['toAddr'])

    text = """\
From: {fromAddr}\r
To: {toAddr}\r
Subject: {msgtype} from {fromName}\r
\r
{body}\r
\r
To view or reply, visit: {view}?t={tid}\r
"""

    if msg['text'] and msg['voice']:
        msgtype='Messages'
    elif msg['text']:
        msgtype='Text message'
        if msg['text'] > 1:
            msgtype += 's'
    elif msg['voice']:
        msgtype='Call'
        if msg['voice'] > 1:
            msgtype += 's'

    # TODO configurable connection (auth, tls, et al)
    smtp = smtplib.SMTP()
    smtp.connect()
    smtp.sendmail(msg['fromAddr'],
                  msg['toAddr'],
                  text.format(fromAddr=msg['fromAddr'],
                              toAddr=msg['toAddr'],
                              fromName=msg['fromName'],
                              msgtype=msgtype,
                              body=msg['body'],
                              view=configuration['root-url'],
                              tid=msg['tid']))
    smtp.quit()

def addEmail(uri, event):
    conf = configuration['notify']['mailto']
    fromAddr = conf['from']
    toAddr = uri.split(':')[1]
    peer = event.conversation.peer
    if peer.display_name:
        fromName = '%s (%s)' % (peer.display_name, peer.phone_number)
    else:
        fromName = peer.phone_number

    if threads.has_key(event.conversation.id):
        logger.info("Appending to tid=%s", event.conversation.id)
        msg = threads[event.conversation.id]
    else:
        logger.info("New thread for tid=%s", event.conversation.id)
        msg = {'fromAddr': fromAddr,
               'toAddr': toAddr,
               'fromName': fromName,
               'tid': event.conversation.id,
               'body': '',
               'text': 0,
               'voice': 0
        }

    if event.type == 'text':
        msg['text'] += 1
        mediaType = 'Attachment'
    else:
        msg['voice'] += 1
        mediaType = 'Voicemail'

    body = event.time.strftime("At %x %H:%M:\r\n")
    if event.message_body:
        body += "%s\r\n" % event.message_body

    for attach in event.media:
        body += "{mediaType} (%s%s): %s\r\n" % (attach.mime_type,
                                              (attach.duration and
                                               ', %d:%02d' % (attach.duration/60,
                                                              attach.duration%60)
                                               ) or '',
                                              attach.url)
        if attach.transcription:
            body += "Transcript:\r\n\r\n%s\r\n\r\n" % attach.transcription

    body += "\r\n"
    msg['body'] += body

    threads[event.conversation.id] = msg    

def handleEvents():
    """Handle all of the events in the past.
    
    Returns the number of milliseconds until the next time to check the queue.
    """
    nextTime = None
    for item in NotificationQueue.select().where(NotificationQueue.handled == False).order_by(NotificationQueue.time):
        now = datetime.datetime.now()
        if item.time > now:
            interval = item.time - now
            nextTime = interval.seconds + interval.microseconds*1e-6
            break

        uri = item.notification.uri
        event = item.event
        logger.info("uri=%s event.id=%d event.type=%s", uri, event.id, event.type)

        try:
            schema = uri.split(':')[0]
            if schema == 'mailto':
                addEmail(uri, event)
            else:
                logger.warning("Unknown protocol %s for URI %s", schema, uri)

            item.handled = True
            item.save()
        except:
            if item.retries_left > 0:
                logger.exception("Got exception trying to handle %s; retrying in %d milliseconds", uri, item.retry_wait)
                item.retries_left -= 1
                item.time = now + datetime.timedelta(milliseconds=item.retry_wait)
                item.retry_wait += item.retry_wait
            else:
                logger.exception("Got exception trying to handle %s; giving up", uri)
                item.handled = True
            item.save()

    num =  NotificationQueue.delete().where(NotificationQueue.handled == True).execute()
    if num:
        logger.info("Completed %d notifications", num)

    if len(threads):
        logger.info("Have %d threads to notify about", len(threads))
    for tt in threads:
        logger.info("thread: %d", tt)
        sendEmail(threads[tt])

    for item in CnamLookupQueue.select().where(CnamLookupQueue.handled == False):
        peer = item.peer
        if not peer.display_name:
            user = peer.user
            try:
                phone = opencnam.Phone(peer.phone_number,
                                       account_sid=user.opencnam_sid,
                                       auth_token=user.opencnam_auth_token)
                if phone.cnam:
                    peer.display_name = phone.cnam
                    peer.save()
            except opencnam.errors.InvalidPhoneNumberError:
                logger.warn("Invalid phone number %s", peer.phone_number)
        item.handled = True
        item.save()

    num = CnamLookupQueue.delete().where(CnamLookupQueue.handled == True).execute()
    if num:
        logger.info("Completed %d CNAM lookups", num)

    return min(nextTime, 15) or 15

if __name__ == '__main__':
    # If we're running as a daemon, just quietly sit around in the
    # background, sending out messages
    #while True:
    #    nextWait = None
    #    try:
            nextWait = handleEvents()
    #    except:
    #        logger.exception("Got exception handling pending notifications")
    #    time.sleep(nextWait or 3)
