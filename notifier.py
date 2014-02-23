#!/usr/bin/python
#
# A notifier mechanism that sends notifications about
# stuff. Eventually this module will be replaced by the notifier
# bot/jabber console.

from config import configuration
import model
from model import NotificationQueue
import os
import datetime
import time
import logging
import smtplib

# TODO make the background notifier not write to one old logfile in perpetuity
logger = logging.getLogger(__name__)

def sendEmail(uri, event):
    conf = configuration['notify']['mailto']
    fromAddr = conf['from']
    toAddr = uri.split(':')[1]
    peer = event.conversation.peer
    if peer.display_name:
        fromName = '%s (%s)' % (peer.display_name, peer.phone_number)
    else:
        fromName = peer.phone_number
    
    msg = "From: {fromAddr}\r\nTo: {toAddr}\r\n"
    if event.type == 'text':
        msg += "Subject: Text message from {fromName}\r\n"
        mediaType = 'Attachment'
    else:
        msg += "Subject: Call from {fromName}\r\n"
        mediaType = 'Voicemail'
    msg += "\r\n"

    if event.message_body:
        msg += "Message: {body}\r\n"

    for attach in event.media:
        msg += "{mediaType} (%s%s): %s\r\n" % (attach.mime_type,
                                              (attach.duration and
                                               ', %d:%02d' % (attach.duration/60,
                                                              attach.duration%60)
                                               ) or '',
                                              attach.url)
        if attach.transcription:
            msg += "Transcript:\r\n\r\n%s\r\n\r\n" % attach.transcription

    msg += "\r\nTo view or reply, visit: {view}?t={tid}\r\n"
    logger.info("Sending email from %s to %s", fromAddr, toAddr)
    # TODO configurable connection (auth, tls, et al)
    smtp = smtplib.SMTP()
    smtp.connect()
    smtp.sendmail(fromAddr, toAddr, msg.format(fromAddr=fromAddr,
                                               toAddr=toAddr,
                                               fromName=fromName,
                                               body=event.message_body,
                                               mediaType=mediaType,
                                               view=configuration['root-url'],
                                               tid=event.conversation.id))
    smtp.quit()

# Handle all of the events in the past; returns the number of milliseconds until the next time to check the queue
def handleEvents():
    nextTime = None
    for item in NotificationQueue.select().where(NotificationQueue.handled == False):
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
                sendEmail(uri, event)
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

    return min(nextTime, 15) or 15

if __name__ == '__main__':
    # If we're running as a daemon, just quietly sit around in the
    # background, sending out messages
    while True:
        nextWait = None
        try:
            nextWait = handleEvents()
        except:
            logger.exception("Got exception handling pending notifications")
        time.sleep(nextWait or 3)
