class TwitchAPIException(Exception):
    """Base class for errors relating to the Twitch API"""


class TwitchRequestError(TwitchAPIException):
    """Error included in a response from the Twitch API"""

    def __init__(self, status, message):
        super().__init__(f'[{status}] {message}')

        self.status = status
        self.message = message