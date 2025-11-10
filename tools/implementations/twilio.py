"""
Twilio Communications API Implementation
Handles SMS, voice, WhatsApp, video, and email
"""
from twilio.rest import Client
import os

class TwilioTools:
    def __init__(self):
        """Initialize Twilio client"""
        self.client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
    
    def send_sms(self, to, from_, body, **kwargs):
        """Send SMS message"""
        return self.client.messages.create(
            to=to,
            from_=from_,
            body=body,
            media_url=kwargs.get('media_url'),
            status_callback=kwargs.get('status_callback')
        )
    
    def get_message(self, message_sid):
        """Get message details"""
        return self.client.messages(message_sid).fetch()
    
    def list_messages(self, **kwargs):
        """List messages"""
        return self.client.messages.list(
            to=kwargs.get('to'),
            from_=kwargs.get('from'),
            date_sent=kwargs.get('date_sent'),
            limit=kwargs.get('limit', 50)
        )
    
    def make_call(self, to, from_, **kwargs):
        """Make voice call"""
        return self.client.calls.create(
            to=to,
            from_=from_,
            url=kwargs.get('url'),
            twiml=kwargs.get('twiml'),
            status_callback=kwargs.get('status_callback'),
            timeout=kwargs.get('timeout', 60)
        )
    
    def send_whatsapp(self, to, from_, body, **kwargs):
        """Send WhatsApp message"""
        return self.client.messages.create(
            to=to,
            from_=from_,
            body=body,
            media_url=kwargs.get('media_url')
        )
    
    def create_video_room(self, unique_name, **kwargs):
        """Create video room"""
        return self.client.video.rooms.create(
            unique_name=unique_name,
            type=kwargs.get('type', 'group'),
            max_participants=kwargs.get('max_participants', 10),
            record_participants_on_connect=kwargs.get('record_participants_on_connect', False),
            status_callback=kwargs.get('status_callback')
        )

# Export tool functions
def twilio_send_sms(**kwargs):
    tools = TwilioTools()
    return tools.send_sms(**kwargs)

def twilio_get_message(**kwargs):
    tools = TwilioTools()
    return tools.get_message(**kwargs)

def twilio_list_messages(**kwargs):
    tools = TwilioTools()
    return tools.list_messages(**kwargs)

def twilio_make_call(**kwargs):
    tools = TwilioTools()
    return tools.make_call(**kwargs)

def twilio_send_whatsapp(**kwargs):
    tools = TwilioTools()
    return tools.send_whatsapp(**kwargs)

def twilio_create_video_room(**kwargs):
    tools = TwilioTools()
    return tools.create_video_room(**kwargs)
