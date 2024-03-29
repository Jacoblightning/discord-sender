from .other import OtherUser
from .tools import ziplist


class Channel:
    def __init__(
        self,
        channel_id: str,
        recipients: list[OtherUser],
        chan_type: int = 1,
        is_in_server: bool = False,
        name: str | None = None,
    ):
        self.channel_id: str = channel_id
        self.is_in_server: bool = is_in_server
        self.recipients: list[OtherUser] = recipients
        self.to = {user.username: user for user in recipients}
        self.type: int = chan_type
        self.name: str = name
        if chan_type == 1:
            self.channel_type: str = "DM"
        elif chan_type == 3:
            self.channel_type: str = None
        else:
            self.channel_type: str = "unknown"

    @staticmethod
    def strict_equality_check(first, second):
        try:
            if first != second:
                return False
            if first.to != second.to:
                return False
            if first.name != second.name:
                return False
            if first.channel_type != second.channel_type:
                return False
            return True
        except AttributeError:
            return False

    def __eq__(self, other: object) -> bool:
        try:
            if not isinstance(other, Channel):
                return False
            if self.channel_id != other.channel_id:
                return False
            if self.is_in_server != other.is_in_server:
                return False

            if len(self.recipients) != len(other.recipients):
                return False
            zipped = ziplist(self.recipients, other.recipients)
            if len(zipped) != len(other.recipients):
                return False
            for recp1, recp2 in zipped:
                if recp1 != recp2:
                    return False

            if self.type != other.type:
                return False
            return True
        except AttributeError:
            return False
