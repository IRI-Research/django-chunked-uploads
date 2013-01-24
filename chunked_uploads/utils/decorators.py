from django.http import HttpResponse
from django.conf import settings
import oauth2
from django.contrib.sites.models import Site
try: from functools import wraps
except ImportError: from django.utils.functional import wraps # Python 2.4 fallback.

def oauth_required(view_func):
    """
    Decorator for views to ensure that the user is sending an OAuth signed request.
    """
    def _checklogin(request, *args, **kwargs):
        try:
            key = request.REQUEST.get('oauth_consumer_key', None)
            uurl = 'http://' + Site.objects.get_current().domain + request.path   # if you don't use the Site framework, you just need to provide the domain of your site/API
            oreq = oauth2.Request(request.method, uurl, request.REQUEST, '', False)
            server = oauth2.Server()
            cons = oauth2.Consumer(key, settings.OAUTH_PARTNERS[key])
            server.add_signature_method(oauth2.SignatureMethod_HMAC_SHA1())
            server.verify_request(oreq, cons, None)
            return view_func(request, *args, **kwargs)
        except:
            return HttpResponse("API ERROR")
    return wraps(view_func)(_checklogin)