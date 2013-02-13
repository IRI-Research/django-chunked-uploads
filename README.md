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
			//authentication (see below)
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


## Authentication

Inspired by tastypie, django_chunked_uploads provide authentications (basic auth, api_key auth, query auth)

To change the type of authentication, in views.py, replace <authentication_type> with the authentication you want:

        from chunked_uploads.authentication import <authentication_type> as Authentication

### ApiKeyAuthentication

You need to provide through the headers, or the data :
* username
* api_key

The apikey can be set in the django admin view, in the api_key section.

### QueryAuthentication

You need to provide through the headers or the data :
* api_key
* timestamp
* signature (created with your secret key and the timestamp)

### TO DO

Ideally chunked_upload doesn't have to authenticate the user. Chunked_upload gets the timstamp, the api_key, and the signature, and sends it to an external server. If the external server succeeds in authenticating the user, it send back few informations about him. Then chunked_upload create his own user with the informations provided by the external server.

So in authentication.py, the function is_authenticate would be something like this:
* get the api_key, the timestamp, and the signature from the request
* check if the user corresponding to the api_key exists in chunked_upload database
* if not : send the informations to an external serveur, to make him authenticate the user
* if the external server authenticate the user, it send back user informations
* chunked upload save these informations in a new user in its database
* return true


## CrossDomain

Thanks to Jquery File Upload, used client side, you can upload on a different server (crossdomain).

To use a custom configuration of the cross domain, set the following variables :

        CROSS_DOMAIN_ALLOWED_ORIGINS (default : "http://localhost")
        CROSS_DOMAIN_ALLOWED_METHODS = (default : 'POST, GET, OPTIONS, DELETE')
        CROSS_DOMAIN_ALLOWED_HEADERS = (default : "Content-Type, Content-Range, Content-Disposition, Content-Description, username, api_key")
        CROSS_DOMAIN_ALLOWED_CREDENTIALS = (default : 'true')

## Credits

This API uses and updates some existing ones :
* jQuery-File-Upload : https://github.com/blueimp/jQuery-File-Upload (for JQuery upload part)
* django-chunked-uploads : https://github.com/eldarion/django-chunked-uploads (for Django part, updated)
