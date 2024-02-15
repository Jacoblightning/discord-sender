class OtherUser:
    def __init__(
        self,
        user_id: str,
        username: str | None = None,
        global_name: str | None = None,
        is_bot: bool = False,
    ):
        self.user_id: str = user_id
        self.username: str | None = username
        self.is_bot = is_bot
        self.global_name: str = global_name

    def __repr__(self):
        return f"{self.user_id}: {self.username}{('/' + self.global_name) if self.global_name else ''}"

    def strict_equality_check(self, other) -> bool:
        try:
            if self != other:
                return False
            if self.username == other.username:
                return True
            return False
        except AttributeError:
            return False

    def __eq__(self, other):
        try:
            if not isinstance(other, OtherUser):
                return False
            if self.user_id != other.user_id:
                return False
            if self.is_bot != other.is_bot:
                return False
            if self.global_name != other.global_name:
                return False
            return True
        except AttributeError:
            return False
