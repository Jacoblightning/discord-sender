from .other import OtherUser


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
            self.channel_type: str = "group"
        else:
            self.channel_type: str = "unknown"
