import hashlib
import uuid

from django.conf import settings


def get_secret(string):
    md5 = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    md5.update(string.encode('utf-8'))
    return md5.hexdigest()


def get_key():
    return get_secret(str(uuid.uuid4()))
