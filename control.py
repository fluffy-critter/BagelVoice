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

def getAssociate(form, user, whoField=None, whoValue=None):
    if whoValue:
        phone_number = whoValue
    else:
        phone_number = form.getfirst(whoField)
    try:
        assoc = Associate.get(Associate.user == user
                              and Associate.phone_number == phone_number)
    except Associate.DoesNotExist:
        assoc = Associate()
        assoc.user = user
        assoc.phone_number = phone_number
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
            last_update = timeutil.getTime(),
            associate = associate)
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
        associate = getAssociate(form, inbox.user, whoField)
        now = timeutil.getTime()
        conversation = getConversation(form, inbox, associate)
        
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
        
    if applyAttribs(event, form, {
        'CallStatus': 'status',
        'MessageStatus': 'status',
        'CallDuration': 'duration',
        'Body': 'message_body',
        }):
        event.save()

    return event
