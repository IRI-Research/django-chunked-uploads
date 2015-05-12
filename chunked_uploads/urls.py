from django.conf.urls import patterns, url

from chunked_uploads.views import UploadView, complete_upload, upload_template


urlpatterns = patterns(
    "",
    url(r"^upload/done/(?P<uuid>[-0-9a-f]{36})/$", complete_upload, name="upload_done"),
    url(r"^upload/$", UploadView.as_view(), name="upload"),
    url(r"^(?P<pk>\d+)/delete/$", UploadView.as_view(), name="upload_delete"),
    url(r"upload_template/$", upload_template),
)
