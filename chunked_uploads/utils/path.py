"""
Some small file related utilities
"""

import string
import unicodedata

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)


def sanitize_filename(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').lower()
    return ''.join(c for c in cleanedFilename if c in validFilenameChars).replace(' ', '_')
    
