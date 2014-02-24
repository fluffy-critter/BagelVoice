"""Useful backfill functions."""

from model import *
import datetime
from twilio.rest import TwilioRestClient

def getClient(user):
    return TwilioRestClient(user.twilio_sid, user.twilio_auth_token)


def makePeer(user, phone_number):
    try:
        return Peer.get(Peer.user == user and Peer.phone_number == phone_number)
    except Peer.DoesNotExist:
        return Peer.create(user=user,
                           phone_number = phone_number)

def makeConversation(inbox, peer):
    try:
        return Conversation.get(Conversation.inbox == inbox and Conversation.peer == peer)
    except Conversation.DoesNotExist:
        return Conversation.create(user=inbox.user,
                                   inbox=inbox,
                                   peer=peer,
                                   last_update=datetime.datetime.fromtimestamp(0),
                                   unread=False)

def makeCallEvent(conversation, call, inbound):
    try:
        event = Event.get(Event.inbox == conversation.inbox and Event.sid == call.sid)
    except Event.DoesNotExist:
        event = Event.create(sid=call.sid,
                             inbox=conversation.inbox,
                             conversation=conversation,
                             type='voice',
                             inbound=inbound,
                             time=datetime.datetime.strptime(call.start_time or call.date_created, '%a, %d %b %Y %H:%M:%S +0000'),
                             last_update=datetime.datetime.strptime(call.date_updated or call.end_time or call.start_time, '%a, %d %b %Y %H:%M:%S +0000'))
    event.call_duration=call.duration and int(call.duration)
    event.status = call.status
    event.save()
    conversation.last_update = max(conversation.last_update, event.last_update)
    conversation.save()
    return event

def makeMessageEvent(conversation, message, inbound):
    try:
        event = Event.get(Event.inbox == conversation.inbox and Event.sid == message.sid)
    except Event.DoesNotExist:
        event = Event.create(sid=message.sid,
                             inbox=conversation.inbox,
                             conversation=conversation,
                             type='text',
                             inbound=inbound,
                             time=datetime.datetime.strptime(message.date_created, '%a, %d %b %Y %H:%M:%S +0000'),
                             last_update=datetime.datetime.strptime(message.date_updated, '%a, %d %b %Y %H:%M:%S +0000'))
    event.status = message.status
    event.message_body = message.body
    event.save()
    conversation.last_update = max(conversation.last_update, event.last_update)
    conversation.save()
    return event

def makeVoicemail(call, vm):
    try:
        return Attachment.get(Attachment.sid == vm.sid)
    except Attachment.DoesNotExist:
        return Attachment.create(sid=vm.sid,
                                 event=call,
                                 duration=vm.duration,
                                 url=vm.uri + '.mp3',
                                 mime_type='audio/mpeg',
                                 msg_new=False)

def makeNotificationType(user, uri):
    try:
        return Notification.get(Notification.user == user and Notification.uri == uri)
    except Notification.DoesNotExist:
        return Notification.create(user=user, uri=uri)
    
