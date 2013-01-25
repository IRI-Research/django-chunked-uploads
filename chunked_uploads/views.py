import json
import logging
import urllib2

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.template import RequestContext
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from chunked_uploads.models import Upload, Chunk
from chunked_uploads.utils.url import absurl_norequest, get_web_url
from chunked_uploads.utils.path import sanitize_filename
from chunked_uploads.utils.cross_domain import allow_cross_domain_response as HttpResponse_cross_domain
from chunked_uploads.utils.build_auth_request import build_request
from chunked_uploads.utils.decorators import oauth_required

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
    if request.method == "POST":
        data = []
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
            up.remove_related_chunks()
            data.append({
                         "video_url": get_web_url() + up.upload.url, 
                         "state": Upload.STATE_CHOICES[up.state]
                         })
        else:
            up.delete()
            
        return HttpResponse_cross_domain(json.dumps(data), mimetype="application/json")
    else:
        return HttpResponse_cross_domain({}, mimetype="application/json")


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
        logging.debug("self.request.raw_post_data : " + str(self.request.raw_post_data))
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
                # if the objet's got an upload error: delete
                if u.state == Upload.STATE_UPLOAD_ERROR:
                    u.delete()
                else:
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
