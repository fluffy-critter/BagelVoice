from peewee import *

database = SqliteDatabase('voicebox.db')
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
    session_id = CharField(primary_key=True)
    user = ForeignKeyField(User, related_name='web_sessions')
    last_ip = CharField()
    last_seen = DateTimeField()
        
class Inbox(BaseModel):
    phone_number = CharField(unique=True)
    account = ForeignKeyField(User, related_name='inboxes')

class ForwardingRule(BaseModel):
    id = PrimaryKeyField()
    inbox = ForeignKeyField(Inbox, related_name='forwarding_rules')
    max_ring_time = IntegerField()
    # destination type; for now, Number or Sip
    dest_type = CharField()
    dest_addr = CharField()
    active = BooleanField()

class VoiceCall(BaseModel):
    call_sid = CharField(primary_key=True)
    account = ForeignKeyField(User, related_name='calls')
    time = DateTimeField(index=True)
    
    call_from = CharField()
    call_to = ForeignKeyField(Inbox, related_name='calls')
    call_status = CharField()

    caller_id_string = CharField()
    from_city = CharField()
    from_state = CharField()
    from_zip = CharField()
    from_country = CharField()

    call_duration = IntegerField()

class VoiceCallRecording(BaseModel):
    recording_sid = CharField(primary_key=True)
    recording_duration = IntegerField()
    recording_url = CharField()
    call = ForeignKeyField(VoiceCall, related_name='recordings')

class TextMessage(BaseModel):
    message_sid = CharField(primary_key=True)
    inbox = ForeignKeyField(Inbox, related_name='texts')
    time = DateTimeField(index=True)

    msg_from = CharField()
    msg_to = CharField()
    msg_body = CharField()

class TextAttachment(BaseModel):
    message = ForeignKeyField(TextMessage, related_name='attachments')
    content_type = CharField()
    content_url = CharField()

def init_schema():
    for table in [
        User,
        WebSession,
        Inbox,
        ForwardingRule,
        VoiceCall,
        VoiceCallRecording,
        TextMessage,
        TextAttachment]:
        table.create_table(fail_silently=True)
        table.update_schema()

        
        
