from unittest import mock

import pytest
import requests

from discord_sender import (channel, discord, discord_exceptions, info, other,
                            tools)
from discord_sender.other import OtherUser


@pytest.fixture()
def user():
    return discord.DiscordUser()


def internet_connection():
    try:
        timeo = 5  # pragma: no mutate
        requests.get("https://google.com", timeout=timeo)
        return True
    except requests.ConnectionError:  # pragma: no cover
        return False


class TestExceptions:
    def test_captcha(self, user):
        resp = mock.Mock()
        resp.json.return_value = {'captcha_key': ['captcha-required'], 'captcha_service': 'hcaptcha'}
        with pytest.raises(discord_exceptions.CaptchaError):
            user._handle_error(resp)

    def test_invalid_credentials(self, user):
        resp = mock.Mock()
        resp.json.return_value = {
            "errors": {"login": {"_errors": [{"code": "INVALID_LOGIN", "message": ""}]}}
        }
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user._handle_error(resp)

    def test_channel_not_found(self, user):
        resp = mock.Mock()
        resp.json.return_value = {"code": 10003}
        with pytest.raises(discord_exceptions.ChannelNotFoundError):
            user._handle_error(resp)

    def test_401(self, user):
        resp = mock.Mock()
        resp.status_code = 401
        resp.json.return_value = {"code": 0, "message": ""}
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user._handle_error(resp)

    def test_unauthorized(self, user):
        resp = mock.Mock()
        resp.json.return_value = {"code": 50001}
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user._handle_error(resp)

    def test_unknown_error(self, user):
        resp = mock.Mock()
        resp.json.return_value = {"code": 10033}
        with pytest.raises(requests.RequestException):
            user._handle_error(resp)

    def test_login_checks(self, user):
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.get_dms(False)
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.send_message_to_channel("", "")
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.send_message_to_user("", "")
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.get_channel_id("")
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.send_message_to_username("", "")
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.get_channel_info("")
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.get_user_info_by_id("")
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            user.get_user_info_by_username("")

    def test_cookie_failure(self, user):
        with pytest.raises(NotImplementedError):
            user.login_with_cookie(None)

    def test_channel_failure(self, user):
        with pytest.warns(UserWarning, match="This method snould not be used outside of tests."):
            user._set_logged_in(False)

    def test_info_exception(self):
        with pytest.raises(discord_exceptions.ArgumentError):
            info.DiscordLoginInfo()


class TestWarnings:
    def test_dms(self, user):
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            with pytest.warns(DeprecationWarning, match= "Passing int to get_dms is Deprecated and will soon be removed"):
                user.get_dms(1)

    def test_alert(self, user):
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            with pytest.warns(UserWarning):
                user.send_message_to_username("", "")

        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            with pytest.warns(UserWarning):
                user.get_channel_info("")

        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            with pytest.warns(UserWarning):
                user.get_user_info_by_id("")

        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            with pytest.warns(UserWarning):
                user.get_user_info_by_username("")

        with pytest.warns(UserWarning):
            user._set_logged_in(False)


class edgeCase:
    def __init__(self):
        self.checked = 0

    def __len__(self):
        self.checked += 1
        return self.checked - 1


class TestChannels:
    def test_get_dms(self, user):
        user.session = mock.Mock()
        user._set_logged_in(True)
        user.user_info = info.DiscordLoginInfo(token="1")
        resp = mock.Mock()
        resp.json.return_value = [
            {"id": "939487398457", "recipients": [{"id": "438957"}], "type": 1},
            {"id": "304857398457", "recipients": [{"id": "5495876"}], "type": 3},
        ]
        resp.ok.return_value = True
        user.session.get.return_value = resp
        dms = user.get_dms(True)
        should = [
            channel.Channel(
                channel_id="939487398457",
                recipients=[other.OtherUser("438957")],
                chan_type=1,
            ),
            channel.Channel(
                channel_id="304857398457",
                recipients=[other.OtherUser("5495876")],
                chan_type=3,
            ),
        ]
        assert len(dms) == len(should)
        zipped = tools.ziplist(dms, should)
        assert len(zipped) == len(should)
        for thing1, thing2 in zipped:
            assert thing1 == thing2

    def test_channel_types(self):
        chan = channel.Channel("12345", [], 1)
        assert chan.type == 1
        assert chan.recipients == []
        assert chan.channel_id == "12345"
        assert chan.channel_type == "DM"
        chan = channel.Channel("12345", [], 3)
        assert chan.channel_type is None
        chan = channel.Channel("12345", [], 2)
        assert chan.channel_type is "unknown"

    def test_channel_equals(self):
        chan1 = channel.Channel("12345", [], 1)
        assert chan1 != 4
        assert chan1 != channel.Channel("1234", [], 1)
        assert chan1 != channel.Channel("12345", [], 1, is_in_server=True)
        recipientmocker = mock.Mock()
        recipientmocker.username = None
        chan2 = channel.Channel("12345", [recipientmocker], 1)
        assert chan1 != chan2
        del chan2
        assert chan1 != channel.Channel("12345", [], 2)
        chan2 = channel.Channel("12345", [], 2)
        del chan2.recipients
        assert chan1 != chan2

    def test_channel_strict_equals(self):
        check = channel.Channel.strict_equality_check
        nch = lambda first, second: not check(first, second)
        chan1 = channel.Channel("12345", [], 1)
        assert nch(chan1, 4)
        chan2 = channel.Channel("12345", [], 1)
        chan2.to = 3
        assert nch(chan1, chan2)
        del chan2.to
        assert nch(chan1, chan2)
        del chan2
        assert nch(chan1, channel.Channel("12345", [], 1, name="HI"))
        chan2 = channel.Channel("12345", [], 1)
        chan2.channel_type = "12345"
        assert nch(chan1, chan2)
        assert check(chan1, channel.Channel("12345", [], 1))


class TestDefaults:
    def test_default_channel(self):
        default_channel = channel.Channel("12321", [])
        deafult_should_be = channel.Channel("12321", [], 1, False, None)
        assert channel.Channel.strict_equality_check(default_channel, deafult_should_be)

    def test_internettest_works(self):
        assert discord.internet_connection() == internet_connection()

    def test_patcher_works(self):
        def g():
            return "WORKS"

        if internet_connection():
            assert discord.patch_get(g)() == g()
        else:
            with pytest.raises(requests.ConnectionError, match="Internet not connected"):
                discord.patch_get(g)()

    def test_default_duser(self, user):
        assert user.user_info is None
        assert user.logged_in() is False
        assert user.session is None
        assert user.auth_method is None

    def test_tests(self):
        assert True


class TestOtheruser:
    def test_repr(self):
        user = OtherUser("12345")
        assert repr(user) == f"{user.user_id}: {user.username}{('/' + user.global_name) if user.global_name else ''}"

