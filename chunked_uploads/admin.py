from django.contrib import admin
from django.conf import settings
from chunked_uploads.models import Upload, Chunk, ApiKey


admin.site.register(Upload)
admin.site.register(Chunk)
admin.site.register(ApiKey)

if 'django.contrib.auth' in settings.INSTALLED_APPS:

    class ApiKeyInline(admin.StackedInline):
        model = ApiKey
        extra = 0
