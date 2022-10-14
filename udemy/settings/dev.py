from ._base import *

WEBSITE_URL = 'http://127.0.0.1:8000/'

ALLOW_REGISTRATION = True

INSTALLED_APPS.extend([
    'django_browser_reload',
])

MIDDLEWARE.extend([
    'django_browser_reload.middleware.BrowserReloadMiddleware',
])

# Tailwind config

TAILWIND_APP_NAME = 'theme'
