from chunked_uploads.utils.web_url_management import get_web_url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
import urlparse


def absstatic(request, path):
    domain = get_web_url(request)
    new_path = staticfiles_storage.url(path)
    return urlparse.urljoin(domain, new_path)


def absurl(request, viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    domain = get_web_url(request)
    path = reverse(viewname, urlconf, args, kwargs, prefix, current_app)
    return urlparse.urljoin(domain, path)


def absurl_norequest(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    domain = get_web_url()
    path = reverse(viewname, urlconf, args, kwargs, prefix, current_app)
    return urlparse.urljoin(domain, path)
