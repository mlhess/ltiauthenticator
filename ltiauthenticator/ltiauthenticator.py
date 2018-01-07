from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.utils import url_path_join
from tornado import gen, web
from traitlets import Unicode
from ltioauth import oauth
from ltioauth import oauth_store
from pprint import pprint


class LTILoginHandler(BaseHandler):
    def get(self):
        _url = url_path_join(self.hub.server.base_url, 'home')
        next_url = self.get_argument('next', default=False)
        if next_url:
             _url = next_url
        self.redirect(_url)

    def post(self):
        #This should become more than one method. 
        username = self.authenticator.usernamefield
        key = self.authenticator.key
        secret = self.authenticator.secret
        user_id = self.get_body_argument(username, default=None, strip=False)
        email = self.get_body_argument('lis_person_contact_email_primary', default=None, strip=False)
        lti_key = self.get_body_argument("oauth_consumer_key", default=None, strip=False)
        oauth_server = oauth.OAuthServer(oauth_store.LTI_OAuthDataStore(key, secret))
        oauth_server.add_signature_method(oauth.OAuthSignatureMethod_PLAINTEXT())
        oauth_server.add_signature_method(oauth.OAuthSignatureMethod_HMAC_SHA1())
        full_uri = self.authenticator.url 
        c = dict()
        for f in self.request.arguments:
            c[f] = self.get_argument(f, default=None, strip=False)
        oauth_request = oauth.OAuthRequest.from_request('POST', full_uri, None, c, query_string=self.request.query)
        try:
            consumer, token, params = oauth_server.verify_request(oauth_request)
        except oauth.OAuthError as err:
            oauth_error = "OAuth Security Validation failed:"+err.message
            consumer = None
            print(oauth_error)
            print (err)
            #if we get here, there was an issue, fail and raise a 401
            raise web.HTTPError(401)

        if consumer is not None:
           #oauth was good. 
           user = self.user_from_username(user_id)
           self.set_login_cookie(user)
           self.redirect(url_path_join(self.hub.server.base_url, 'home'))


class LTIAuthenticator(Authenticator):
    """
    Do some LTI 
    """
    usernamefield = Unicode(
        default_value='user_id',
        config=True,
        help="""
         The username field from the LTI request
        """
    )

    secret = Unicode(
        default_value='secret',
        config=True,
        help="""
         The LTI secret 
        """
    )

    key = Unicode(
        default_value='key',
        config=True,
        help="""
             The LTI key          
          """
    )
    url = Unicode(
        default_value='http://localhost',
        config=True,
        help="""
             The LTI key          
          """
    )

    def get_handlers(self, app):
        return [
            (r'/login', LTILoginHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


