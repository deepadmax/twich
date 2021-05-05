import requests
import json

from .exceptions import TwitchRequestError


class TwitchAPIRequest:
    """An HTTP request to the Twitch API"""
    
    def __init__(self, method, *args, **kwargs):
        # Use the corresponding function from requests
        if method == 'GET':
            self.method = requests.get
        elif method == 'POST':
            self.method = requests.post
        elif method == 'DELETE':
            self.method = requests.delete
        else:
            raise ValueError('Method must be either GET, POST, or DELETE')

        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.send()

    def send(self):
        """Send the request and return the response"""

        # Send request and unpack JSON payload
        response = self.method(*self.args, **self.kwargs)
        content = json.loads(response.content)

        if 'status' in content:
            raise TwitchRequestError(
                content['status'],
                content['message']
            )

        return TwitchAPIResponse(content)


class TwitchAPIResponse(dict):
    def __init__(self, content):
        # Attempt to load any string as JSON,
        # as Twitch sends back any JSON object
        # that is not top-level, as a string
        self.update(unpack_json(content))

    def __repr__(self):
        return json.dumps(self, sort_keys=True, indent=2)


def unpack_json(data):
    """Unpack any JSON strings inside
    the hierarchy of a dictionary
    """

    # Create a new dictionary to avoid modification
    json_object = {}

    for key, value in data.items():
        # Attempt to unpack value if string, as JSON object
        if type(value) is str:
            try:
                value = json.loads(value)
            except ValueError:
                pass

        # Unpack any dictionary found, further
        if type(value) is dict:
            value = unpack_json(value)

        # Add the new value to the new object
        json_object[key] = value

    return json_object