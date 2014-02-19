from model import *
import timeutil

def applyAttribs(obj, form, keyMapping):
    needsSave = False
    for k, v in keyMapping.items():
        if form.getfirst(k):
            needsSave = True
            setattr(obj, v, form.getfirst(k))
    return needsSave

def getUser(form):
    return User.get(User.twilio_sid == form.getfirst('AccountSid'))

def getInbox(form, user, inboxField):
    return Inbox.get(Inbox.user == user
                     and Inbox.phone_number == form.getfirst(inboxField))

def getPeer(form, user, whoField=None, whoValue=None):
    if whoValue:
        phone_number = whoValue
    else:
        phone_number = form.getfirst(whoField)
    try:
        peer = Peer.get(Peer.user == user
                              and Peer.phone_number == phone_number)
    except Peer.DoesNotExist:
        peer = Peer.create(user=user, phone_number=phone_number)
    if applyAttribs(peer, form, {
            'FromCity'   : 'from_city',
            'FromState'  : 'from_state',
            'FromZip'    : 'from_zip',
            'FromCountry': 'from_country'
            }):
        peer.save()
    return peer

def getConversation(form, inbox, peer):
    # TODO create a new conversation if the old one's too old
    try:
        conv = Conversation.get(Conversation.inbox == inbox
                                and Conversation.peer == peer)
    except Conversation.DoesNotExist:
        conv = Conversation.create(
            user = inbox.user,
            inbox = inbox,
            last_update = timeutil.getTime(),
            peer = peer)
    return conv

def getEvent(form, sidField, inbound, type):
    if inbound:
        whoField = 'From'
        inboxField = 'To'
    else:
        whoField = 'To'
        inboxField = 'From'
        
    try:
        event = Event.get(Event.sid == form.getfirst(sidField))
    except Event.DoesNotExist:
        user = getUser(form)
        inbox = getInbox(form, user, inboxField)
        peer = getPeer(form, inbox.user, whoField)
        now = timeutil.getTime()
        conversation = getConversation(form, inbox, peer)
        
        event = Event.create(
            sid=form.getfirst(sidField),
            inbound=inbound,
            inbox=inbox,
            conversation=conversation,
            time=now,
            last_update=now,
            type=type
            )
        conversation.last_update = now
        conversation.unread = True
        conversation.save()
   
    # there are several fields that could rightfully become 'status' and we want to guarantee precedence 
    save = False
    for field in ['CallStatus', 'DialCallStatus', 'MessageStatus']:
        if applyAttribs(event, form, { field : 'status' }):
            save = True    
    if applyAttribs(event, form, {
        'DialCallDuration': 'duration',
        'Body': 'message_body',
        }):
        save = True
    if save:
        event.save()

    # Attach any voicemail
    if form.getfirst('RecordingSid'):
        try:
            attach = Attachment.get(Attachment.sid==form.getfirst('RecordingSid'))
        except Attachment.DoesNotExist:
            attach = Attachment.create(sid=form.getfirst('RecordingSid'),
                                       url='%s.mp3' % form.getfirst('RecordingUrl'),
                                       mime_type = 'audio/mpeg',
                                       event=event)
        save = False
        if form.getfirst('RecordingDuration'):
            attach = duration=int(form.getfirst('RecordingDuration'))
            save = True
        if applyAttribs(attach, form, {
                'TranscriptionText' : 'transcription'
                }):
            save = True
        if save:
            attach.save()

    return event


