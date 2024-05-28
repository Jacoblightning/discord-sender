import datetime
from .other import OtherUser
from .channel import Channel


class Message:
    def __init__(
            self,
            content: str,
            timestamp: datetime.datetime = None,
            sender: OtherUser = None,
            parent_channel: Channel = None,
            attachments: list = None,
            message_id: str = None
    ):
        self.content = content,
        self.timestamp = timestamp,
        self.sender = sender,
        self.parent = parent_channel,
        self.attachments = attachments,
        self.id = message_id

