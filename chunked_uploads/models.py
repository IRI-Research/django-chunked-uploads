from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.files.utils import FileProxyMixin
from django.db import models
from django_extensions.db.fields import UUIDField
import datetime
import errno
import hashlib
import hmac
import logging
import os
import time

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


STORAGE_CLASS = getattr(settings, "CHUNKED_UPLOADS_STORAGE_CLASS", None)
if STORAGE_CLASS:
    storage = STORAGE_CLASS()
else:
    storage = None


def get_storage_path(obj, fname):
    return os.path.join("chunked_uploads", obj.uuid, fname)


STORAGE_PATH = getattr(settings, "CHUNKED_UPLOADS_STORAGE_PATH", None)
if STORAGE_PATH:
    storage_path = STORAGE_PATH
else:
    storage_path = get_storage_path


def get_chunks_storage_path(obj, fname):
    return os.path.join("chunked_uploads", obj.upload.uuid, "chunks", "chunk")

CHUNKS_STORAGE_PATH = getattr(settings, "CHUNKED_UPLOADS_CHUNKS_STORAGE_PATH", None)
if CHUNKS_STORAGE_PATH:
    chunks_storage_path = CHUNKS_STORAGE_PATH
else:
    chunks_storage_path = get_chunks_storage_path


class File(FileProxyMixin):
    """
    This is needed as there was a bug pre-1.4 django with getting
    size off of a file object
    """
    def __init__(self, file):  # @ReservedAssignment
        self.file = file

    @property
    def size(self):
        pos = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(pos)
        return size


class Upload(models.Model):

    STATE_UPLOADING = 1
    STATE_COMPLETE = 2
    STATE_STITCHED = 3
    STATE_UPLOAD_ERROR = 4

    STATE_CHOICES = [
        (STATE_UPLOADING, "Uploading"),
        (STATE_COMPLETE, "Complete - Chunks Uploaded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="uploads")
    uuid = UUIDField(auto=True, unique=True)
    filename = models.CharField(max_length=250)
    filesize = models.IntegerField()
    upload = models.FileField(max_length=250, upload_to=storage_path)
    md5 = models.CharField(max_length=32, blank=True)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_UPLOADING)
    created_at = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return u"<%s - %s bytes - pk: %s, uuid: %s, md5: %s>" % (
            self.filename, self.filesize, self.pk, self.uuid, self.md5
        )

    def stitch_chunks(self):
        fname = os.path.join(
            self.upload.storage.location,
            storage_path(self, self.filename + ".tmp")
        )
        try:
            os.makedirs(os.path.dirname(fname))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        try:
            fp = open(fname, "wb")
            m = hashlib.md5()
            for chunk in self.chunks.all().order_by("pk"):
                bytes = chunk.chunk.read()  # @ReservedAssignment
                m.update(bytes)
                fp.write(bytes)
                chunk.chunk.close()
            fp.close()
        except Exception, e:
            if os.path.exists(fname):
                os.remove(fname)
            self.delete()
            raise

        try:
            temp_file = open(fname, "rb")
            f = File(temp_file)
            self.upload.save(
                name=self.filename,
                content=UploadedFile(
                    file=f,
                    name=self.filename,
                    size=f.size
                )
            )
            temp_file.close()
        except Exception, e:
            if os.path.exists(fname):
                os.remove(fname)
            self.delete()
            raise

        self.md5 = m.hexdigest()
        self.state = Upload.STATE_COMPLETE
        self.save()
        os.remove(fname)

    def delete(self):
        #get upload path
        upload_path = os.path.join(settings.MEDIA_ROOT, storage_path(self, self.filename))
        self.remove_related_chunks()
        #remove upload from bdd
        super(Upload, self).delete()
        #try to delete the upload if exists
        if os.path.exists(upload_path):
            os.remove(upload_path)

        #delete the upload dir if empty
        if os.path.exists(os.path.dirname(upload_path)):
            if not os.listdir(os.path.dirname(upload_path)):
                os.rmdir(os.path.dirname(upload_path))

    def remove_related_chunks(self):
        for chunk in self.chunks.all().order_by("pk"):
            chunk.delete()

    def uploaded_size(self):
        return self.chunks.all().aggregate(
            models.Sum("chunk_size")
        ).get("chunk_size__sum")


class Chunk(models.Model):

    upload = models.ForeignKey(Upload, related_name="chunks")
    chunk = models.FileField(upload_to=chunks_storage_path)
    chunk_size = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return u"<Chunk pk=%s, size=%s, upload=(%s, %s)>" % (
            self.pk, self.chunk_size, self.upload.pk, self.upload.uuid
        )

    def delete(self):
        #get chunk path
        chunk_path = os.path.join(settings.MEDIA_ROOT, str(self.chunk))
        #deletion of chunk in bdd
        super(Chunk, self).delete()
        #deletion of chunk file
        if os.path.exists(chunk_path):
            os.remove(chunk_path)

        #delete the chunk dir if empty
        if os.path.exists(os.path.dirname(chunk_path)):
            if not os.listdir(os.path.dirname(chunk_path)):
                os.rmdir(os.path.dirname(chunk_path))


class ApiAccess(models.Model):
    """A simple model for use with the ``CacheDBThrottle`` behaviors."""
    identifier = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default='')
    request_method = models.CharField(max_length=10, blank=True, default='')
    accessed = models.PositiveIntegerField()

    def __unicode__(self):
        return u"%s @ %s" % (self.identifer, self.accessed)

    def save(self, *args, **kwargs):
        self.accessed = int(time.time())
        return super(ApiAccess, self).save(*args, **kwargs)


if 'django.contrib.auth' in settings.INSTALLED_APPS:
    import uuid

    class ApiKey(models.Model):
        user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='chunked_upload_api_key')
        key = models.CharField(max_length=256, blank=True, default='')
        created = models.DateTimeField(default=datetime.datetime.now)

        def __unicode__(self):
            return u"%s for %s" % (self.key, self.user)

        def save(self, *args, **kwargs):
            if not self.key:
                self.key = self.generate_key()

            return super(ApiKey, self).save(*args, **kwargs)

        def generate_key(self):
            # Get a random UUID.
            new_uuid = uuid.uuid4()
            # Hmac that beast.
            return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()

    def create_api_key(**kwargs):
        """
        A signal for hooking up automatic ``ApiKey`` creation.
        """
        logging.debug("kwargs : " + str(kwargs))
        logging.debug("kwargs2 : " + str(kwargs.get('created')))
        logging.debug("kwargs2 : " + str(kwargs.get('instance')))
        if kwargs.get('created') is True:
            ApiKey.objects.create(user=kwargs.get('instance'))
