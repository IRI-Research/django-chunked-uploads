import json

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from chunked_uploads.models import Upload, Chunk
from chunked_uploads.utils.url import absurl_norequest, get_web_url


class LoginRequiredView(View):
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)

@login_required
def upload_template(request):
    return render_to_response ('demo.html', context_instance=RequestContext(request))


@csrf_exempt
def complete_upload(request, uuid):
    up = get_object_or_404(Upload, uuid=uuid)
    if up.filesize == up.uploaded_size():
        up.state = Upload.STATE_COMPLETE
    else:
        up.state = Upload.STATE_UPLOAD_ERROR
    up.save()
        
    if "upload-uuid" in request.session:
        del request.session["upload-uuid"]
        
    if up.state == Upload.STATE_COMPLETE:
        up.stitch_chunks()
        
    if up.state == Upload.STATE_STITCHED:
        up.remove_related_chunks()
    
    data = []
    data.append({
        "video_url": get_web_url() + up.upload.url, 
        "state": up.state
    })
    return HttpResponse(json.dumps(data), mimetype="application/json")


class UploadView(LoginRequiredView):
    
    def _add_status_response(self, upload):
        return {
            "name": upload.filename,
            "type": "",
            "size": upload.uploaded_size(),
            "progress": "",
            "thumbnail_url": "",
            "url": upload.chunks.all()[0].chunk.url,
            "delete_url": absurl_norequest("upload_delete", kwargs={"pk": upload.pk}),
            "delete_type": "DELETE",
            "upload_uuid": str(upload.uuid)
        }
    
    def handle_chunk(self):
        f = ContentFile(self.request.raw_post_data)
        if "upload-uuid" in self.request.session:
            try:
                u = Upload.objects.get(uuid=self.request.session["upload-uuid"])
                if u.state in [Upload.STATE_COMPLETE, Upload.STATE_UPLOAD_ERROR]:
                    del self.request.session["upload-uuid"]
            except Upload.DoesNotExist:
                del self.request.session["upload-uuid"]
        
        if "upload-uuid" not in self.request.session:
            content_disposition = self.request.META["HTTP_CONTENT_DISPOSITION"]
            content_range = self.request.META["HTTP_CONTENT_RANGE"]
            u = Upload.objects.create(
                user=self.request.user,
                filename=content_disposition.split("=")[1].split('"')[1],
                filesize=content_range.split("/")[1]
            )
            self.request.session["upload-uuid"] = str(u.uuid)
        
        c = Chunk(upload=u)
        c.chunk.save(u.filename, f, save=False)
        c.chunk_size = c.chunk.size
        c.save()
        
        data = []
        data.append(self._add_status_response(u))
        
        return HttpResponse(json.dumps(data), mimetype="application/json")
    
    def get(self, request, *args, **kwargs):
        data=[]
        if "upload-uuid" in self.request.session:
            try:
                u = Upload.objects.get(uuid=self.request.session["upload-uuid"])
                data.append(self._add_status_response(u))
            except Upload.DoesNotExist:
                del self.request.session["upload-uuid"]
        return HttpResponse(json.dumps(data), mimetype="application/json")
    
    def post(self, request, *args, **kwargs):
        return self.handle_chunk()
    
    def abort (self, request, *args, **kwargs):
        pass
    
    def delete(self, request, *args, **kwargs):
        upload = get_object_or_404(Upload, pk=kwargs.get("pk"))
        upload.delete()
        if "upload-uuid" in self.request.session:
            del request.session["upload-uuid"]
        return HttpResponse(json.dumps({}), mimetype="application/json")
