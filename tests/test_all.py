from unittest import mock

import pytest
import requests

from ..discord_sender import (channel, discord, discord_exceptions, info,
                              other, tools)


@pytest.fixture()
def user():
    return discord.DiscordUser()


class TestExceptions:
    def test_captcha(self, user):
        resp = mock.Mock()
        resp.json.return_value = {"hcaptcha": "captcha error"}
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
        user._set_logged_in(False)


class TestWarnings:
    def test_dms(self, user):
        with pytest.raises(discord_exceptions.InvalidCredentialsException):
            with pytest.deprecated_call():
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


@pytest.mark.skip()
class test_discord_main:
    pass  # TODO: Finish this
