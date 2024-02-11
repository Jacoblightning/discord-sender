import copy
import functools

import requests


def internet_connection():
    try:
        response = requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def patch_get(get):
    @functools.wraps(get)
    def wrapper(*args, **kwargs):
        if not internet_connection():
            raise requests.ConnectionError("Internet not connected")
        return get(*args, **kwargs)

    return wrapper


class InvalidCredentialsException(Exception):
    pass


class ArgumentError(Exception):
    pass


class CaptchaError(Exception):
    pass


class ChannelNotFoundError(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AlreadyLoggedInException(Exception):
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
    _DATA = {
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
        self.auth_method: str | None = None

    def logged_in(self) -> bool:
        return self.__logged_in

    def _handle_error(self, resp: requests.Response, custom_message: str | None = None) -> None:
        json_data = resp.json()
        if "hcaptcha" in json_data:
            errcde = "Please login in a browser first and complete the captcha"
            if self.auth_method == "cred":
                errcde += "\nor try token authentication."
            raise CaptchaError(errcde)
        try:
            error: dict[str, str] = json_data["errors"]["login"]["_errors"][0]
            if error["code"] == "INVALID_LOGIN":
                raise InvalidCredentialsException(error["message"])
            else:
                raise requests.RequestException(
                    f"Unknown error code from discord. Json data: {json_data}"
                )
        except KeyError:
            pass
        try:
            error = json_data
            if error["code"] == "10003":
                raise ChannelNotFoundError(f"Channel {channel_id} not found")
            elif resp.status_code == 401 and error["code"] == 0:
                raise InvalidCredentialsException(error["message"] if not custom_message else custom_message)
            else:
                raise requests.RequestException(
                    f"Unknown error code from discord. Json data: {json_data}"
                )
        except KeyError:
            raise requests.RequestException(
                f"Unknown error code from discord. Json data: {json_data}"
            )

    def login_with_credentials(self, email: str, password: str):
        if self.__logged_in:
            raise AlreadyLoggedInException("You already logged in")
        self.session = requests.Session()
        self.session.get = patch_get(self.session.get)  # Fix internet not connected
        self.session.get("https://discord.com/login")  # Get required cookie
        creds = copy.copy(self._DATA)  # Get a copy of the default data
        creds["login"] = email
        creds["password"] = password
        response: requests.Response = self.session.post(
            "https://discord.com/api/v9/auth/login", headers={}, json=creds
        )
        if not response.ok:
            self._handle_error(response)
        user_data: dict[str, str | dict[str, str]] = response.json()
        self.user_info = DiscordLoginInfo(
            token=user_data["token"], uid=user_data["user_id"]
        )
        self.__logged_in: bool = True
        return self

    def login_with_token(self, token):
        if self.__logged_in:
            raise AlreadyLoggedInException("You already logged in")
        resp = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
        if not resp.ok:
            self._handle_error(resp, "Invalid Token")
        self.user_info = DiscordLoginInfo(token=token)
        self.__logged_in = True
        self.session = requests.Session()
        self.session.get = patch_get(self.session.get)
        return self

    def login_with_cookie(self, cookie: None):
        raise NotImplementedError("Cookie not implemented yet")  # TODO: Figure this out

    def send_message_to_channel(self, message: str, channel_id: str):
        if not self.__logged_in:
            raise InvalidCredentialsException("You need to login first")
        if not self.user_info.get_token():
            raise NotImplementedError("Only token or credential authentication can be used currently")
        heads = {"Authorization": self.user_info.get_token()}
        json_data = {
            "mobile_network_type": "unknown",
            "content": message,
            "nonce": "0",  # For some reason this works as intended??
            # https://github.com/discord/discord-api-docs/issues/5607
            "tts": False,
            "flags": 0,
        }
        response = self.session.post(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            headers=heads,
            data=json_data,
        )
        if not response.ok:
            self._handle_error(response)
        return self

    def get_channel_id(self, user_id: str) -> str:
        if not self.__logged_in:
            raise InvalidCredentialsException("You need to login first")
        data = {"recipient_id": user_id}
        headers: dict[str, str | None] = {"authorization": self.user_info.get_token()}
        response = requests.post(
            f"https://discord.com/api/v9/users/@me/channels", json=data, headers=headers
        )
        try:
            return response.json()["id"]
        except KeyError:
            raise UnknownUserException(f"User with id {user_id} not found")

    def send_message_to_user(self, message: str, user_id: str):
        return self.send_message_to_channel(message, self.get_channel_id(user_id))
