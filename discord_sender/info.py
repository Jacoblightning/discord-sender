from .discord_exceptions import ArgumentError


class DiscordLoginInfo:
    def __init__(
        self, *, token: str | None = None, cookie: None = None, uid: str | None = None
    ):
        if not token:  # Keep it until we have cookie auth
            raise ArgumentError("Token must be provided")
        if not (token or cookie):
            raise ArgumentError("either token or cookie is required")
        self.__token: str | None = token
        self.__cookie: None = cookie
        self.uid: str | None = uid
        self.preferred_method: str = "token"

    def get_token(self) -> str | None:
        return self.__token
