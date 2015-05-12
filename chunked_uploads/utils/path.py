"""
Some small file related utilities
"""
import os
from django.template.defaultfilters import slugify


def sanitize_filename(uncleaned_filename):
    fileName, fileExtension = os.path.splitext(uncleaned_filename)
    cleanedFilename = slugify(fileName)
    return (cleanedFilename + fileExtension).replace('-', '_')
