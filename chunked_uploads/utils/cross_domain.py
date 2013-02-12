from django.http import HttpResponse

try:
    from django.conf import settings
    CROSS_DOMAIN_ALLOWED_ORIGINS = settings.CROSS_DOMAIN_ALLOWED_ORIGINS
    CROSS_DOMAIN_ALLOWED_METHODS = settings.CROSS_DOMAIN_ALLOWED_METHODS
    CROSS_DOMAIN_ALLOWED_HEADERS = settings.CROSS_DOMAIN_ALLOWED_HEADERS
    CROSS_DOMAIN_ALLOWED_CREDENTIALS = settings.CROSS_DOMAIN_ALLOWED_CREDENTIALS
    
except AttributeError:
    CROSS_DOMAIN_ALLOWED_ORIGINS = "http://localhost"
    CROSS_DOMAIN_ALLOWED_METHODS = 'POST, GET, OPTIONS, DELETE'
    CROSS_DOMAIN_ALLOWED_HEADERS = "Content-Type, Content-Range, Content-Disposition, Content-Description, username, api_key"
    CROSS_DOMAIN_ALLOWED_CREDENTIALS = 'true'

def allow_cross_domain_response(data, mimetype=None, status=None):
    
    response = HttpResponse(data, mimetype=mimetype, status=status)
    response['Access-Control-Allow-Origin']  = CROSS_DOMAIN_ALLOWED_ORIGINS
    response['Access-Control-Allow-Methods'] = CROSS_DOMAIN_ALLOWED_METHODS
    response['Access-Control-Allow-Headers'] = CROSS_DOMAIN_ALLOWED_HEADERS
    response['Access-Control-Allow-Credentials'] = CROSS_DOMAIN_ALLOWED_CREDENTIALS
    return response