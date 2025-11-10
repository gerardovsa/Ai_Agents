"""
Slack API Implementation
Handles team communication, channels, and file management
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

class SlackTools:
    def __init__(self):
        """Initialize Slack client"""
        self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    
    def post_message(self, channel, text, **kwargs):
        """Post message to channel"""
        return self.client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=kwargs.get('thread_ts'),
            blocks=kwargs.get('blocks'),
            attachments=kwargs.get('attachments'),
            username=kwargs.get('username'),
            icon_emoji=kwargs.get('icon_emoji'),
            icon_url=kwargs.get('icon_url')
        )
    
    def update_message(self, channel, ts, text, **kwargs):
        """Update existing message"""
        return self.client.chat_update(
            channel=channel,
            ts=ts,
            text=text,
            blocks=kwargs.get('blocks')
        )
    
    def delete_message(self, channel, ts, **kwargs):
        """Delete message"""
        return self.client.chat_delete(
            channel=channel,
            ts=ts
        )
    
    def list_channels(self, **kwargs):
        """List channels"""
        return self.client.conversations_list(
            exclude_archived=kwargs.get('exclude_archived', True),
            limit=kwargs.get('limit', 100)
        )
    
    def create_channel(self, name, **kwargs):
        """Create channel"""
        return self.client.conversations_create(
            name=name,
            is_private=kwargs.get('is_private', False)
        )
    
    def invite_to_channel(self, channel, users, **kwargs):
        """Invite users to channel"""
        return self.client.conversations_invite(
            channel=channel,
            users=','.join(users)
        )
    
    def upload_file(self, **kwargs):
        """Upload file"""
        return self.client.files_upload(
            channels=kwargs.get('channels'),
            content=kwargs.get('content'),
            filename=kwargs.get('filename'),
            filetype=kwargs.get('filetype'),
            title=kwargs.get('title'),
            initial_comment=kwargs.get('initial_comment')
        )
    
    def add_reaction(self, channel, timestamp, name, **kwargs):
        """Add reaction to message"""
        return self.client.reactions_add(
            channel=channel,
            timestamp=timestamp,
            name=name
        )

# Export tool functions
def slack_post_message(**kwargs):
    tools = SlackTools()
    return tools.post_message(**kwargs)

def slack_update_message(**kwargs):
    tools = SlackTools()
    return tools.update_message(**kwargs)

def slack_delete_message(**kwargs):
    tools = SlackTools()
    return tools.delete_message(**kwargs)

def slack_list_channels(**kwargs):
    tools = SlackTools()
    return tools.list_channels(**kwargs)

def slack_create_channel(**kwargs):
    tools = SlackTools()
    return tools.create_channel(**kwargs)

def slack_invite_to_channel(**kwargs):
    tools = SlackTools()
    return tools.invite_to_channel(**kwargs)

def slack_upload_file(**kwargs):
    tools = SlackTools()
    return tools.upload_file(**kwargs)

def slack_add_reaction(**kwargs):
    tools = SlackTools()
    return tools.add_reaction(**kwargs)
