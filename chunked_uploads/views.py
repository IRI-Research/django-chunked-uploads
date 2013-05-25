from chunked_uploads.models import Upload, Chunk
from chunked_uploads.utils.cross_domain import (
    allow_cross_domain_response as HttpResponse_cross_domain)
from chunked_uploads.utils.path import sanitize_filename
from chunked_uploads.utils.url import absurl_norequest, get_web_url
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
import json



class LoginRequiredView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        you can add your custom authentication here
        """
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)
        
@login_required
def upload_template(request):
    """
    Basic function to render the demo.html page. It allows to make test, with all default values.
    """
    return render_to_response ('demo.html', context_instance=RequestContext(request))


@csrf_exempt
def complete_upload(request, uuid):
    """
    Function to complete an upload and stitch the chunks
    """
    
    #only a POST request can complete the upload 
    if request.method == "POST":
        data = []
        if "upload-uuid" in request.session:
            del request.session["upload-uuid"]
        
        up = get_object_or_404(Upload, uuid=uuid)
        if up.filesize == up.uploaded_size():
            up.stitch_chunks()
            up.remove_related_chunks()
            data.append({
                        "video_url": get_web_url() + up.upload.url, 
                        "state": "COMPLETE"
                        })
        else:
            up.delete()
            data.append({
                        "video_url": "", 
                        "state": "FAIL"
                        })
            
        return HttpResponse_cross_domain(json.dumps(data), mimetype="application/json")
    else:
        return HttpResponse_cross_domain({}, mimetype="application/json")


class UploadView(LoginRequiredView):
    
    def _add_status_response(self, upload):
        return {
            "name": upload.filename,
            "size": upload.uploaded_size(),
            "total_size": upload.filesize,
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
                if u.state==Upload.STATE_COMPLETE:
                    del self.request.session["upload-uuid"]
            except Upload.DoesNotExist:
                del self.request.session["upload-uuid"]
        
        if "upload-uuid" not in self.request.session:
            content_disposition = self.request.META["HTTP_CONTENT_DISPOSITION"]
            try:
                content_range = self.request.META["HTTP_CONTENT_RANGE"]
                content_range  = content_range.split("/")[1]
            except:
                content_range = self.request.META["CONTENT_LENGTH"]
            u = Upload.objects.create(
                user=self.request.user,
                filename=sanitize_filename(unicode(content_disposition.split("=")[1].split('"')[1])),
                filesize=content_range
            )
            self.request.session["upload-uuid"] = str(u.uuid)
        
        c = Chunk(upload=u)
        c.chunk.save(u.filename, f, save=False)
        c.chunk_size = c.chunk.size
        c.save()
        
        data = []
        data.append(self._add_status_response(u))
        
        return data
    
    def get(self, request, *args, **kwargs):
        data=[]
        if "upload-uuid" in self.request.session:
            try:
                u = Upload.objects.get(uuid=self.request.session["upload-uuid"])
                data.append(self._add_status_response(u))
            except Upload.DoesNotExist:
                del self.request.session["upload-uuid"]
        return HttpResponse_cross_domain(json.dumps(data), mimetype="application/json")
    
    def post(self, request, *args, **kwargs):
        data = self.handle_chunk()
        return HttpResponse_cross_domain(json.dumps(data), mimetype="application/json")
        
    def options(self, request, *args, **kwargs):
        return HttpResponse_cross_domain({}, mimetype="application/json")
    
    def delete(self, request, *args, **kwargs):
        upload = get_object_or_404(Upload, pk=kwargs.get("pk"))
        upload.delete()
        #check if upload-uuid still in request, if it : delete
        if "upload-uuid" in self.request.session:
            del request.session["upload-uuid"]
        
        return HttpResponse_cross_domain({}, mimetype="application/json")
