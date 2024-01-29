
from pathlib import Path
from django.conf import settings
from .headers import  *
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
    'rest_framework',
    'rest_framework.authtoken',
    #'rest_authtoken',
   
]


LOCAL_APPS = [
    
    'Apps.nomina_app',
    'Apps.users',
    'Apps.services',

]

#THIRDPARTY_APPS = (
#  'djcelery',
#  'sizefield',
#  'maintenance_mode'
#)

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS 

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
       'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
      'rest_framework.authentication.TokenAuthentication',
    ],
}



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


TEMPORARY_QR = os.path.join(BASE_DIR, STATIC_URL, 'temporary')


STATICFILES_DIRS = [
    BASE_DIR / "static",
    "TEMPORARY_QR",
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/secure'



MEDIA_ROOT = '/tmp/media/'
MEDIA_URL = '/media/'

# STATIC_DIRS = (
#     '/tmp/'
# )

#AUTH_USER_MODEL = 'users.Profile'

FIXTURE_DIRS = (
  'fixtures/',
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

"""
Additional Data
"""






''' el smtp es 10.0.3.12
user: proveedor
passw: g2dMRg99wauf'''
FK_UTILITIES_URL = 'https://demo-facturacion.finkok.com/servicios/soap/utilities.wsdl'
FK_REGISTRATION_URL = "https://demo-facturacion.finkok.com/servicios/soap/registration.wsdl"
NOTIFICATION_ADD_BUSINESS_EMAILS = ["tigreac96@gmail.com"]



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



DEFAULT_FROM_EMAIL = 'soporte@finkok.com'

ACCOUNT_ACTIVATION_DAYS = 7

CERTIFICATE_STORAGE = Path(BASE_DIR, 'cfdi', 'sat_certificados')

INVOICE_STORAGE = Path(BASE_DIR, 'tmp/')


INVOICE_STORAGE = Path(BASE_DIR, '/var/')
SIGNED_STORAGE = Path(BASE_DIR, '/var/')

if DEBUG:
  INVOICE_STORAGE = Path('/tmp/')
  SIGNED_STORAGE = Path('/tmp/')

SESSION_COOKIE_AGE = 1500000

VALIDATE_CFDI = False
USERNAME_FK = 'ccalix@finkok.com.mx'
PASSWORD_FK = 'Legoland1953!'





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



####################33

CFDI_VERSION_32 = '3.2'
CFDI_VERSION_33 = '3.3'
XSD_NAME_32 = 'cfdv32.xsd'
XSD_NAME_33 = 'cfdv33.xsd'
XSLT_NAME_32 = 'cadenaoriginal_3_2.xslt'
XSLT_NAME_33 = 'cadenaoriginal_3_3.xslt'

LAST_VERIFICATION_DATE = 10 # MINUTES

#cloudinary.config( 
#  cloud_name = "dtarr1v4t", 
#  api_key = "171591724155349", 
#  api_secret = "SjIwDdz5IinAcFvFeQHt0n7IT9o" 
#)
#  