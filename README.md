# django-chunked-uploads

This is an app for your Django project to enable large uploads using the Blob API to chunk the files client side and send chunks that are re-assembled server side.

Features
========

* Chunked upload
* Pause/resume upload
* Cancel upload (from database and disk)
* Progress
* CrossDomain (thanks to Jquery file upload)
* No flash used (thanks to Jquery file upload)

Requirements
============

* Django
* Jquery 1.8.3 or later
* That's all ! 

Credits
========

This API uses and updates some existing ones :
* jQuery-File-Upload : https://github.com/blueimp/jQuery-File-Upload (for JQuery upload part)
* django-chunked-uploads : https://github.com/eldarion/django-chunked-uploads (for Django part, updated)
