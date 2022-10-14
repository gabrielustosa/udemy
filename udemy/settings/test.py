from ._base import *

DEBUG = False

WEBSITE_URL = 'http://127.0.0.1:8000/'

ALLOW_REGISTRATION = True

DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
