from peewee import *

database = SqliteDatabase('db/voicebox.db')
database.connect()

class BaseModel(Model):
    class Meta:
        database = database

    @staticmethod
    def update_schema():
        ''' do nothing by default '''

class User(BaseModel):
    username = CharField(null=False,unique=True)
    password = CharField()
    email = CharField(unique=True)
    twilio_sid = CharField(unique=True)
    twilio_auth_token = CharField()
                    
class WebSession(BaseModel):
    session_id = CharField(unique=True)
    user = ForeignKeyField(User, related_name='web_sessions')
    last_ip = CharField()
    last_seen = DateTimeField()

class Inbox(BaseModel):
    owner = ForeignKeyField(User, related_name='inboxes')
    phone_number = CharField(unique=True)
    name = CharField()
    voicemail_greeting = CharField()

class ForwardingRule(BaseModel):
    id = PrimaryKeyField()
    inbox = ForeignKeyField(Inbox, related_name='forwarding_rules')
    name = CharField();
    
    max_ring_time = IntegerField(null=True)
    # destination type; must be something supported by TwiML (e.g. Number, Sip)
    dest_type = CharField()
    dest_addr = CharField()
    active = BooleanField(default=True)

class VoiceCall(BaseModel):
    sid = CharField(unique=True)
    
    account = ForeignKeyField(User, related_name='calls')
    starttime = DateTimeField(index=True)
    lastevent = DateTimeField()
    msg_new = BooleanField(default=True)
    
    call_from = CharField()
    call_to = ForeignKeyField(Inbox, related_name='calls')
    call_status = CharField()

    caller_id_string = CharField(null=True)
    from_city = CharField(null=True)
    from_state = CharField(null=True)
    from_zip = CharField(null=True)
    from_country = CharField(null=True)

    call_duration = IntegerField(null=True)

class Voicemail(BaseModel):
    sid = CharField(unique=True)
    duration = IntegerField()
    url = CharField()
    call = ForeignKeyField(VoiceCall, related_name='recordings')
    msg_new = BooleanField(default=True)

class TextMessage(BaseModel):
    sid = CharField(unique=True)
    inbox = ForeignKeyField(Inbox, related_name='texts')
    time = DateTimeField(index=True)
    msg_new = BooleanField(default=True)

    msg_with = CharField()
    msg_from = CharField()
    msg_to = CharField()
    msg_body = CharField()

    from_city = CharField(null=True)
    from_state = CharField(null=True)
    from_zip = CharField(null=True)
    from_country = CharField(null=True)

class TextAttachment(BaseModel):
    message = ForeignKeyField(TextMessage, related_name='attachments')
    content_type = CharField()
    content_url = CharField()

def create_tables():
    for table in [
        User,
        WebSession,
        Inbox,
        ForwardingRule,
        VoiceCall,
        Voicemail,
        TextMessage,
        TextAttachment]:
        table.create_table(fail_silently=True)
        table.update_schema()

        
        
