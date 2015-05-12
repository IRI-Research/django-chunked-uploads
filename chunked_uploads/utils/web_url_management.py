from django.contrib.sites.models import Site


def get_web_url(request=None):
    if request:
        if request.is_secure():
            domain = "https://%s" % Site.objects.get_current().domain
        else:
            domain = "http://%s" % Site.objects.get_current().domain
    else:
        domain = "http://%s" % Site.objects.get_current().domain
    return domain
