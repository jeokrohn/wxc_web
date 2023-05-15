import logging
import os

from dotenv import load_dotenv

from flaskr import app

load_dotenv()
app.config['WEBEX_CLIENT_ID'] = os.getenv('CLIENT_ID')
app.config['WEBEX_CLIENT_SECRET'] = os.getenv('CLIENT_SECRET')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('authlib').setLevel(logging.DEBUG)
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    app.run()
