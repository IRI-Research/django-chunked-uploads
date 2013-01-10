# django-chunked-uploads

This is an app for your Django project to enable large uploads using the Blob API to chunk the files client side and send chunks that are re-assembled server side.

## Features

* Chunked upload
* Pause/resume upload
* Cancel upload (from database and disk)
* Progress
* CrossDomain
* No flash used

## Install

### Server Side

**On your django server install**

* [httplib2](http://code.google.com/p/httplib2/)
* [django-extentions](http://packages.python.org/django-extensions/)

**Donwload django-chunked-uploads**

* repo [github](https://github.com/IRI-Research/django-chunked-uploads)

or

* install by pip

        pip install django-chunked-uploads
        
**Configuration**

* add 'chunked_uploads' to you 'INSTALLED_APPS'
* in your settings, define 'CHUNKED_UPLOADS_STORAGE_PATH' and 'CHUNKED_UPLOADS_CHUNKS_STORAGE_PATH' (if not defined, default media_root is used)

### Client Side


Credits
========

This API uses and updates some existing ones :
* jQuery-File-Upload : https://github.com/blueimp/jQuery-File-Upload (for JQuery upload part)
* django-chunked-uploads : https://github.com/eldarion/django-chunked-uploads (for Django part, updated)
