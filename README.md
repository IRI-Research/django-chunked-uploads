# django-chunked-uploads

This is an app for your Django project to enable large uploads using the Blob API to chunk the files client side and send chunks that are re-assembled server side.

## Features

* Chunked upload
* Pause/resume upload (even if the page has been closed)
* Cancel upload (from database and disk)
* Progress
* CrossDomain
* No flash used


## Install

### Server Side

**On your django server install**

* [httplib2](http://code.google.com/p/httplib2/)
* [django-extensions](http://packages.python.org/django-extensions/)

**Donwload django-chunked-uploads**

* repo [github](https://github.com/IRI-Research/django-chunked-uploads)

**Configuration**

* add 'chunked_uploads' to you 'INSTALLED_APPS'
* in your settings, define 'CHUNKED_UPLOADS_STORAGE_PATH' and 'CHUNKED_UPLOADS_CHUNKS_STORAGE_PATH' (if not defined, default media_root is used)


### Client Side

**Configuration**

* Get the jquery.fileupload.js or include the link to the file in the server
* Get the partial chunked_upload.html or use your own custom html
* Set the following chunked_uploads_endpoints :
        
        chunked_uploads_endpoints = {
			upload_url: 'upload url',
			done_url: 'done url with uuid="00000000-0000-0000-0000-000000000000"',
			username: 'example',
			api_key: 'secret_example',
        };

* Available callbacks :
        
        //callback of chunked upload start
        chunked_upload_start = function(){
        };
        
        //callback of chunked upload stop
        chunked_upload_stop = function(){
        };
        
        //callback of chunked upload error
        chunked_uploads_error = function(){
        };
        
        //callback of chunked upload complete
        chunked_upload_complete = function(){
        };
        
        //callbacks with the url of the completed upload
        chunked_uploads_video_url = function(video_url) {
        };


## Credits

This API uses and updates some existing ones :
* jQuery-File-Upload : https://github.com/blueimp/jQuery-File-Upload (for JQuery upload part)
* django-chunked-uploads : https://github.com/eldarion/django-chunked-uploads (for Django part, updated)
