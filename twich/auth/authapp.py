import threading
import logging

from flask import Flask, request


class AuthorizationApp:
    """A temporary Flask application to host a page for the redirect URI from Twitch,
    and on that, send a POST request to another internally hosted route
    with the requested user access token which would otherwise only be accessible
    for the web browser and the user
    """
    
    def __init__(self, user_token, port=6319, path='/'):
        self.user_token = user_token
        self.port = port
        self.path = path

        # State of the authorization process
        self.transaction_completed = False

        # Flask app to await user and receive user access token
        self.flask_app = Flask(f'{__name__}_{id(self)}')

        # Wrap methods as Flask routes
        self.flask_app.redirect = self.flask_app.route(self.path, methods=['GET'])(self.redirect)
        self.flask_app.receive = self.flask_app.route(self.path, methods=['POST'])(self.receive)

        # Disable all logging for Flask except errors
        # NOTE: This does not seem to work! Try switching to built-in HTTP server module.
        self.flask_app.logger.disabled = True
        log = logging.getLogger('werkzeug')
        log.disabled = True

        # Start the authorization process
        self.start()

    def redirect(self):
        """Redirect the user to send the only locally accessible user access token
        in a POST request to another route which will receive and extract it
        """

        return f"""
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>OAuth Local Redirection</title>
                </head>
                
                <body>
                    You should be redirected shortly.

                    <noscript>
                        <h1>
                            Please enable JavaScript! I need to redirect
                            the OAuth token back to the application.
                        </h1>
                    </noscript>

                    <script lang="javascript">
                        let req = new XMLHttpRequest()
                        req.open('POST', '{self.path}', false)
                        
                        req.setRequestHeader('Content-Type', 'text')
                        req.send(document.location.hash)

                        console.log(`Response Headers: ${{req.getAllResponseHeaders()}}`)
                        console.log("I'm ready to close now.")

                        window.close()
                    </script>
                </body>
            </html>
        """

    def receive(self):
        """Receive and extract the user access token
        from the pound sign section of the redirect URL
        """

        string = request.data.decode()

        # Remove # from the start
        string = string[1:]

        # Read parameters from string
        # by splitting at &s and =s

        params = {}

        for segment in string.split('&'):
            try:
                key, value = segment.split('=')
                params[key] = value
            
            except ValueError:
                # Ignore if segment could not be parsed
                # into exactly two strings, key and value
                continue

        if 'access_token' not in params:
            raise KeyError('access_token could not be found')

        # Save the received user access token to user_token
        self.user_token.token = params['access_token']

        # Mark authorization process as completed
        self.transaction_completed = True

        # Terminate application as it is no longer needed
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

        return 'TRANSACTION COMPLETED'

    def start(self):
        """Start Flask server to begin the authorization process"""        
        
        thread = threading.Thread(
            target=self.flask_app.run,
            kwargs={
                'host': 'localhost',
                'port': self.port
            }
        )
        thread.start()