import copy
import functools
import warnings

import requests

from .channel import Channel
from .discord_exceptions import *
from .info import DiscordLoginInfo
from .other import OtherUser


def internet_connection():
    try:
        timo = 5  # pragma: no mutate
        requests.get("https://google.com", timeout=timo)
        return True
    except requests.ConnectionError:  # pragma: no cover
        return False  # pragma: no mutate


def patch_get(get):
    @functools.wraps(get)  # pragma: no mutate
    def wrapper(*args, **kwargs):
        if not internet_connection():
            raise requests.ConnectionError("Internet not connected")  # pragma: no mutate
        return get(*args, **kwargs)

    return wrapper


class DiscordUser:
    def __init__(self):
        self.user_info: DiscordLoginInfo | None = None
        self.__logged_in: bool = False
        self.session: requests.Session | None = None
        self.auth_method: str | None = None

    def logged_in(self) -> bool:
        return self.__logged_in

    def _set_logged_in(self, logged_in: bool):
        warnings.warn("This method snould not be used outside of tests.")
        self.__logged_in = logged_in

    def get_dms(self, format_type: bool | int = True):
        if isinstance(format_type, int) and not isinstance(format_type, bool):
            warnings.warn(
                "Passing int to get_dms is Deprecated and will soon be removed",
                DeprecationWarning,
            )  # TODO: Remove passing an int.
            format_type = False if format_type == 1 else True
        if not self.__logged_in:
            raise InvalidCredentialsException("You are not logged in")
        heads = {"Authorization": self.user_info.get_token()}
        response = self.session.get(
            "https://discord.com/api/v9/users/@me/channels", headers=heads
        )
        if not response.ok:
            self._handle_error(response)
        if not format_type:
            return response.json()
        dms = []
        json: list[dict[str, str | int | list[dict[str, int | str | None | bool]]]] = (
            response.json()
        )
        for channel in json:
            dms.append(
                Channel(
                    channel["id"],
                    [
                        OtherUser(
                            user_id=other["id"],
                            global_name=other.get("global_name"),
                            username=other.get("username"),
                            is_bot=other.get("bot", False),
                        )
                        for other in channel["recipients"]
                    ],
                    chan_type=channel["type"],
                    name=channel.get("name", None),
                )
            )
        return dms

    def _handle_error(
        self, resp: requests.Response, custom_message: str | None = None
    ) -> None:
        json_data = resp.json()
        if json_data.get("captcha_key") == ['captcha-required']:
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
            if error["code"] == 10003:
                raise ChannelNotFoundError(f"Channel not found")
            elif resp.status_code == 401 and error["code"] == 0:
                raise InvalidCredentialsException(
                    error["message"] if not custom_message else custom_message
                )
            elif error["code"] == 50001:
                raise InvalidCredentialsException(
                    "You do not have permission to send a message in this channel"
                )
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
        creds = {"login": email, "password": password}
        response: requests.Response = self.session.post(
            "https://discord.com/api/v9/auth/login", headers={}, json=creds
        )
        if not response.ok:
            self._handle_error(response)
        user_data: dict[str, str | dict[str, str]] = response.json()
        self.user_info = DiscordLoginInfo(
            token=user_data["token"], uid=user_data["user_id"]
        )
        self.__logged_in = True
        return self

    def login_with_token(self, token):
        if self.__logged_in:
            raise AlreadyLoggedInException("You already logged in")
        resp = requests.get(
            "https://discord.com/api/v9/users/@me", headers={"Authorization": token}
        )
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
            raise NotImplementedError(
                "Only token or credential authentication can be used currently"
            )
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

    def send_message_to_username(self, message: str, username: str):
        warnings.warn("Username support is still experimental")
        dms: list[Channel] = self.get_dms(True)
        for dm in dms:
            to: OtherUser | list[OtherUser] = dm.recipients
            if isinstance(to, OtherUser):
                to: list[OtherUser] = [to]
            for user in to:
                if user.username == username:
                    return self.send_message_to_user(message, user.user_id)

    def get_channel_info(self, channel_id: str):
        warnings.warn("Channel info is still experimental")
        channels: list[Channel] = self.get_dms(True)
        for channel in channels:
            if channel.channel_id == channel_id:
                return channel

    def get_user_info_by_id(self, user_id: str):
        warnings.warn(
            "It is recommended to use get_dms to get the info of a user as this function calls that "
            "internally"
        )
        return self._do_user_check(lambda user: user.user_id == user_id)

    def get_user_info_by_username(self, username: str):
        warnings.warn("Username support is still experimental")
        warnings.warn(
            "It is recommended to use get_dms to get the info of a user as this function calls that "
            "internally"
        )
        return self._do_user_check(lambda user: user.username == username)

    def _do_user_check(self, checker):
        dms: list[Channel] = self.get_dms(True)
        for dm in dms:
            to: OtherUser | list[OtherUser] = dm.recipients
            if isinstance(to, OtherUser):
                to: list[OtherUser] = [to]
            for user in to:
                if checker(user):
                    return user
