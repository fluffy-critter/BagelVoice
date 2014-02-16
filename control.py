from model import *
import datetime

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

def getAssociate(form, user, whoField):
    try:
        assoc = Associate.get(Associate.user == user
                              and Associate.phone_number == form.getfirst(whoField))
    except Associate.DoesNotExist:
        assoc = Associate()
        assoc.user = user
        assoc.phone_number = form.getfirst(whoField)
    if applyAttribs(assoc, form, {
            'FromCity'   : 'from_city',
            'FromState'  : 'from_state',
            'FromZip'    : 'from_zip',
            'FromCountry': 'from_country'
            }):
        assoc.save()
    return assoc

def getConversation(form, inbox, associate):
    # TODO create a new conversation if the old one's too old
    try:
        conv = Conversation.get(Conversation.inbox == inbox
                                and Conversation.associate == associate)
    except Conversation.DoesNotExist:
        conv = Conversation.create(
            user = inbox.user,
            inbox = inbox,
            last_update = datetime.datetime.now(),
            associate = associate)
    return conv
        
def getEvent(form, sidField, inbound):
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
        associate = getAssociate(form, inbox.user, whoField)
        now = datetime.datetime.now()
        conversation = getConversation(form, inbox, associate)
        
        event = Event.create(
            sid=form.getfirst(sidField),
            inbound=inbound,
            inbox=inbox,
            conversation=conversation,
            time=now,
            last_update=now,
            )
        conversation.last_update = now
        conversation.unread = now
        conversation.save()
        
    if applyAttribs(event, form, {
        'CallStatus': 'status',
        'MessageStatus': 'status',
        'CallDuration': 'duration',
        'Body': 'message_body',
        }):
        event.save()

    return event

        
            
