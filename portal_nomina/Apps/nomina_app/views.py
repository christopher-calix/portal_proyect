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
from Apps.users.models import User
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



#@method_decorator(login_required(login_url='/'), name='dispatch')
#@get_query_history  # Assuming this decorator is compatible with Python 3
#@get_default_account  # Assuming this decorator is compatible with Python 3
#class HistoryView(View):
#
#    def get(self, request, *args, **kwargs):
#        template = 'history/history.html'
#        context = {'filter_form': HistoryFilterForm()}
#        return render(request, template, context)
#
#    def post(self, request, *args, **kwargs):
#        try:
#            form = HistoryFilterForm(request.POST)
#            if form.is_valid():
#                query = form.cleaned_data['query']
#                account = kwargs['account']
#                active_taxpayer_id = kwargs['active_taxpayer_id']
#
#                list_history = History.objects.filter(query).order_by('-date')
#                list_history = list_history.filter(
#                    Q(business__taxpayer_id=active_taxpayer_id) | Q(employee=account)
#                )
#                total = list_history.count()
#
#                start = int(request.POST.get('iDisplayStart'))
#                length = int(request.POST.get('iDisplayLength'))
#                list_history = list_history[start:start+length]
#
#                list_result = []
#                for history in list_history:
#                    options_dict = {'details': {
#                        'detail': reverse('details_history', kwargs={'id_history': history.id})
#                    }}
#                    options = render_to_string('history/options.html', options_dict, request)
#                    user = '<span class="label label-emails" title="">{}</span>'.format(history.business.email[0])
#                    list_result.append([
#                        user,
#                        history.business.taxpayer_id,
#                        history.date.strftime("%Y-%m-%d %H:%M:%S"),
#                        history.totales_files,
#                        history.successful_files,
#                        history.failed_files,
#                        options
#                    ])
#
#                result = {
#                    'aaData': list_result,
#                    'iTotalRecords': total,
#                    'iTotalDisplayRecords': total,
#                }
#                return JsonResponse(result)
#
#        except ObjectDoesNotExist:
#            # Handle case where History objects are not found
#            pass
#
#        except Exception as e:
#            print(str(e))  # Log exception for debugging
#            raise  # Re-raise the exception for higher-level h


class Dashboard(TemplateView):
     template_name = 'views/main_views/dashboard.html'
     
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

