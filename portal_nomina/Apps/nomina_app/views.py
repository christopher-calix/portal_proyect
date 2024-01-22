from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .views_choices import *

from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
###########################################3333

# -*- coding: utf-8 -*-


from django.db.models import Q
from django.conf import settings

from django.core.files import File
from django.core import signing

from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied

from django.urls import reverse

from django.views.decorators.cache import cache_page
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMessage, BadHeaderError

from .models import Business, Employee, TokensUser, SatFile
from django.db.models import Avg, Count, Min, Sum
from .models import Notifications
from .models import PayRoll
from .models import History
from .models import DetailsHistory
from .models import Address, News
from .models import Upload
from .models import PayrollReport
#from .tasks import import_upload, send_mail_payroll, generate_report_payrolls, generate_report_payrolls_employee
from django.db import transaction
from Apps.users.models import Profile
import re
import time
import zipfile
import rarfile
import json
from decimal import Decimal
from .stamp import FINKOKWS
from .utils import *


from .decorators import *

from lxml import etree
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.db import transaction, IntegrityError
from django.core.validators import validate_email
import os
import PyPDF2
import locale
from celery.result import AsyncResult
#import cloudinary.api
#import cloudinary.uploader
from pdb import set_trace
import tempfile
import base64
from M2Crypto import X509
from M2Crypto import EVP
import qrcode
import pyminizip
import random
import string
#from rest_framework.authtoken.models import Token
from .cem.utils import FinkokWS
from suds.client import Client as suds_client

#################################333

from django.shortcuts import redirect
from django.views import View
from django.template.response import TemplateResponse
from .models import Employee







@method_decorator(login_required(login_url='/'), name='dispatch')

class Dashboard(TemplateView):
    template_name = 'views/main_views/dashboard.html'

    def get(self, request, *args, **kwargs):
        extra_content = {}
        if request.user.profile.is_authenticated and request.user.profile.role == 'E':
                taxpayer_id = request.session.get('active_account')
        if not taxpayer_id:
                    taxpayer_id = Employee.objects.filter(user=request.user)[0].taxpayer_id
               # extra_content = get_extra_content(taxpayer_id, request.user.role)
        

        if request.user.profile.role == 'S':
        
            return redirect('')

        return TemplateResponse(request, self.template_name, extra_content)
     
     
    #   if request.user.is_authenticated:
    #    return HttpResponseRedirect(reverse('nomina_app:dashboard'))
    #return render(request, 'auth/login.html')
     
     
     
class Company(TemplateView):
     template_name = 'views/main_views/companies.html'
     
    

class Users(TemplateView):
     template_name = 'views/main_views/users.html'
     
class Employees(TemplateView):
     template_name = 'views/main_views/employees.html'

class Vouchers(TemplateView):
     template_name = 'views/main_views/vouchers.html'

class Uploads(TemplateView):
     template_name = 'views/main_views/uploads.html'
     
     
     
####################################################################################################

