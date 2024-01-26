
from pathlib import Path
from django.conf import settings
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=!g%8ufcuc!q018+!-$g6ktfvy=b7kg)gmn)1_4e^&9ln19*+c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
   
]




LOCAL_APPS = [
    
     'Apps.nomina_app',
    'Apps.users',

]

#THIRDPARTY_APPS = (
#  'djcelery',
#  'sizefield',
#  'maintenance_mode'
#)

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS 


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portal_nomina.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/ 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': [BASE_DIR /'templates'],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'django.template.context_processors.debug',
#                'django.template.context_processors.request',
#                'django.contrib.auth.context_processors.auth',
#                'django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]


WSGI_APPLICATION = 'portal_nomina.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# 
# DATABASES = {
    # 'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
    # }
# }
# 

##  DATABASE POSTGRESQL



DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "portal_nomina_v310",
        "USER": "nomina_user",
        "PASSWORD": "nomina_user",
        "HOST": "localhost",
        "PORT": "",
      
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
#STATICFILES_DIRS = [BASE_DIR /  'static']

STATIC_URL_USERS =  'static/users/images/'

TEMPORARY_QR = os.path.join(BASE_DIR + STATIC_URL, 'temporary')
if not os.path.exists(TEMPORARY_QR):
    os.mkdir(TEMPORARY_QR)
    
STATICFILES_DIRS = (
  BASE_DIR.child('static'),
  TEMPORARY_QR
  )


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/secure'




MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

"""
Additional Data
"""

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "amexiproc.test@gmail.com"
EMAIL_HOST_PASSWORD = "6193dcd78e9cee"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

FK_INC_URL = "https://demo-facturacion.finkok.com/servicios/soap/inc.wsdl"
FK_STAMP_URL = 'https://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl'
#FK_STAMP_URL = 'https://app2-demo.facturacion.finkok.com/servicios/soap/stamp.wsdl'
FK_CANCEL_URL = 'https://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl'
#FK_CANCEL_URL = 'https://app2-demo.facturacion.finkok.com/servicios/soap/cancel.wsdl'
FK_USERNAME = 'finkok_test@alfredo.com'
FK_PASSWORD = 'f1nk0K#17'
FK_NO_CER = '20001000000300022762'

''' el smtp es 10.0.3.12
user: proveedor
passw: g2dMRg99wauf'''
FK_UTILITIES_URL = 'https://demo-facturacion.finkok.com/servicios/soap/utilities.wsdl'
FK_REGISTRATION_URL = "https://demo-facturacion.finkok.com/servicios/soap/registration.wsdl"
NOTIFICATION_ADD_BUSINESS_EMAILS = ["tigreac96@gmail.com"]






CERTIFICATE_STORAGE = Path(BASE_DIR, 'cfdi', 'sat_certificados')

INVOICE_STORAGE = Path(BASE_DIR, 'tmp/')


CERTIFICATE_STORAGE = Path(CERTIFICATE_STORAGE, 'local')

INVOICE_STORAGE = Path(BASE_DIR, '/var/')
SIGNED_STORAGE = Path(BASE_DIR, '/var/')

if DEBUG:
  INVOICE_STORAGE = Path('/tmp/')
  SIGNED_STORAGE = Path('/tmp/')

SESSION_COOKIE_AGE = 1500000

VALIDATE_CFDI = False

USERNAME_FK = 'ccalix@finkok.com.mx'
PASSWORD_FK = 'Legoland1953!'