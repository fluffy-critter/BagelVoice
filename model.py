from peewee import *
import config


database = SqliteDatabase('db/bagel.db')
database.connect()

# Run inside a transaction
def transaction():
    return database.transaction()

class BaseModel(Model):
    class Meta:
        database = database

    @staticmethod
    def update_schema():
        ''' do nothing by default '''

class User(BaseModel):
    """A user, with a 1:1 mapping to a Twilio account."""
    username = CharField(null=False,unique=True)
    password = CharField()
    email = CharField(unique=True)
    twilio_sid = CharField(unique=True)
    twilio_auth_token = CharField()
    timezone = CharField(default='UTC')

class Notification(BaseModel):
    """Notification settings."""
    user = ForeignKeyField(User, related_name='notifications')
    # notification URI, e.g. mailto:foo@example.com, xmpp:foo@example.com, or aim:aolsystemmsg
    uri = CharField(unique=True)
    # Notify on an incoming SMS
    notify_sms = BooleanField(default=False)
    # Notify when a call is received
    notify_call_incoming = BooleanField(default=False)
    # Notify when a call is missed
    notify_call_missed = BooleanField(default=False)
    # Notify when a voicemail is received
    notify_voicemail = BooleanField(default=True)

class WebSession(BaseModel):
    """User login sessions."""
    session_id = CharField(unique=True)
    user = ForeignKeyField(User, related_name='web_sessions')
    last_ip = CharField()
    last_seen = DateTimeField()

class Inbox(BaseModel):
    """An inbox, i.e. a phone number."""
    user = ForeignKeyField(User, related_name='inboxes')
    phone_number = CharField(unique=True)
    name = CharField()
    voicemail_greeting = CharField(null=True)
    transcribe_voicemail = BooleanField(default=False)

class CallRoute(BaseModel):
    """Routes for a call to take"""
    inbox = ForeignKeyField(Inbox, related_name='routes')
    name = CharField();
    
    max_ring_time = IntegerField(null=True)
    # destination type; must be something supported by TwiML (e.g. Number, Sip)
    dest_type = CharField()
    dest_addr = CharField()
    active = BooleanField(default=True)

    class Meta:
        indexes = (
            (('inbox', 'dest_type', 'dest_addr'), True),
            )

class CallRouteRule(BaseModel):
    """A rule for when to activate a call route."""
    route = ForeignKeyField(CallRoute, related_name='rules')
    # start time (in user's local timezone)
    start_time = TimeField()
    # end time (in user's local timezone); if end_time < start_time then this inverts the rule (i.e. only OUTSIDE this period)
    end_time = TimeField()
    # on which days to activate (string containing one or more of MTWRFSU)
    active_days = CharField()

class Peer(BaseModel):
    """Someone with whom a conversation occurs."""
    user = ForeignKeyField(User, related_name='peers')
    display_name = CharField(null=True)
    phone_number = CharField()
    blocked = BooleanField(default=False)
    send_to_voicemail = BooleanField(default=False)
    from_city = CharField(null=True)
    from_state = CharField(null=True)
    from_zip = CharField(null=True)
    from_country = CharField(null=True)

    class Meta:
        indexes = (
            # ensure that any given phone number only appears once
            (('user', 'phone_number'), True),
            )

class Conversation(BaseModel):
    """A conversation thread."""
    user = ForeignKeyField(User, related_name='threads')
    inbox = ForeignKeyField(Inbox, related_name='threads')
    peer = ForeignKeyField(Peer, related_name='threads')
    last_update = DateTimeField(index=True)
    unread = BooleanField(default=True)
    class Meta:
        indexes = (
            (('last_update','inbox','peer'),False),
            (('last_update','user','peer'),False),
            )
        order_by = ('-last_update',)    

class Event(BaseModel):
    """An event in a conversation."""
    sid = CharField(unique=True)
    inbox = ForeignKeyField(Inbox, related_name='events')
    conversation = ForeignKeyField(Conversation, related_name='events')
    type = CharField()
    time = DateTimeField()
    last_update = DateTimeField()
    inbound = BooleanField()
    call_duration = IntegerField(null=True)
    message_body = CharField(null=True)
    status = CharField(null=True)
    caller_id_string = CharField(null=True)
    class Meta:
        order_by = ('-time',)
    
# Queue of pending notifications
# while n=NotificationQueue.get() and n.time < now:
#   get event, notification
#   try:
#     handle notification
#     n.delete()
#   except:
#     if n.retries_left > 0:
#       n.time += datetime.timeinterval(milliseconds=n.retry_wait)
#       n.retry_wait += n.retry_wait
#       n.retries_left--
#       n.save()
class NotificationQueue(BaseModel):
    """A queue of pending notifications."""
    # when to next try the notification (NOTE: uses local datetime.now(), NOT the normalized timeutil time)
    time = DateTimeField(index=True)
    # if the event has been handled already
    handled = BooleanField(default=False)
    # the event to notify them about
    event = ForeignKeyField(Event, related_name='pending_notifications')
    # the notification method
    notification = ForeignKeyField(Notification, related_name='pending')
    # How many retries are left
    retries_left = IntegerField()
    # How long to wait before the next retry (exponential backoff), in milliseconds
    retry_wait = IntegerField()
    class Meta:
        order_by = ('time',)
        indexes = (
            (('event', 'notification'), True),
            (('handled',), False),
            )

class Attachment(BaseModel):
    sid = CharField(unique=True)
    duration = IntegerField(null=True)
    url = CharField()
    mime_type = CharField()
    event = ForeignKeyField(Event, related_name='media')
    transcription = CharField(null=True)
    msg_new = BooleanField(default=True)

def create_tables():
    for table in [
        User,
        Notification,
        WebSession,
        Inbox,
        CallRoute,
        CallRouteRule,
        Peer,
        Conversation,
        Event,
        NotificationQueue,
        Attachment
        ]:
        table.create_table(fail_silently=True)
        table.update_schema()

