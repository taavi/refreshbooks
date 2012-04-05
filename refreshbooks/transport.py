import base64
import httplib

try:
    from refreshbooks.optional import oauth as os
    
    OAuthAuthorization = os.OAuthAuthorization
except ImportError:
    def OAuthAuthorization(consumer, token, sig_method=None):
        raise NotImplementedError('oauth support requires the "oauth" module.')

transport = None
try:
    from refreshbooks.transports import use_requests as transport
except ImportError:
    pass

if transport is None:
    try:
        from refreshbooks.transports import use_httplib2 as transport
    except ImportError:
        pass

if transport is None:
    import warnings
    warnings.warn("Unable to load requests or httplib2 transports, falling back to urllib2. SSL cert verification disabled.")
    from refreshbooks.transports import use_urllib2 as transport

class TokenAuthorization(object):
    """Generates HTTP BASIC authentication headers obeying FreshBooks'
    token-based auth scheme (token as username, password irrelevant).
    
        >>> auth = TokenAuthorization("monkey")
        >>> auth()
        {'Authorization': 'Basic bW9ua2V5Og=='}
    
    Prefer OAuthAuthorization, from refreshbooks.optional.oauth, for new
    development.
    """
    def __init__(self, token):
        # See RFC 2617.
        base64_user_pass = base64.b64encode("%s:" % (token, ))
        
        self.headers = {
            'Authorization': 'Basic %s' % (base64_user_pass, )
        }
    
    def __call__(self):
        return self.headers

class UserAgentHeaders(object):
    def __init__(self, base_headers_factory, user_agent):
        self.base_headers_factory = base_headers_factory
        self.user_agent = user_agent
    
    def __call__(self):
        headers = self.base_headers_factory()
        headers['User-Agent'] = self.user_agent
        return headers

class KeepAliveHeaders(object):
    def __init__(self, base_headers_factory):
        self.base_headers_factory = base_headers_factory
    
    def __call__(self):
        headers = self.base_headers_factory()
        headers['Connection'] = 'Keep-Alive'
        return headers

class TransportException(Exception):
    def __init__(self, status, content):
        self.status = status
        self.content = content
    
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return "TransportException(%r, %r)" % (self.status, self.content)

HttpTransport = transport.Transport
