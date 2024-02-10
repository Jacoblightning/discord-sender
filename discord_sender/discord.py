import copy

import requests


class InvalidCredentialsException(Exception):
    pass


class ArgumentError(Exception):
    pass


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


class DiscordUser:
    DATA = {
        "login": "xxxxx@gmail.com",
        "password": "xxxxx",
        "undelete": False,
        "login_source": None,
        "gift_code_sku_id": None,
    }

    def __init__(self):
        self.user_info: DiscordLoginInfo | None = None
        self.__logged_in: bool = False
        self.session: requests.Session | None = None

    def login_with_credentials(self, email: str, password: str) -> None:
        self.session = requests.Session()
        self.session.get("https://discord.com/login")  # Get required cookie
        creds = copy.copy(self.DATA)  # Get a copy of the default data
        creds["login"] = email
        creds["password"] = password
        response: requests.Response = self.session.post(
            "https://discord.com/api/v9/auth/login", headers={}, json=creds
        )
        if not response.ok:
            error: dict[str, str] = response.json()["errors"]["login"]["_errors"][0]
            if error["code"] == "INVALID_LOGIN":
                raise InvalidCredentialsException(error["message"])
            raise requests.RequestException(
                f"Unknown error code from discord: {error['code']}"
            )
        user_data: dict[str, str | dict[str, str]] = response.json()
        self.user_info = DiscordLoginInfo(
            token=user_data["token"], uid=user_data["user_id"]
        )
        self.__logged_in: bool = True

    def login_with_token(self, token) -> None:
        self.user_info = DiscordLoginInfo(token=token)
        self.__logged_in = True
        self.session = requests.Session()

    def login_with_cookie(self, cookie: None):
        raise NotImplementedError("Cookie not implemented yet")  # TODO: Figure this out

    def send_message_to_channel(self, message: str, channel_id: str):
        if not self.__logged_in:
            raise InvalidCredentialsException("You need to login first")
        if not self.user_info.__token:
            raise NotImplementedError("Only token authentication can be used currently")
        heads = {"Authorization": self.user_info.__token}
        json_data = {
            "mobile_network_type": "unknown",
            "content": message,
            "nonce": "0",  # For some reason this works as intended??
            # https://github.com/discord/discord-api-docs/issues/5607
            "tts": False,
            "flags": 0,
        }
        self.session.post(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            headers=heads,
            data=json_data,
        )

    def get_channel_id(self, user_id: str) -> str:
        if not self.__logged_in:
            raise InvalidCredentialsException("You need to login first")
        data = {"recipient_id": user_id}
        headers: dict[str, str | None] = {"authorization": self.user_info.__token}
        response = requests.post(
            f"https://discord.com/api/v9/users/@me/channels", json=data, headers=headers
        )
        return response.json()["id"]

    def send_message_to_user(self, message: str, user_id: str) -> None:
        self.send_message_to_channel(message, self.get_channel_id(user_id))
