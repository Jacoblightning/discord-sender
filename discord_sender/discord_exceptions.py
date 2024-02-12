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
