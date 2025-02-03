# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
#import environ
from decouple import config
from unipath import Path
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## Initialize environment variables
#env = environ.Env()
## Load environment variables from the .env file
#environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# load production server from .env
ALLOWED_HOSTS = [
    'test-cop.copromanager.com', 'www.test-cop.copromanager.com', '35.180.33.83',
    'your.copromanager.pro', 'www.your.copromanager.pro', '142.93.235.205',
    'localhost', '127.0.0.1', config('SERVER', default='127.0.0.1'),
    '192.168.157.182', '0.0.0.0'
]

# To route traffic through OWASP ZAP for testing
PROXY = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

# Set secure headers (Optional but recommended for production)
CSRF_TRUSTED_ORIGINS = [
    'https://test-cop.copromanager.com',
    'https://www.test-cop.copromanager.com',
    'https://your.copromanager.pro',
    'https://www.your.copromanager.pro',
]

# Allow all origins to access the API
# CORS_ALLOW_ALL_ORIGINS = True  # Not recommended for production

# Alternatively, you can specify allowed origins like this:
# CORS_ALLOWED_ORIGINS = [
#     'https://example.com',
#     'https://sub.example.com',
# ]

# Other CORS settings you might use
CORS_ALLOW_CREDENTIALS = True  # Allow cookies and HTTP authentication


# Login URL for authentication redirects
LOGIN_URL = 'two_factor:login'
#LOGIN_REDIRECT_URL = reverse_lazy('redirect-based-on-role')  # Map to the role redirection logic
LOGIN_REDIRECT_URL = 'dashboard-supersyndic/<int:supersyndic_id>/'
LOGOUT_REDIRECT_URL = 'home'

# Optional: Customize 2FA settings
TWO_FACTOR_PATCH_ADMIN = True  # Apply 2FA to Django admin
TWO_FACTOR_LOGIN_TEMPLATE = 'two_factor/register-login-super-user.html'
TWO_FACTOR_QR_FACTORY = 'qrcode.image.pil.PilImage'  # Generates QR codes for authenticator apps

# Optional: Control when users should be redirected to setup
TWO_FACTOR_AUTO_SETUP = False  # If False, users must manually complete the setup

#OTP_EMAIL_SENDER = config("EMAIL_HOST_USER")

# reCAPTCHA settings for v2 and v3
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY')

RECAPTCHA_REQUIRED_SCORE = 0.85  # For reCAPTCHA v3

# Set secure headers (Optional but recommended for production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Ensuring security settings are enforced only in production
SESSION_COOKIE_SECURE = not config('DEBUG', default=True, cast=bool)
CSRF_COOKIE_SECURE = not config('DEBUG', default=True, cast=bool)
SECURE_SSL_REDIRECT = not config('DEBUG', default=True, cast=bool)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 10800  # 3h 

# Use production email settings only if DEBUG is False
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_recaptcha',
    # 2AF Authentication
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_email',  # <- if you want email capability.
    #'otp_yubikey',
    'two_factor',
    'two_factor.plugins.phonenumber',  # <- if you want phone number capability.
    'two_factor.plugins.email',  # <- if you want email capability.
    #'two_factor.plugins.yubikey',  # <- for yubikey capability.
    
    'apps.authentication',
    'apps.home',  # Enable the inner home (home)

    'apps.superadmin',
    'apps.syndic',
    'apps.supersyndic',
    'apps.coproprietaire',
    'apps.prestataire',
    'apps.user',
    'apps.residence',
    'apps.association',
    'apps.import_data', 

    #'rest_framework',
    #'corsheaders',
]

AUTH_USER_MODEL = 'authentication.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    #that detects the user's preferred language from their browser settings or session and applies it
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 2AF Authentication
    'django_otp.middleware.OTPMiddleware',
]

MIDDLEWARE += [
    'core.middleware.ThreadLocals',
    ]


ROOT_URLCONF = 'core.urls'

TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'apps/authentication/templates'),
            #os.path.join(BASE_DIR, 'apps/dashboard/templates'),
            ],
        #'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

## # Better for Production
#DATABASES = {
#    'default': env.db('DATABASE_URL', default='postgresql://postgres:Toure7Medina@localhost:5432/real_copromanager'),
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR.child('db.sqlite3')),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
    ('es', _('Spanish')),
    ('pt', _('Portuguese')),
]

LOCALE_PATHS = [
    os.path.join(CORE_DIR, 'locale'),
    #os.path.join(CORE_DIR, '..', 'locale'),
    os.path.join(BASE_DIR, 'env', 'lib', 'python3.10', 'site-packages', 'two_factor', 'locale')  # two_factor app's locale folder
]

LANGUAGE_CODE = 'en'  # Default language
LANGUAGE_COOKIE_NAME = 'django_language'  # Default is 'django_language'
LANGUAGE_COOKIE_PATH = '/'  # Optional: Path scope for the language cookie
LANGUAGE_COOKIE_AGE = 31536000  # 1 year

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)


# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#############################################################
#############################################################

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
