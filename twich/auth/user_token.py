import webbrowser
import time

from urllib.parse import urlparse, quote

from .authapp import AuthorizationApp

from ..request import TwitchAPIRequest

from ..exceptions import TwitchRequestError
from .exceptions import InvalidTokenException


class TwitchUserToken:
    """A user access token for Twitch"""

    def __init__(self, client_id, scope='', port=6319, path='/', token=None):
        self.client_id = client_id
        
        self.port = port        
        self.path = path

        self.token = token
        self.expires_at = None

        # Join with spaces if a list is given for scope
        if type(scope) is list:
            scope = quote(' ').join(scope)

        # All parameters required for the token request
        self.query = {
            'client_id': client_id,
            'redirect_uri': get_redirect_uri(port, path),
            'response_type': 'token',
            'scope': scope
        }

        # Make sure to start with a valid token
        str(self)

    def __str__(self):
        """Make sure the token is valid and then return it"""

        if not self.is_valid():
            self.request_new()

        return self.token

    def is_valid(self):
        """Validate token with the Twitch API"""
        
        if not self.token:
            return False

        if self.expires_at is not None:
            return time.time() < self.expires_at

        try:
            response = TwitchAPIRequest('GET',
                'https://id.twitch.tv/oauth2/validate',
                headers={'Authorization': f'OAuth {self.token}'}
            ).send()
            
            self.expires_at = time.time() + response['expires_in']
            
            # Keep username and user ID for external use
            self.login = response.get('login')
            self.user_id = response.get('user_id')

            return True

        except TwitchRequestError:
            return False

    def request_new(self):
        """Request a new user access token,
        and retrieve it through a temporary Flask server
        with which to allow the user to grant permission"""

        # Start an AuthorizationApp server
        auth_app = AuthorizationApp(self, self.port, self.path)

        # Create URL from parameters
        url = get_authorization_url(**self.query)

        # Open address in web browser
        webbrowser.open(url, 2)

        # Wait for the POST to be submitted
        # and the Flask server to be closed
        while not auth_app.transaction_completed:
            time.sleep(1)

        # If the newly requested token is not valid, something is wrong
        if not self.is_valid():
            raise InvalidTokenException(
                'Something has gone wrong with retrieving a new valid token')


def get_authorization_url(**query):
    """Create a URL to the authentication endpoint from query"""

    # Join all parameters by &s and append to endpoint
    params = '&'.join(f'{key}={value}' for key, value in query.items())
    url = f'https://id.twitch.tv/oauth2/authorize?{params}'

    return url


def get_redirect_uri(port, path):
    """Create a URL for the redirect URI"""

    # Remove trailing /
    if path.endswith('/'):
        path = path[:-1]

    return f'http://localhost:{port}{path}'