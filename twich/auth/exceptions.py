from ..exceptions import TwitchAPIException


class InvalidTokenException(TwitchAPIException):
    """User access token used for request is invalid"""