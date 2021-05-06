import websocket
import time
import threading
import json

from .request import TwitchAPIResponse


class TwitchPubSub:
    """A template class for a Twitch PubSub websocket"""
    
    def __init__(self, user_token, topics, auto_reconnect=True, log=False):
        self.user_token = user_token
        self.topics = topics
        self.auto_reconnect = auto_reconnect
        self.log = log

        self.websocket = websocket.WebSocketApp(
            'wss://pubsub-edge.twitch.tv',
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        self.is_connected = False

    def subscribe(self, *topics):
        self.websocket.send(json.dumps({
            'type': 'LISTEN',
            'data': {
                'topics': topics,
                'auth_token': str(self.user_token)
            }
        }))

        if self.log:
            print(f'Subscribing to:')
            for topic in topics:
                print(f'  * {topic}')

    def ping(self):
        """Ping socket every 4 and a half minutes"""

        # Delay thread to let connection get established
        time.sleep(270)

        while self.is_connected:
            self.websocket.send(json.dumps({'type': 'PING'}))

            if self.log:
                print('[PING] >> Next ping in 4:30 minutes')
                
            time.sleep(270)

    def _on_open(self, ws):
        self.is_connected = True

        # Subscribe to all selected topics on start-up
        self.subscribe(*self.topics)

        self.on_open()

    def on_open(self):
        pass
        
    def _on_message(self, ws, message):
        response = TwitchAPIResponse(message)

        if response.get('type') == 'RECONNECT':
            if self.log:
                print('[RECONNECT] >> Reconnecting to Twitch...')
                
            self.disconnect()
            self.connect()

        elif response.get('type') == 'PONG':
            if self.log:
                print('[PONG]')

        else:
            self.on_message(response)

    def on_message(self, message):
        """What to do when a new message is received"""

    def _on_error(self, ws, error):
        response = TwitchAPIResponse(error)
        self.on_error(response)

    def on_error(self, error):
        """What to do when an error is received"""

    def _on_close(self, ws):
        self.is_connected = False
        self.on_close()

        if self.auto_reconnect:
            self.connect()

    def on_close(self):
        """What to do when the websocket connection
        has been shut down, before exiting the loop"""

    def connect(self):
        """Set up websocket connection and start a PING loop"""
        
        # Start thread for pinging
        self.is_connected = True
        threading.Thread(target=self.ping, daemon=True).start()

        # Run websocket client
        self.websocket.run_forever()
        
    def disconnect(self):
        """Close websocket connection"""
        self.auto_reconnect = False
        self.websocket.close()