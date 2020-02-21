import os
import urllib.parse
from Main.Toolbox import Toolbox

tlbx = Toolbox()
tlbx.loadConfigFile()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "8^&49y1q@bk$e!se63y77^m&eqbt7hpdobl4cl(eg7$9rg-y7p"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*','app.djangobaseapp','djangobaseapp','localhost','127.0.0.1']
# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # 'djangobaseapp.apps.djangobaseappConfig',
    'djangobaseapp',
    'sweetify',
    'django_celery_beat',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Main.urls' # garbage

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['Page_templates'],#'/home/chris/xs/ys/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]


#WSGI_APPLICATION = 'Main.wsgi.application' # garbage
AUTH_USER_MODEL = 'djangobaseapp.User'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     tlbx.CONFIG['pgsql']['name'],
        'USER':     tlbx.CONFIG['pgsql']['user'],
        'PASSWORD': tlbx.CONFIG['pgsql']['pass'],
        'HOST':     tlbx.CONFIG['pgsql']['host'],
        'PORT':'5432',
    }
}

###     With Redis Queue
#CELERY_BROKER_URL = 'redis://localhost:6379'
#CELERY_RESULT_BACKEND = 'redis://localhost:6379'

###     With Amazon SQS key
CELERY_BROKER_URL = 'sqs://{access_key}:{secret_key}@'.format(
    access_key = tlbx.CONFIG['amazonsqs']['access']
    , secret_key = urllib.parse.quote(tlbx.CONFIG['amazonsqs']['secret'], safe=''))

CELERY_RESULT_BACKEND = 'db+postgresql://{user}:{passw}@{host}/{dbname}'.format(
    user        = tlbx.CONFIG['pgsql']['user']
    , passw     = tlbx.CONFIG['pgsql']['pass']
    , host      = tlbx.CONFIG['pgsql']['host']
    , dbname    = tlbx.CONFIG['pgsql']['name'])

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
#CELERY_TIMEZONE = TIME_ZONE


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}
# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Update database configuration with $DATABASE_URL.
#db_from_env = dj_database_url.config(conn_max_age=500)
#DATABASES['default'].update(db_from_env)

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



#SESSION_ENGINE = "django.contrib.sessions.backends.cache"
#SESSION_ENGINE = 'main.session_backend'
SESSION_CACHE_ALIAS = "default"

#   ACCORDING TO DJANGO DOCS: This should only be enabled 
#       if a proxy which sets this header is in use.

USE_X_FORWARDED_HOST=True
FAVICON_PATH = STATIC_URL + 'images/favicon.png'

EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'SMTP_Injection'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
