from ._base import *

DEBUG = False

WEBSITE_URL = 'http://127.0.0.1:8000/'

ALLOW_REGISTRATION = True

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

INSTALLED_APPS.extend([
    'udemy.apps.core',
])
