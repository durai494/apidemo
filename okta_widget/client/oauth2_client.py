import requests
import json
import base64
import urllib3


class OAuth2Client(object):
    def __init__(self, base_url, auth_server, client_id=None, client_secret=None):
        self.base_url = base_url
        self.auth_server = auth_server
        self.client_id = client_id
        self.client_secret = client_secret
        self.basic = None
        if client_id is not None and client_secret is not None:
            enc = client_id + ':' + client_secret
            basic = base64.b64encode(enc.encode('ascii'))
            self.basic = str(basic, 'utf-8')

    def token(self, code, redirect_uri):
        url = self.base_url + '/oauth2/{}/v1/token'.format(self.auth_server)
        payload = {
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code
        }
        auth = {}
        if self.basic:
            auth = {'Authorization': 'Basic ' + self.basic}
        response = requests.post(url, data=payload, headers=auth)
        tokens = response.json()
        # print('tokens = {}'.format(tokens))
        return tokens

    def token_cc(self, scope):
        try:
            url = self.base_url + '/oauth2/{}/v1/token'.format(self.auth_server)
            payload = {
                'grant_type': 'client_credentials',
                'scope': scope.split(',')
            }
            auth = {'Authorization': 'Basic ' + self.basic}
            response = requests.post(url, data=payload, headers=auth)
            tokens = response.json()
        except Exception as e:
            tokens = {'error': e}
        return tokens

    def profile(self, token):
        url = '{0}/oauth2/{1}/v1/userinfo'.format(self.base_url, self.auth_server)
        headers = {'Authorization': 'Bearer ' + token}
        profile = {}
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(url, headers=headers, verify=False)
            if response.status_code == 200:
                profile = response.json()
        except Exception as e:
            print('exception: {}'.format(e))

        # (Deprecated)
        # # IMPERSONATION Hack: Get the profile from the "Other" issuer
        # if profile == {} and settings.IMPERSONATION_ORG and settings.IMPERSONATION_ORG != 'None'\
        #         and settings.IMPERSONATION_ORG_AUTH_SERVER_ID and settings.IMPERSONATION_ORG_AUTH_SERVER_ID != 'None':
        #     url = 'https://{0}/oauth2/{1}/v1/userinfo'.format(settings.IMPERSONATION_ORG, settings.IMPERSONATION_ORG_AUTH_SERVER_ID)
        #     print('userinfo url={}'.format(url))
        #     try:
        #         response = requests.post(url, headers=headers, verify=False)
        #         profile = response.json()
        #     except Exception as e2:
        #         print('exception2: {}'.format(e2))

        return profile


def _tokenIssuer(token):
    iss = None
    try:
        parts = token.split('.')
        payload = parts[1]
        payload += '=' * (-len(payload) % 4)
        decoded = base64.b64decode(payload)
        # print('payload = {}'.format(decoded))
        iss = json.loads(decoded)['iss']
    except Exception as e:
        print('there was an exception: {}'.format(e))
        return None
    # print('iss = {}'.format(iss))
    return iss


