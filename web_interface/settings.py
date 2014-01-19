# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *
DATABASES['default']['HIGH_REPLICATION'] = True

import os

import socket

DEBUG=False

ALLOWED_HOSTS = [
    '*', # Allow domain and subdomains
]

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
)

# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF = 'indexes'

SECRET_KEY = 'your_secret_key'#all apps should use this same key


DBINDEXER_BACKENDS = (
    'dbindexer.backends.BaseResolver',
    'dbindexer.backends.FKNullFix',
    'dbindexer.backends.InMemoryJOINResolver',
    'dbindexer.backends.ConstantFieldJOINResolver', 
    )


LOGIN_REDIRECT_URL = '/door/admin'
LOGIN_URL = '/door/login'


SUIT_CONFIG = {
    'ADMIN_NAME': 'Enjigo Sentry',
    'MENU_ICONS': {
        'galleries': 'icon-th-large',
        'shorty': 'icon-magnet',
        'blog': 'icon-road',
        'decorations': 'icon-fire',
        'store':'icon-shopping-cart',
        'background': 'icon-picture',
        'appsettings': 'icon-wrench',
        'about': 'icon-user',
        'navigation': 'icon-th-list',
        'door': 'icon-lock',
        'config': 'icon-cog'
    },
     'MENU_EXCLUDE': ('auth.group', 'sites'),
}

AUTHENTICATION_BACKENDS = {
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
}

INSTALLED_APPS = (
    'suit_redactor',
    'suit',
    #'appsettings',
    #'django.contrib.sites',
    #'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'permission_backend_nonrel',
    'autoload',
    'dbindexer',
    'bootstrap_toolkit',
    'door',
    'search',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

CONFIG_DEFAULT_SETTINGS = {
    #group/app
    'testSettings':{
        #key/display name : value, help text, read_only
        'setting_one' : ('first value','helpt text', True),
        'setting_two' : ('second value','more helpt text', False)
    }
    

}



# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

BASE_URL = socket.gethostname()

ADMIN_MEDIA_PREFIX = '/media/admin/'
STATIC_URL = '/media/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'
