class OtherUser:
    def __init__(self, user_id: str, username: str | None = None, global_name: str | None = None, is_bot: bool = False):
        self.user_id: str = user_id
        self.username: str | None = username
        self.is_bot = is_bot
        self.global_name: str = global_name

    def __repr__(self):
        return f"{self.user_id}: {self.username}{('/'+self.global_name) if self.global_name else ''}"
