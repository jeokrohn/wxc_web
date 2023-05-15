import os

from flask import Flask, url_for, jsonify, request
from authlib.integrations.flask_client import OAuth
from requests import Session

app = Flask(__name__)
app.secret_key = os.urandom(50)
oauth = OAuth()

# auto-configuration does not work b/c there is a mismatch between the issuer in the OID config and the iss claim in
# the JWT token obtained.
# two options:
#   1) use auto-config and define claim_options when getting the JWT toke to override the issuer claim option
#       token = webex.authorize_access_token(response_type='id_token',
#                                            claims_options={'iss': {'values': ['https://idbroker-b-us.webex.com/idb']}}
#                                            )
#
#   2) manually configure the client. Then an access token can be obtained w/o claim_options when getting the access
#   token. This minimizes the risk of the static reference to an issue host name.
#         webex = oauth.register('webex',
#                                access_token_url='https://webexapis.com/v1/access_token',
#                                authorize_url='https://webexapis.com/v1/authorize',
#                                jwks_uri='https://webexapis.com/v1/verification',
#                                client_kwargs={'scope': 'openid email profile phone address',
#                                               'code_challenge_method': 'S256',
#                                               })

webex = oauth.register('webex',
                       # server_metadata_url='https://webexapis.com/v1/.well-known/openid-configuration',
                       access_token_url='https://webexapis.com/v1/access_token',
                       authorize_url='https://webexapis.com/v1/authorize',
                       jwks_uri='https://webexapis.com/v1/verification',
                       client_kwargs={'scope': 'openid email profile phone address',
                                      'code_challenge_method': 'S256',
                                      })

oauth.init_app(app)


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    # code_verifier, code_challenge = generate_pkce_pair()
    # return webex.authorize_redirect(redirect_uri, response_type='code', code_challenge=code_challenge,
    #                                 code_verifier=code_verifier)
    return webex.authorize_redirect(redirect_uri, response_type='code')


@app.route('/authorize')
def authorize():
    token = webex.authorize_access_token(response_type='id_token',
                                         # claims_options={'iss': {'values': ['https://idbroker-b-us.webex.com/idb']}}
                                         )
    # use access token to get actual user info
    with Session() as session:
        with session.get('https://webexapis.com/v1/userinfo',
                         headers={'Authorization': f'Bearer {token["access_token"]}'}) as r:
            r.raise_for_status()
            profile = r.json()
    return jsonify(profile)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
