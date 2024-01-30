from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseNotFound



from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django.views import View
from .views_choices import *

from django.contrib.auth.decorators import login_required

from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
###########################################3333

# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.db.models import Q
from django.conf import settings

from django.core.files import File
from django.core import signing

from django.http import Http404
from django.http import JsonResponse
from django.http import HttpResponseRedirect

from django.urls import reverse

from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
#from django.contrib.staticfiles.templatetags.staticfiles import static

from django.core.mail import send_mail, EmailMessage, BadHeaderError

from .models import Business, Employee, TokensUser, SatFile
from django.db.models import Avg, Count, Min, Sum
from .models import Notifications, PayRoll, History, DetailsHistory, Address, News, Upload, PayrollReport, Employee

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

from django.urls import reverse_lazy
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
from django.shortcuts import redirect



@method_decorator(login_required(login_url='user:login'), name='dispatch')
class Dashboard(View):
    
    
    template_name = 'views/main_views/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        #import pdb;set_trace();
        extra_content = {}
        if request.user.is_authenticated == True and request.user.profile.role == 'E':
            taxpayer_id = request.session.get('active_account', None)
            
            if not taxpayer_id:
                taxpayer_id = request.user.employee.taxpayer_id

        elif request.user.is_authenticated == True and request.user.profile.role in ('S'):
            return redirect(reverse('nomina_app:company')) 
        
        elif request.user.is_authenticated == True and request.user.profile.role in ('A'):

            return render(request, self.template_name, extra_content)
    
    
  

     

     
     
@method_decorator(login_required(login_url='user:login'), name='dispatch')     
#pendiente el quer_get

class Company(TemplateView):

     name = Business
     template_name = 'views/main_views/companies.html'
     
   

     def post(self, request, *args, **kwargs):
         query = request.POST.get('query')
 
         if request.is_ajax():
             start = int(request.POST.get('iDisplayStart'))
             length = int(request.POST.get('iDisplayLength'))
             ltype = request.POST.get('ltype')
             role = request.user.profile.role
 
             try:
                 accounts = Business.objects.filter(query).exclude(status='R').order_by("taxpayer_id")
                 active_account = request.session.get('active_account', None)
                 if active_account and request.user.profile.role == 'B':
                     accounts = accounts.filter(taxpayer_id=active_account)
                 total = accounts.count()
                 accounts = accounts[start:start+length]
 
                 users_list = []
                 for account in accounts.iterator():
                     user = account.user.profile.filter(role='B')[0]
                     email = user.profile.email
                     options = render_to_string('admin/business_options.html', {'status': account.status, 'account_id': account.id, 'user_id': user.id, 'role': role, 'taxpayer_id': account.taxpayer_id})
                     emails = render_to_string('admin/business_emails.html', {'emails': account.email})
                     users_list.append([account.taxpayer_id, account.name, email, emails, STATUS_ACCOUNT[account.status], options])
 
                 result = {
                     'aaData': users_list,
                     'iTotalRecords': total,
                     'iTotalDisplayRecords': total,
                 }
                 return JsonResponse(result)
 
             except Exception as e:
                 print("Error al listar los negocios:", str(e))
                 raise Http404
 
         else:
             raise Http404

     def dispatch(self, request, *args, **kwargs):
         try:
             return super().dispatch(request, *args, **kwargs)
         except:
             return HttpResponseRedirect(reverse('nomina_app:dashboard'))
     
    

class Users(TemplateView):
     
     model = Profile
     template_name = 'views/main_views/users.html'
     
     def post(self, request, query, *args, **kwargs):
        try:
            if request.is_ajax():
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))
                users = Profile.objects.filter(query).order_by("id")[start:start+length]
                total = users.count()
                users_list = []
                for user in users:
                    role = user.profile.role
                    status = user.is_active
                    last_login = user.last_login
                    name = user.profile.name
                    email = user.profile.email
                    options = render_to_string('admin/user_options.html', {'status': status, 'mail': email, 'user_id': user.id}, request)
                    users_list.append([last_login, name, email, TYPEUSER[status], TYPEROLE[role], options])
                result = {
                    'aaData': users_list,
                    'iTotalRecords': total,
                    'iTotalDisplayRecords': total,
                }
                return JsonResponse(result)
            else:
                return HttpResponseRedirect(reverse('nomina_app:dashboard'))
        except Exception as e:
            return HttpResponseRedirect(reverse('nomina_app:dashboard'))

class UserOptions(TemplateView):
     
     model = Profile
     template_name = 'admin/userOptions'
     
     def post(self, request, query, *args, **kwargs):
          
           query = request.POST.get('query')
           
           success, message = False, ''
           data = {}
           try:
             if request.method == 'POST' and request.is_ajax():
               option = request.POST.get('option')
      
               try:
                 active_account = kwargs['account']
               except:
                 pass
               try:
                 active_taxpayer_id = kwargs['active_taxpayer_id']
               except:
                 pass
               if option == 'get-info':
                 user_id = request.POST.get('user_id', None)
                 if user_id is not None:
                   response = {}
                   user = Profile.objects.get(id=user_id)
                   name = user.profile.name
                   email = user.profile.email
                   businesses = Business.objects.filter(user=user).values_list('id')
      
                   response.update({
                     'info': {
                       'edit_user_id': user_id,
                       'edit_username': email,
                       'edit_firstname': name,
                       'edit_role': user.role,
                       'edit_businesses': list(businesses),
                     }
                   })
                   success, message = True, response
                 else:
                   message = 'Intenta mas tarde'
               if option == 'edit-user':
                 message = u'Error actualizando la información del usuario.'
                 try:
                   with transaction.atomic():
                     user_id = request.POST.get('user_id')
                     username = request.POST.get('username')
                     name = request.POST.get('name')
                     role = request.POST.get('type')
                     new_businesses = request.POST.getlist('businesses[]')
                     new_password = request.POST.get('password', None)
      
                     user = Profile.objects.get(id=user_id)
                     user.username = username
                     user.profile.email = username
                     user.profile.name = name
                     if new_password is not None:
                       user.set_password(new_password)
      
                     if user.profile.role == 'S':
                       if not len(new_businesses):
                         raise Exception('Debes seleccionar al menos un negocio.')
                       businesses = Business.objects.filter(status='A')
                       for business in businesses:
                         business_users = business.user.all()
                         if (str(business.id) not in new_businesses) and (user in business_users):
                           business.user.remove(user)
                           business.save()
                         elif (str(business.id) in new_businesses) and (user not in business_users):
                           business.user.add(user)
                           business.save()
                     user.save()
                     success = True
                     message = u'La información del usuario ha sido actualizada.'
                 except IntegrityError:
                   print ("Exception user_options update-info => Username already exists.")
                   message = 'Ese usuario ya esta en uso.'
                 except Exception as e:
                   print ("Exception user_options update-info => " + str(e))
                   message = str(e)
               if option == 'add-user':
                 try:
                   username = request.POST.get('username', None)
                   name = request.POST.get('name', None)
                   _type = request.POST.get('type', None)
                   selected_businesses = request.POST.getlist('businesses[]', [])
                   new_password = request.POST.get('password', None)
                   try:
                     validate_email(username)
                     try:
                       with transaction.atomic():
                         user, created = Profile.objects.get_or_create(email=username, is_superuser=False)
                         if created:
                           user.profile.email = username
                           user.profile.name = name
                           user.is_active = True
                           user.profile.role = _type
                           user.type_business = request.user.type_business
                           user.set_password(new_password)
                           user.save()
                           if _type == 'S':
                             businesses = Business.objects.filter(id__in=selected_businesses)
                             for business in businesses:
                               business.user.add(user)
                               business.save()
                           success = True
                           message = u'Usuario agregado exitosamente.'
                         else:
                           message = u'Usuario previamente registrado.'
                     except Exception as e:
                       print ('Exception user_options => adding user => ' + str(e))
                       message = 'Registrando nuevo usuario.'  
                   except Exception as e:
                     print ('Exception user_options => validate_email => ' + str(e))
                     message = 'Correo inválido.'
                 except Exception as e:
                   print ("Exception user_options add-user => " + str(e))
               if option == 'ADD':
                 ltype = request.POST.get('ltype')
                 taxpayer_id = request.POST.get('taxpayer_id')
                 name = request.POST.get('name')
                 status = request.POST.get('status')
                 email = request.POST.get('email')
                 pass1 = request.POST.get('password')
                 pass2 = request.POST.get('password2')
      
                 if taxpayer_id and name and status and email and pass1 and pass2:
                   if pass1 == pass2:
                     if ltype == 'B':
                       exists_email = Profile.objects.filter(email=email).exists()
                       exists_taxpayer_id = Business.objects.filter(taxpayer_id=taxpayer_id).exists()
                       if not exists_email:
                         if not exists_taxpayer_id:
                           user = Profile(email=email, role='B', is_active=bool(int(status)))
                           user.set_password(pass1)
                           user.save()
                           account = Business()
                           account.taxpayer_id = taxpayer_id
                           account.name = name
                           account.save()
                           account.user.add(user)
      
                           url = request.build_absolute_uri(reverse('dashboard'))
                           subject = 'ACCCESOS | PORTAL DE NOMINAS'
                           html_url = 'invoices/send_register_employe.html'
                           context = {'receiver_name': name, 'username': email, 'password': pass1, 'url': url}
                           info_user = {'username': email, 'password': pass1}
      
                           success, message = send_email(subject=subject, html_url=html_url, context=context, to_email=email) 
                         else:
                           message = 'Este RFC ya se encuentra registrado'
                       else:
                         message = 'Este correo ya se encuentra registrado'
                     elif ltype == 'E':
                       exists_email = Profile.objects.filter(email=email).exists()
                       exists_taxpayer_id = Employee.objects.filter(taxpayer_id=taxpayer_id).exists()
                       if not exists_email:
                         if not exists_taxpayer_id:
                           curp = request.POST.get('curp')
                           department = request.POST.get('department')
                           puesto = request.POST.get('puesto')
                           mbid = request.POST.get('mbid')
      
                           if curp and mbid and department and puesto:
                             is_active = status == "A"
                             user = Profile(email=email, role='E', is_active=is_active)
                             user.set_password(pass1)
                             user.save()
      
                             account = Employee()
                             account.name = name
                             account.email = [email]
                             account.curp = curp
                             account.taxpayer_id = taxpayer_id
                             account.status = status
                             business = Business.objects.get(taxpayer_id=active_taxpayer_id).id
                             account.business_id = business
                             account.department = department
                             account.position = puesto
                             account.mbid = mbid
                             account.user = user
                             account.save()
      
                             url = request.build_absolute_uri(reverse('dashboard'))
                             subject = 'ACCCESOS | PORTAL DE NOMINAS'
                             html_url = 'invoices/send_register_employe.html'
                             context = {'receiver_name': name, 'username': email, 'password': pass1, 'url': url}
                             info_user = {'username': email, 'password': pass1}
      
                             success, message = send_email(subject=subject, html_url=html_url, context=context, to_email=[email]) 
                           else:
                             message = 'Los campos que contienen * son requeridos'
                         else:
                           message = 'Este RFC ya se encuentra registrado'
                       else:
                         message = 'Este correo ya se encuentra registrado'
                   else:
                     message = 'Las contraseñas no coinciden'
                 else:
                   message = 'Los campos que contienen * son requeridos'
               elif option == 'AS':
                 user_id = request.POST.get('user_id')
                 user = Profile.objects.get(id=user_id)
                 if user.is_active:
                   user.is_active = False
                   message = "Usuario Desactivado"
                 else:
                   user.is_active = True
                   message = "Usuario Activado"
                 user.save()
                 success = True
               elif option == 'EDIT':
                 try:
                   action = request.POST.get('action')
                   if action == 'EU':
                     user_id = request.POST.get('user_id')
                     user = User.objects.get(id=user_id)
                     success = True
                     data.update({
                       'email': user.email
                     })
                   elif action == 'LA':
                     user_id = request.POST.get('user_id')
                     user_email = request.POST.get('mail',None)
                     if user_email is not None:
                       user = User.objects.get(email=user_email)
                     else:
                       user = User.objects.get(id=user_id)
                     if user.is_active:#.last_login and user.is_active:
                       auth_login(request, user)
                       success = True
                       message = u'Personalización correcta.'
                     else:
                       message = 'El usuario no ha activado su cuenta o no esta activo.'
                   elif action == 'SU':
                     try:
                       
                       account_id = request.POST.get('account_id')
                    
                       try:
                         account = Business.objects.get(id=account_id)#, taxpayer_id=active_account)
                       except:
                         account = Employee.objects.get(id=account_id)#, taxpayer_id=active_account)
                       account.status = 'S'
                       account.save()
                       success = True
                       message = 'Usuario suspendido'
                     except Exception as e:
                       message = 'Error al suspender'
                   elif action == 'AU':
                     try:
                       account_id = request.POST.get('account_id')
                     
                       try:
                         account = Business.objects.get(id=account_id)#, taxpayer_id=active_account)
                       except:
                         account = Employee.objects.get(id=account_id)#, taxpayer_id=active_account)
                       account.status = 'A'
                       account.save()
                       success = True
                       message = 'Usuario activado'
                     except Exception as e:
                       message = 'Error al activar'
                   elif action == 'RU':
                     try:
                       account_id = request.POST.get('account_id')
                   
                       try:
                         account = Business.objects.get(id=account_id)#, taxpayer_id=active_account)
                       except:
                         account = Employee.objects.get(id=account_id)#, taxpayer_id=active_account)
                       account.status = 'R'
                       account.save()
                       success = True
                       message = 'Usuario revocado'
                     except Exception as e:
                       message = 'Error al revocar'
                   elif action == 'VU':
                     try:
                       account_id = request.POST.get('account_id')
                  
                       try:
                         account = Business.objects.get(id=account_id)#, taxpayer_id=active_account)
                       except:
                         account = Employee.objects.get(id=account_id)#, taxpayer_id=active_account)
                       account.status = 'A'
                       account.save()
                       success = True
                       message = 'Usuario reactivado'
                     except Exception as e:
                       message = 'Error al reactivar'
                 except Exception as e:
                   message = 'Error al cargar datos'
               elif option == 'UPD':
                 try:
                   user_id = request.POST.get('user_id')
                   new_password_1 = request.POST.get('new_password_1')
                   new_password_2 = request.POST.get('new_password_2')
      
                   if new_password_1 and new_password_2: 
                     if new_password_1 == new_password_2:
                       user = User.objects.get(id=user_id)
      
                       user.set_password(new_password_1)
                       user.save()
      
                       success = True
                       message = 'Contraseña actualizada'
                     else:
                       message = 'Las contraseñas no coinciden'
                   else:
                     message = u'Contraseña invalida'
                 except Exception as e:
                   message = 'Error al actualizar'
               elif option == 'get_info_employee':
                 try:
                   employee_id = request.POST.get('employee_id', None)
                   if employee_id is not None:
                     employee_filter = Employee.objects.filter(id=employee_id)
                     if employee_filter.exists():
                       employee_obj = employee_filter[0]
                       message = {
                         "RFC": employee_obj.taxpayer_id,
                         "CURP": employee_obj.curp,
                         "ID": employee_obj.mbid,
                         "Nombre": employee_obj.name,
                         "Correo": employee_obj.user.profile.email,
                         "Estatus": employee_obj.status,
                         "Departamento": employee_obj.department,
                         "Puesto": employee_obj.position
                       }
                       success = True
                     else:
                       message = "El registro del empleado no existe"
                   else:
                     message = "El registro del empleado no existe"
                 except Exception as e:
                   print('Exception in get_info_employee => {}'.format(str(e)))
               elif option == 'edit_info_employee':
                
                 try:
                   employee_id = request.POST.get('employee_id', None)
                   if employee_id is not None:
                     employee_filter = Employee.objects.filter(id=employee_id)
                     if employee_filter.exists():
                       employee_obj = employee_filter[0]
                       user_obj = employee_obj.user.profile
      
                       taxpayer_id = request.POST.get('taxpayer_id', None)
                       curp = request.POST.get('curp', None)
                       mbid = request.POST.get('mbid', None)
                       name = request.POST.get('name', None)
                       email = request.POST.get('email', None)
                       status = request.POST.get('status', None)
                       department = request.POST.get('department', None)
                       puesto = request.POST.get('puesto', None)
      
                       if not None in (taxpayer_id, curp, mbid, name, email, status, department, puesto):
                     
                         if email != user_obj.email:
                           if User.objects.filter(email=email).exists():
                             return JsonResponse({
                               "success": False,
                               "message": 'El email ya se encuentra registrado'
                               })
      
                         if taxpayer_id != employee_obj.taxpayer_id:
                           if Employee.objects.filter(taxpayer_id=taxpayer_id).exists():
                             return JsonResponse({
                               "success": False,
                               "message": 'El RFC ya se encuentra registrado'
                               })
      
                         user_obj.email = email
                         user_obj.name = name
                         user_obj.save()
                         employee_obj.taxpayer_id = taxpayer_id
                         employee_obj.curp = curp
                         employee_obj.mbid = mbid
                         employee_obj.name = name
                         employee_obj.status = status
                         employee_obj.department = department
                         employee_obj.position = puesto
                         employee_obj.email = [email]
                         employee_obj.save()
                         success = True
                         message = 'El registro se actualizo exitosamente'
      
                       else:
                         message = "Todos los campos son requeridos"
                     else:
                       message = "El registro del empleado no existe"
                   else:
                     message = "El registro del empleado no existe"
                 except Exception as e:
                   print('Exception in get_info_employee => {}'.format(str(e)))
               elif option == 'get_business_emails':
                 business_id = request.POST.get('business_id', None)
                 if business_id is not None:
                   business_filter = Business.objects.filter(id=business_id)
                   if business_filter.exists():
                     business_obj = business_filter[0]
                     message = str(','.join(business_obj.email))
                     success = True
                   else:
                     message = "El negocio no existe"
                 else:
                   message = "No seleccionaste un negocio"
      
               elif option == 'set_business_emails':
                 business_id = request.POST.get('business_id', None)
                 if business_id is not None:
                   business_filter = Business.objects.filter(id=business_id)
                   if business_filter.exists():
                     business_obj = business_filter[0]
                     emails = request.POST.get('emails', None)
                     if emails:
                       business_obj.email = emails[:-1].split(',')
                       business_obj.save()
                       message = "El registro se actualizo exitosamente"
                       success = True
      
                   else:
                     message = "El negocio no existe"
                 else:
                   message = "No seleccionaste un negocio"
      
               elif option == 'get_business_send_emails':
                 business_id = request.POST.get('business_id', None)
                 if business_id is not None:
                   business_filter = Business.objects.filter(id=business_id)
                   if business_filter.exists():
                     business_obj = business_filter[0]
                     message = {
                       'send_mail_encryption': business_obj.send_mail_encryption,
                       'password': business_obj.password,
                       'name': '{} ({})'.format(business_obj.name, business_obj.taxpayer_id)
                     }
                     success = True
                   else:
                     message = "El negocio no existe"
                 else:
                   message = "No seleccionaste un negocio"
      
               elif option == 'set_business_send_emails':
                 business_id = request.POST.get('business_id', None)
                 if business_id is not None:
                   business_filter = Business.objects.filter(id=business_id)
                   if business_filter.exists():
                     business_obj = business_filter[0]
                     encrypted = request.POST.get('encrypted', "false")
                     encrypted_bool = True if encrypted == 'true' else False
                     encrypted_password = request.POST.get('encrypted_password', None)
                     business_obj.send_mail_encryption = encrypted_bool
                     business_obj.password = encrypted_password
                     business_obj.save()
                     message = "El registro se actualizo exitosamente"
                     success = True
                   else:
                     message = "El negocio no existe"
                 else:
                   message = "No seleccionaste un negocio"
      
           except Exception  as e:
             print ('Exception in user_options => %s' % e)
           data.update({
             'success': success,
             'message': message,
           })
           return JsonResponse(data)
     
     
class Employees(TemplateView):
    model = Employee
    template_name = 'views/main_views/employees.html'
    context_object_name = 'employees'

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        return Employee.objects.filter(query).order_by("taxpayer_id")

    def post(self, request, *args, **kwargs):
      start = int(request.POST.get('iDisplayStart'))
      length = int(request.POST.get('iDisplayLength'))
      query = request.GET.get('query', '')
      try:
        accounts = self.get_queryset()[start:start+length]
        total = accounts.count()
        users_list = []
        for account in accounts:
          status = account.status
          email = account.user.profile.email
          options = render_to_string('admin/options.html', {
            'status': status,
            'account_id': account.id,
            'user_id': account.user.id,
            'role': request.user.profile.role,
            'taxpayer_id': account.taxpayer_id
          })
          users_list.append([
            account.taxpayer_id,
            account.curp,
            account.name,
            email,
            account.department,
            account.position,
            STATUS_ACCOUNT[account.status],
            options
          ])
      except Exception as e:
        logging.error(str(e))  # Use logging for better error handling
        raise Http404
      return JsonResponse({
        'aaData': users_list,
        'iTotalRecords': total,
        'iTotalDisplayRecords': total
      })


class Vouchers(TemplateView):
    
    model = PayRoll
    template_name = 'views/main_views/vouchers.html'
    context_object_name = 'invoices'

    def post(self, request, *args, **kwargs):
        try:
            if request.is_ajax():
                total = 0
                list_result = []
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))

                account = kwargs['account']
                active_taxpayer_id = kwargs['active_taxpayer_id']

                list_invoices = PayRoll.objects.filter(kwargs['query'])
                if request.user.profile.role == "E":
                    list_invoices = list_invoices.filter(status='S')
                list_invoices = list_invoices.order_by('-id')

                total = list_invoices.count()
                list_invoices = list_invoices[start:start + length]

                for invoice in list_invoices.iterator():
                    uuid = str(invoice.uuid).upper() if invoice.uuid else ''
                    options_dict = {'invoice': {
                        'status': invoice.status,
                        'confirmed': invoice.signed,
                        'txt': reverse('txt', kwargs={'payroll_id': invoice.id}),
                        'download': reverse('download', kwargs={'payroll_id': invoice.id}),
                    }}
                    if invoice.status == 'S':
                       options_dict['invoice']['pdf'] = reverse('pdf', kwargs={'uuid': uuid})
                       options_dict['invoice']['uuid'] = uuid
                       options_dict['invoice']['taxpayer_id'] = invoice.taxpayer_id

                    error = invoice.notes
                    options = render_to_string('vouchers/options.html', options_dict, request)
                    invoice_status = render_to_string('vouchers/voucher_status.html', {'status': invoice.status, 'notes': invoice.notes}, request)
                    emission_date = invoice.emission_date.strftime("%Y-%m-%d %H:%M:%S") if invoice.emission_date is not None else invoice.emission_date
                    paid_date_from = ""
                    paid_date_to = ""
                    try:
                      paid_date_from = invoice.details.last().paid_date_from.strftime("%Y-%m-%d")
                    except:
                      pass
                    try:
                      paid_date_to = invoice.details.last().paid_date_to.strftime("%Y-%m-%d")
                    except:
                      pass


                    list_result.append([
                        uuid,
                        invoice.folio,
                        emission_date,
                        invoice.rtaxpayer_id,
                        invoice.rname,
                        paid_date_from,
                        paid_date_to,
                        invoice.total,
                        invoice_status,
                        INVOICE_SIGNED[invoice.signed],
                        options
                    ])

        except Exception as e:
            print(f'Exception in ListInvoicesView post method ==> {str(e)}')

        result = {
            'aaData': list_result,
            'iTotalRecords': total,
            'iTotalDisplayRecords': total,
        }
        return JsonResponse(result)

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name)

class Uploads(TemplateView):
     template_name = 'views/main_views/uploads.html'
     
     
     def post(self, request, *args, **kwargs):
        try:
            if request.is_ajax():
                result = {'aaData': [], 'iTotalRecords': 0, 'iTotalDisplayRecords': 0}
                business = kwargs['account']
                total = 0
                list_result = []
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))
                uploads_obj = Upload.objects.filter(business_id=business.id).filter(kwargs['query']).order_by('-id')
                total = uploads_obj.count()
                uploads = uploads_obj[start:start + length]

                for upload in uploads:
                    url_descarga = None
                    upload_id = render_to_string('uploads/strings/number.html', {'number': upload.task_id}, request)
                    user = render_to_string('uploads/strings/user.html', {'user': upload.user}, request)
                    filename = upload.name
                    date = upload.created
                    total_txts = render_to_string('uploads/strings/number.html', {'number': upload.total_txt}, request)
                    total_txt_good = render_to_string('uploads/strings/number.html', {'number': upload.total_txt_good}, request)
                    total_txt_error = render_to_string('uploads/strings/number.html', {'number': upload.total_txt_error}, request)
                    status = render_to_string('uploads/strings/status.html', {'status': upload.status}, request)

                    if upload.file:
                        url_descarga = reverse('download_upload', kwargs={'upload_id': upload.id})

                    options = render_to_string('uploads/strings/options.html', {'upload': upload, 'url_descarga': url_descarga}, request)

                    list_result.append([
                        upload_id,
                        user,
                        filename,
                        str(upload.period_date_from),
                        str(upload.period_date_to),
                        date.strftime("%Y-%m-%d %H:%M:%S"),
                        total_txts,
                        total_txt_good,
                        total_txt_error,
                        status,
                        options,
                    ])

                result['aaData'] = list_result
                result['iTotalRecords'] = total
                result['iTotalDisplayRecords'] = total

                return JsonResponse(result)
        except Exception as e:
            print(f'Exception in ListUploadsView post method => {str(e)}')

        return JsonResponse({})

     def get(self, request, *args, **kwargs):
         template = self.template_name
         context = {}
         return render(request, template, context)

     
     ##################### [ EXTRA CONTENT] ########################################
     
class ListPayrollsLastView(TemplateView):

    def post(self, request, *args, **kwargs):
        try:
            list_result = []
            total = 0

            if request.is_ajax():
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))
                list_invoices = PayRoll.objects.filter(rtaxpayer_id=kwargs['active_taxpayer_id'], status='S').order_by('-emission_date')[:10]
                total = list_invoices.count()
                list_invoices = list_invoices[start:start + length]

                for invoice in list_invoices.iterator():
                    list_result.append([
                        str(invoice.uuid).upper(),
                        invoice.serial,
                        invoice.folio,
                        invoice.total
                    ])
        except Exception as e:
            print(f'Exception in ListPayrollsLastView post method ==> {str(e)}')

        result = {
            'aaData': list_result,
            'iTotalRecords': total,
            'iTotalDisplayRecords': total,
        }
        return JsonResponse(result)
      
class ListInvoicesView(TemplateView):

    template_name = 'vouchers/status.html'

    def post(self, request, *args, **kwargs):
        try:
            if request.is_ajax():
                total = 0
                list_result = []
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))

                account = kwargs['account']
                active_taxpayer_id = kwargs['active_taxpayer_id']

                try:
                    list_invoices = PayRoll.objects.filter(kwargs['query'])
                    if request.user.profile.role == "E":
                        list_invoices = list_invoices.filter(status='S')
                    list_invoices = list_invoices.order_by('-id')

                    total = list_invoices.count()
                    list_invoices = list_invoices[start:start+length]
                    for invoice in list_invoices.iterator():
                        uuid = str(invoice.uuid).upper() if invoice.uuid else ''
                        options_dict = {'invoice': {
                            'status': invoice.status,
                            'confirmed': invoice.signed,
                            'txt': reverse('txt', kwargs={'payroll_id': invoice.id}),
                            'download': reverse('download', kwargs={'payroll_id': invoice.id}),
                        }}
                        if invoice.status == 'S':
                            options_dict['invoice']['pdf'] = reverse('pdf', kwargs={'uuid': uuid})
                            options_dict['invoice']['uuid'] = uuid
                            options_dict['invoice']['taxpayer_id'] = invoice.taxpayer_id

                        error = invoice.notes
                        options = render_to_string('invoices/options.html', options_dict, request)
                        invoice_status = render_to_string('invoices/invoice_status.html', {'status': invoice.status, 'notes': invoice.notes}, request)
                        emission_date = invoice.emission_date.strftime("%Y-%m-%d %H:%M:%S") if invoice.emission_date is not None else invoice.emission_date
                        paid_date_from = ""
                        paid_date_to = ""
                        try:
                            paid_date_from = invoice.details.last().paid_date_from.strftime("%Y-%m-%d")
                        except:
                            pass
                        try:
                            paid_date_to = invoice.details.last().paid_date_to.strftime("%Y-%m-%d")
                        except:
                            pass

                        list_result.append([
                            uuid,
                            invoice.folio,
                            emission_date,
                            invoice.rtaxpayer_id,
                            invoice.rname,
                            paid_date_from,
                            paid_date_to,
                            invoice.total,
                            invoice_status,
                            INVOICE_SIGNED[invoice.signed],
                            options
                        ])
                except Exception as e:
                    print(f'Exception in ListInvoicesView post method ==> {str(e)}')

                result = {
                    'aaData': list_result,
                    'iTotalRecords': total,
                    'iTotalDisplayRecords': total,
                }
                return JsonResponse(result)
        except Exception as e:
            print(f'Exception in ListInvoicesView post method ==> {str(e)}')

        return JsonResponse({})

    def get(self, request, *args, **kwargs):
        template = self.template_name
        return TemplateResponse(request, template)

class UploadView(TemplateView):

    template_name = 'views/main_views/uploads.html'

    def post(self, request, *args, **kwargs):
        try:
            success, message = False, 'Error al Cargar Archivo'

            if request.method == 'POST' and request.is_ajax() and request.FILES:
                user = request.user
                business_id = kwargs['account'].id
                zip_file = request.FILES.get('file_data')

                if zip_file.content_type in ('text/zip', 'application/zip'):
                    upload_obj = Upload.objects.create(
                        business_id=business_id,
                        user_id=user.id,
                        name=zip_file.name,
                        file=zip_file,
                        period_date_from=date.today(),
                        period_date_to=date.today()
                    )

                    if settings.ASYNC_PROCCESS:
                        task_upload = import_upload.apply_async((upload_obj.id,),)
                        upload_obj.refresh_from_db()
                        upload_obj.task_id = task_upload.id
                        upload_obj.task_status = task_upload.status
                        upload_obj.save()
                    else:
                        import_upload(upload_obj.id)

                    success, message = True, 'Archivo subido exitosamente'
                else:
                    message = 'El formato del archivo no es zip'
        except Exception as e:
            print(f'Exception in UploadView post method ==> {str(e)}')

        return JsonResponse({"success": success, "message": message})
      
class CancelView(View):

    def post(self, request, *args, **kwargs):
        result = {'success': False, 'message': u'Error al cancelar CFDI'}
        try:
            if request.method == 'POST' and request.is_ajax():
                uuid = request.POST.get('uuid')
                notes = request.POST.get('notes', '')
                taxpayer_id = request.POST.get('taxpayer_id')
                account = kwargs['account']
                motive = request.POST.get('motive', '')
                folio = request.POST.get('folio', '')

                try:
                    response, client = FINKOKWS.sign_cancel(uuid, taxpayer_id, motive, folio, business_obj=account)

                    if response and hasattr(response, 'Folios'):
                        status_uuid = response.Folios[0][0].EstatusUUID
                        status_cancel = unicode(response.Folios[0][0].EstatusCancelacion)

                        if status_uuid in ('201', '202'):
                            message = u'Nomina en proceso de cancelación'
                            try:
                                invoice = PayRoll.objects.get(uuid=uuid)
                                result_ = self._consult_invoice_status(invoice)
                                if result_.Estado == "Cancelado":
                                    message = u'Nomina Cancelada'
                                    invoice.notes = u'{} => {}'.format(message, notes)
                                    invoice.status = 'C'
                                    invoice.status_sat = 'C'
                                    invoice.save()
                                    print("UUID:{} Cancelado".format(invoice.uuid))
                                elif result_.Estado == "Vigente":
                                    message = u'La nomina aún se encuentra Vigente'
                                result['success'], result['message'] = True, message
                            except Exception as e:
                                print('Exception update cancellation status ==> {}'.format(str(e)))

                    elif response and hasattr(response, 'CodEstatus'):
                        result['message'] = unicode(response['CodEstatus'])

                except Exception as e:
                    print('Exption in WS sign_cancel ==> {}'.format(str(e)))

        except Exception as e:
            print('Exception in cancel CFDI ==> {}'.format(str(e)))

        return JsonResponse(result)

    def _consult_invoice_status(self, invoice):
        url = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?WSDL"
        client = suds_client(url, location=url, cache=None)
        return client.service.Consulta(invoice.get_satquery_str())
      
class DownloadView(TemplateView):

    def get(self, request, payroll_id, *args, **kwargs):
        try:
            user = request.user
            role = user.profile.role
            account = kwargs['account']
            query = Q(id=payroll_id)
            invoice = PayRoll.objects.get(query)
            inv_account = None

            if role == 'B':
                inv_account = invoice.business
            elif role == 'E':
                inv_account = invoice.employee

            if inv_account == account or user.profile.role in ('S', 'A', 'B', 'E'):
                filename = '%s.xml' % invoice.get_filename()
                response = HttpResponse(invoice.xml, content_type='application/xml text/xml')
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
            else:
                return HttpResponseForbidden()

        except PayRoll.DoesNotExist:
            raise Http404('Payroll does not exist.')

        except Exception as e:
            print('Error al descargar XML ==> %s' % str(e))
            raise Http404
  
class DeleteView(TemplateView):

    def post(self, request, *args, **kwargs):
        try:
            uuid = request.POST.get('uuid')
            query = Q(uuid=uuid)
            invoice = PayRoll.objects.get(query)
            path = invoice._xml.path
            os.remove(path)
            invoice.delete()
        except PayRoll.DoesNotExist:
            pass  # Handle the case where the PayRoll doesn't exist, if needed
        except Exception as e:
            print('Error Al intentar borrar el registro %s' % str(e))

        return HttpResponseRedirect(reverse('list_invoices'))
      
class PDFView(TemplateView):

    def get(self, request, uuid, *args, **kwargs):
        try:
            user = request.user
            role = user.profile.role
            account = kwargs['account']
            query = Q(uuid=uuid)
            invoice = PayRoll.objects.get(query)
            inv_account = ''
            business_number = invoice.details.first().business_number

            if role == 'B':
                inv_account = invoice.business
            elif role == 'E':
                inv_account = invoice.employee

            if inv_account == account or user.profile.role in ('S', 'B', 'E', 'A'):
                filename = '%s.xml' % invoice.uuid
                XML_PATH = invoice._xml.path
                PDF_PATH = '/tmp/'

                result_pdf = CreatePDF(xml_path=XML_PATH, filename=filename, business_number=business_number)

                if result_pdf.success:
                    pdf_file = open('%s%s.pdf' % (PDF_PATH, uuid))
                    pdf_read = pdf_file.read()
                    response = HttpResponse(pdf_read, content_type='application/pdf text/pdf')
                    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % invoice.get_filename()
                    os.remove('%s/%s.pdf' % (PDF_PATH, uuid))
                    return response
                else:
                    print(u"Creacion de PDF: ERROR")
            else:
                return HttpResponseForbidden()

        except PayRoll.DoesNotExist:
            raise Http404('Payroll does not exist.')

        except Exception as e:
            print('Error al descargar PDF ==> %s' % str(e))
            raise Http404

@method_decorator(login_required(login_url='user:login'), name='dispatch')
class TxtView(TemplateView):

    def get(self, request, payroll_id, *args, **kwargs):
        try:
            invoice = PayRoll.objects.get(id=payroll_id)
            filename = '%s.txt' % invoice.get_filename()
            response = HttpResponse(invoice.txt, content_type='application/txt text/txt')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        except PayRoll.DoesNotExist:
            raise Http404('Payroll does not exist.')
        except Exception as e:
            print('Error al descargar XML ==> %s' % str(e))
            raise Http404

@method_decorator(login_required(login_url='user:login'), name='dispatch')
class SendEmailView(TemplateView):

    def post(self, request, *args, **kwargs):
        success = False
        message = ''
        
        if request.user.profile.role == 'E':
            business_obj = kwargs['account'].business
        else:
            business_obj = kwargs['account']

        try:
            list_email = request.POST.get('mail')[:-1].split(',')
            uuid = request.POST.get('uuid')
            query = Q(uuid=uuid)
            invoice = PayRoll.objects.get(query)
            XML_PATH = invoice._xml.path
            PDF_PATH = '/tmp'
            filename = '%s.xml' % invoice.uuid

            try:
                business_number = invoice.details.first().business_number
                result_pdf = CreatePDF(xml_path=XML_PATH, filename=invoice.filename, business_number=business_number)
                if result_pdf.success:
                    print("Creación de PDF: OK")
            except Exception as e:
                print("Exception %s" % str(e))

            uuid = invoice.uuid
            name_receiver = invoice.rname
            name_issuer = invoice.name
            taxpayer_receiver = invoice.rtaxpayer_id
            taxpayer_issuer = invoice.taxpayer_id
            date = invoice.emission_date
            data_receiver = str(date)
            date_final = (data_receiver[:10])
            filenamepdf = '%s/%s' % (PDF_PATH, invoice.filename.replace('txt', 'pdf'))
            xml = invoice._xml.path
            pdf = open(filenamepdf)

            subject = u'Envio de Comprobante Fiscal de Nómina'
            from_email = settings.DEFAULT_FROM_EMAIL

            extra_dic = {'receiver_name': name_receiver, 'emision_date': date_final, 'uuid': uuid,
                         'issuces_name': name_issuer, 'taxpayer_id': taxpayer_issuer, 'rtaxpayer_id': taxpayer_receiver}
            html_content = render_to_string('invoices/send_cfdi.html', extra_dic, request)

            if subject and from_email and html_content and list_email and xml and pdf:
                try:
                    msg = EmailMessage(subject, html_content, from_email, list_email)
                    msg.content_subtype = "html"

                    if business_obj.send_mail_encryption:
                        zip_path = '{}{}'.format(settings.PATH_REPORTS_TMP, invoice.filename.replace('txt', 'zip'))
                        pyminizip.compress_multiple([xml, filenamepdf], ['', ''], zip_path, business_obj.password, 5)
                        msg.attach_file(zip_path)
                        msg.send()
                        os.remove(zip_path)
                    else:
                        msg.attach_file(xml)
                        msg.attach_file(filenamepdf)
                        msg.send()
                        os.remove(filenamepdf)

                    message = 'Correo Enviado satisfactoriamente'
                    success = True

                except Exception as e:
                    print('Error al enviar correo ==> %s' % str(e))
                    message = 'Error al enviar correo'

            else:
                print('Error al enviar correo')
                message = 'Error al enviar correo'

        except PayRoll.DoesNotExist:
            message = 'El comprobante fiscal de nómina no existe.'
        except Exception as e:
            print('Error al enviar correo ==> %s' % str(e))
            message = 'Error al enviar correo'

        result = {'success': success, 'message': message}
        print(result)
        return JsonResponse(result)
      
class HistoryView(TemplateView):

    def post(self, request, query, *args, **kwargs):
        try:
            if request.is_ajax():
                total = 0
                list_result = []
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))
                account = kwargs['account']
                active_taxpayer_id = kwargs['active_taxpayer_id']

                try:
                    list_history = History.objects.filter(query).order_by('-date')

                    if request.user.role in ('B', 'S', 'A'):
                        list_history = list_history.filter(business__taxpayer_id=active_taxpayer_id)
                    elif request.user.role == 'E':
                        list_history = list_history.filter(employee=account)

                    total = list_history.count()
                    list_history = list_history[start:start+length]

                    for history in list_history.iterator():
                        options_dict = {'details': {'detail': reverse('details_history', kwargs={'id_history': history.id})}}
                        options = render_to_string('history/options.html', options_dict, request)
                        user = '<span class="label label-emails" title="">{}</span>'.format(history.business.email[0])

                        list_result.append([
                            user,
                            history.business.taxpayer_id,
                            history.date.strftime("%Y-%m-%d %H:%M:%S"),
                            history.totales_files,
                            history.successful_files,
                            history.failed_files,
                            options
                        ])
                except Exception as e:
                    print('Exception in list_invoices_1 ==> {}'.format(str(e)))

                result = {
                    'aaData': list_result,
                    'iTotalRecords': total,
                    'iTotalDisplayRecords': total,
                }
                return JsonResponse(result)

        except Exception as e:
            print(str(e))

    def get(self, request, *args, **kwargs):
        template = 'history/history.html'
        return TemplateResponse(request, template)
      
class DetailsHistoryView(TemplateView):

    def post(self, request, id_history, *args, **kwargs):
        try:
            if request.is_ajax():
                user = request.user
                total = 0
                list_result = []
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))

                try:
                    query = Q(history_id=id_history)
                    list_history = DetailsHistory.objects.filter(query).order_by('status')

                    if list_history and (list_history[0].history.business == kwargs['account'] or user.role in ['S', 'A']):
                        total = list_history.count()
                        list_history = list_history[start:start+length]

                        for history in list_history.iterator():
                            list_result.append([
                                history.name,
                                history.uuid,
                                DETAILS_STATUS_HISTORY.get(history.status, ''),
                                history.notes
                            ])
                except Exception as e:
                    print('Exception in POST details_history ==> {}'.format(str(e)))

                result = {
                    'aaData': list_result,
                    'iTotalRecords': total,
                    'iTotalDisplayRecords': total,
                }
                return JsonResponse(result)

        except Exception as e:
            print('Exception in details_history ==> {}'.format(str(e)))

    def get(self, request, *args, **kwargs):
        template = 'history/details.html'
        return TemplateResponse(request, template)
      
from django.core.cache import cache
class NotificationView(TemplateView):

    @login_required(login_url='user:login')
    def get(self, request, *args, **kwargs):
        try:
            base_path = request.GET.get('base_path')

            new_notification = False
            notification_response = {}
            now = datetime.now() - relativedelta(days=30) if settings.DEBUG else datetime.now() - relativedelta(hours=1)

            notification_cache = cache.get('%s-notifications' % (request.user.id))
            base_path_cache = cache.get('%s-base_path' % (request.user.id))
            notifications = Notifications.objects.filter(account=request.user.account, status='N', date__gte=now).order_by('date')
            notification_count = notifications.count()
            notifications = notifications[:10]

            notification_response = {
                'notifications': [{'title': notification.title, 'date': notification.date} for notification in notifications]
            }

            if self.ordered(notification_response) != self.ordered(notification_cache) or base_path != base_path_cache:
                cache.set('%s-notifications' % (request.user.id), notification_response)
                cache.set('%s-base_path' % (request.user.id), base_path)
                new_notification = True

            notification_response.update({'new': new_notification, 'notification-count': notification_count})

        except Exception as e:
            print(str(e))

        return JsonResponse(notification_response)

    def ordered(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj
          
          
class ProfileView(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            country = ''
            state = ''
            municipality = ''
            locality = ''
            street = ''
            external_number = ''
            phone = ''
            logo = '/static/img/avatar.png'
            
            account = kwargs['account']
            taxpayer_id = ''
            person_type = ''

            try:
                taxpayer_id = account.taxpayer_id
                if taxpayer_id:
                    if len(taxpayer_id) == 12:
                        person_type = 'Moral'
                    elif len(taxpayer_id) == 13:
                        person_type = 'Fisica'
            except Exception as e:
                print('Exception in profile get taxpayer_id ==> {}'.format(str(e)))

            if account.address is not None:
                country = account.address.country if account.address.country else ''
                state = account.address.state if account.address.state else ''
                municipality = account.address.municipality if account.address.municipality else ''
                locality = account.address.locality if account.address.locality else ''
                street = account.address.street if account.address.street else ''
                external_number = account.address.external_number if account.address.external_number else ''
                phone = account.address.phone if account.address.phone else ''

            if request.user.role == 'B':
                logo = account.logo

            context_data = {
                'person_type': person_type,
                'name': account.name,
                'taxpayer_id': taxpayer_id,
                'country': country,
                'state': state,
                'municipality': municipality,
                'locality': locality,
                'street': street,
                'external_number': external_number,
                'phone': phone,
                'logo': logo,
            }

            return TemplateResponse(request, 'profile/info.html', context_data)

        except Exception as e:
            print('Exception in profile ==> {}'.format(str(e)))


class EditInformationView(TemplateView):

    def post(self, request, *args, **kwargs):
        try:
            result = {'success': False, 'message': u'Error al editar la información'}
            option = request.POST.get('option')
            account = kwargs['account']

            if option == 'Account':
                self.save_account_info(request, account, result)

            elif option == 'Address':
                self.save_address_info(request, account, result)

            elif option == 'Fiscal':
                self.save_fiscal_info(request, account, result)

        except Exception as e:
            print('Exception in EDIT_INFORMATION ==> {}'.format(str(e)))

        print(result)
        return JsonResponse(result)

    def save_account_info(self, request, account, result):
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            second_last_name = request.POST.get('second_last_name')
            logo = request.FILES.get('logo')

            account.name = first_name
            account.logo = logo
            account.save()
            result['success'], result['message'] = True, u'Datos actualizados exitosamente'

        except Exception as e:
            print('Exception in SAVE ACCOUNT ==> {}'.format(str(e)))

    def save_address_info(self, request, account, result):
        try:
            country = request.POST.get('country')
            state = request.POST.get('state')
            municipality = request.POST.get('municipality')
            locality = request.POST.get('locality')
            street = request.POST.get('street')
            external_number = request.POST.get('external_number')
            phone = request.POST.get('phone')

            if account.address is None:
                address = Address.objects.create(
                    country=country,
                    state=state,
                    municipality=municipality,
                    locality=locality,
                    street=street,
                    external_number=external_number,
                    phone=phone
                )
                account.address = address
                account.save()
            else:
                address = account.address
                address.country = country
                address.state = state
                address.municipality = municipality
                address.locality = locality
                address.street = street
                address.external_number = external_number
                address.phone = phone
                address.save()

            result['success'], result['message'] = True, u'Datos actualizados exitosamente'

        except Exception as e:
            print('Exception in SAVE ADDRESS ==> {}'.format(str(e)))

    def save_fiscal_info(self, request, account, result, **kwargs):
        try:
            if request.FILES:
                taxpayer_id = kwargs['active_taxpayer_id']
                taxpayer_id = kwargs['account']
                private_key = request.FILES.get('key')
                public_cer = request.FILES.get('cer')
                pwd_key = request.POST.get('csd_password')
                finkok_account = request.POST.get('fk_username')
                finkok_password = request.POST.get('fk_password')

                tmp_private_key = tempfile.NamedTemporaryFile(delete=False)
                tmp_private_key.write(private_key.read())
                tmp_private_key.close()

                tmp_pem_key = tempfile.NamedTemporaryFile(delete=False)
                tmp_pem_key.close()
                command_key = 'openssl pkcs8 -inform DER -in %s -out %s -passin pass:\'%s\'' % (
                tmp_private_key.name, tmp_pem_key.name, pwd_key)
                is_valid_key = os.system(command_key)

                if is_valid_key != 0:
                    raise Exception('Error')

                tmp_public_cer = tempfile.NamedTemporaryFile(delete=False)
                tmp_public_cer.write(public_cer.read())
                tmp_public_cer.close()

                tmp_pem_cer = tempfile.NamedTemporaryFile(delete=False)
                tmp_pem_cer.close()
                command_cer = 'openssl x509 -inform DER -in %s -pubkey -out %s' % (
                tmp_public_cer.name, tmp_pem_cer.name)
                is_valid_cer = os.system(command_cer)

                if is_valid_cer != 0:
                    raise Exception('Error')

                cert = X509.load_cert(tmp_pem_cer.name)
                evp = EVP.load_key(tmp_pem_key.name)
                serial = hex(cert.get_serial_number())[3:-1:2]
                subject = cert.get_subject().__str__()

                certificate_type = 'C' if "OU" in subject else 'F'
                expiration_date = cert.get_not_after().get_datetime().replace(tzinfo=None)
                expedition_date = cert.get_not_before().get_datetime().replace(tzinfo=None)

                if certificate_type == 'C':
                    account.finkok_account = finkok_account
                    account.finkok_password = finkok_password

                    sat_file_obj, created = SatFile.objects.get_or_create(business_id=account.id,
                                                                          serial_number=serial)
                    sat_file_obj.cer_file = public_cer
                    sat_file_obj.key_file = private_key
                    sat_file_obj.passphrase = pwd_key
                    sat_file_obj.default = True
                    account.save()
                    sat_file_obj.save()

                    result['success'], result['message'] = True, u'Datos actualizados exitosamente'
                else:
                    result['message'] = u'Los archivos son de tipo FIEL'

        except Exception as e:
            print('Exception in SAVE FISCAL ==> {}'.format(str(e)))


class StuffsView(TemplateView):

    def post(self, request, *args, **kwargs):
        context = {}
        oper = request.POST.get('oper')

        if request.is_ajax():
            if oper == 'set-business':
                self.set_business(request, context)

        return JsonResponse(context)

    def set_business(self, request, context):
        try:
            business_id = request.POST.get('business')
            role = request.user.profile.role

            if role in ('A', 'S', 'B'):
                business = Business.objects.get(id=business_id)
            else:
                business = Employee.objects.get(id=business_id)

            request.session['business_id'] = business.id
            request.session['active_taxpayer_id'] = business.taxpayer_id
            context['success'] = True

        except Exception as e:
            print('Exception on core stuffs view {}'.format(str(e)))
            context['success'] = False
            context['message'] = 'No existe el negocio o no cuentas con suficientes permisos.'
            
class SignPayrollView(TemplateView):

    def post(self, request, *args, **kwargs):
        success, message = False, u'Error al firmar nomina'
        try:
            if request.method == 'POST' and request.is_ajax():
                uuid = request.POST.get('uuid')
                payroll = PayRoll.objects.get(uuid=uuid)
                if not payroll.signed:
                    img_base64 = request.POST.get('img_base64').replace('data:image/png;base64,','')
                    img_base64 = base64.b64decode(img_base64)
                    filename = '/tmp/%s.png' % uuid
                    with open(filename, 'wb') as f:
                        f.write(img_base64)
                    img = open(filename,'r')
                    img = File(img)
                    payroll.sign = img
                    payroll.signed = True
                    payroll.save()
                    success, message = True, u'Nómina firmada exitosamente'
                else:
                    message = u'Nómina previamente firmada'
        except Exception as e:
            print('Exception in SignPayrollView => %s' % (str(e)))
        result = {'success': success, 'message': message}
        return JsonResponse(result)

class GetCodeView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        if request.method == 'GET':
            oper = request.GET.get('oper')
            if oper == 'obtener':
                try:
                    uuid = request.GET.get('uuid')
                    _id = os.urandom(20).encode('base64').strip()
                    cache.set(_id, uuid, 600)
                    path = reverse('secure', kwargs={'base64string': _id})
                    absolute_uri = request.build_absolute_uri(path)
                    image_path, static_path = self.get_image(absolute_uri, _id)
                    print(_id, uuid, request.build_absolute_uri(path), image_path, static_path)
                    context.update({
                        "success": True,
                        "message": "Secure URL has been generated successfully.",
                        _id: absolute_uri,
                        "qrimage": static_path
                    })
                except Exception as e:
                    print('Exception', str(e))
                    context.update({
                        "success": False,
                        "message": "Something wrong was ocurrs.",
                    })
                return JsonResponse(context)

    def get_image(self, absolute_uri, _id):
        print(absolute_uri)
        img = qrcode.make(absolute_uri)
        filename = '{}.png'.format(_id.replace('/', ''))
        image_path = os.path.join(settings.TEMPORARY_QR, filename)
        img.save(image_path)
        return image_path, settings.STATIC_URL('temporary/'+filename)

@method_decorator(login_required(login_url='user:login'), name='dispatch')
class TokenAddView(View):
    template_name = 'dashboard.html'

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        user = request.user

        try:
            user_tokens = TokensUser.objects.filter(user=user, token=token)

            if user_tokens.exists():
                # Token already exists for the user
                return TemplateResponse(request, self.template_name)
            else:
                # Token does not exist, create a new one
                TokensUser.objects.create(token=token, user=user)

        except Exception as e:
            print('Exception in TokenAddView => %s ' % e)

        return TemplateResponse(request, self.template_name)
      
@method_decorator(login_required, name='dispatch')
class ListNewsView(TemplateView):
    template_name = 'notifications/notifications.html'

    def get(self, request, *args, **kwargs):
        active_account = kwargs.get('account', None)
        active_taxpayer_id = kwargs.get('active_taxpayer_id', None)

        if 'read' in request.path:
            return self.handle_read_request(active_account, active_taxpayer_id)
        elif bool(re.findall(r"[0-9]+", request.path)):
            return self.handle_single_news_request(request)

        return TemplateResponse(request, self.template_name)

    def handle_read_request(self, active_account, active_taxpayer_id):
        user = self.request.user

        if user.profile.role in ('B', 'E'):
            account = self.get_account(user.profile.role, user, active_account, active_taxpayer_id)
            if account:
                news = self.get_news_for_account(user.profile.role, account)
            else:
                news = News.objects.filter(business=None, employee=None)

            news.update(read=True)

        return TemplateResponse(self.request, self.template_name)

    def handle_single_news_request(self, request):
        new_id = re.findall(r"[0-9]+", request.path)[0]
        new = get_object_or_404(News, id=new_id)
        new.read = True
        new.save()

        return TemplateResponse(request, self.template_name)

    def get_account(self, role, user, active_account, active_taxpayer_id):
        if active_account:
            account = active_account
        else:
            try:
                if role == 'B':
                    account = Business.objects.get(user=user, taxpayer_id=active_taxpayer_id)
                elif role == 'E':
                    account = Employee.objects.get(user=user, taxpayer_id=active_taxpayer_id)
            except Exception as e:
                print('Exception in ListNewsView => %s' % e)
                return None
        return account

    def get_news_for_account(self, role, account):
        if role == 'B':
            return News.objects.filter(business=account)
        elif role == 'E':
            return News.objects.filter(employee=account)
          
class SignView(TemplateView):
    template_name = 'vouchers/sing.html'

    def get(self, request, *args, **kwargs):
        try:
            success, uuid = False, ''
            _idb64 = kwargs.get('base64string', None)

            if _idb64 is None:
                try:
                    filename = '{}.png'.format(_idb64.replace('/', ''))
                    image_path = os.path.join(settings.TEMPORARY_QR, filename)
                    os.remove(image_path)
                except:
                    pass
                raise Http404
            else:
                uuid = cache.get(_idb64)
                print(uuid)
                filename = '{}.png'.format(_idb64.replace('/', ''))
                image_path = os.path.join(settings.TEMPORARY_QR, filename)
                cache.delete(_idb64)
                os.remove(image_path)
                success = True
                payroll = PayRoll.objects.get(uuid=uuid)
                date = payroll.details.first().paid_date
                total_per = '$ %s' % payroll.total_per
                total_ded = '$ %s' % payroll.total_ded
                total = '$ %s' % payroll.total
                total_oth = '$ %s' % payroll.total_oth

            context = {
                'success': success,
                'uuid': uuid,
                'date': date,
                'total_per': total_per,
                'total_ded': total_ded,
                'total': total,
                'total_oth': total_oth
            }

            return render(request, self.template_name, context)

        except Exception as e:
            print('Exception in SignView ==> %s' % (str(e)))
            raise Http404
          

class ListUploadsView(TemplateView):
    template_name = 'uploads/uploads.html'

    def post(self, request, query, *args, **kwargs):
        if request.is_ajax():
            return self.handle_ajax_post(request, query, **kwargs)
        else:
            return render(request, self.template_name, {})

    def handle_ajax_post(self, request, query, **kwargs):
        result = {'aaData': [], 'iTotalRecords': 0, 'iTotalDisplayRecords': 0}
        try:
            business = kwargs['account']
            total = 0
            list_result = []
            start = int(request.POST.get('iDisplayStart'))
            length = int(request.POST.get('iDisplayLength'))
            uploads_obj = Upload.objects.filter(business_id=business.id).filter(query).order_by('-id')
            total = uploads_obj.count()
            uploads = uploads_obj[start:start + length]

            for upload in uploads:
                url_descarga = None
                upload_id = render_to_string('uploads/strings/number.html', {'number': upload.task_id}, request)
                user = render_to_string('uploads/strings/user.html', {'user': upload.user}, request)
                filename = upload.name
                date = upload.created
                total_txts = render_to_string('uploads/strings/number.html', {'number': upload.total_txt}, request)
                total_txt_good = render_to_string('uploads/strings/number.html', {'number': upload.total_txt_good},
                                                  request)
                total_txt_error = render_to_string('uploads/strings/number.html', {'number': upload.total_txt_error},
                                                   request)
                status = render_to_string('uploads/strings/status.html', {'status': upload.status}, request)

                if upload.file:
                    url_descarga = reverse('download_upload', kwargs={'upload_id': upload.id})

                options = render_to_string('uploads/strings/options.html', {'upload': upload, 'url_descarga': url_descarga},
                                           request)

                list_result.append([
                    upload_id,
                    user,
                    filename,
                    str(upload.period_date_from),
                    str(upload.period_date_to),
                    date.strftime("%Y-%m-%d %H:%M:%S"),
                    total_txts,
                    total_txt_good,
                    total_txt_error,
                    status,
                    options,
                ])

            result['aaData'] = list_result
            result['iTotalRecords'] = total
            result['iTotalDisplayRecords'] = total

        except Exception as e:
            print('Exception in ListUploadsView => {}'.format(str(e)))

        return JsonResponse(result)

class ListZipsView(View):
    template_name = 'zips/zips.html'

    def post(self, request, query, *args, **kwargs):
        if request.is_ajax():
            return self.handle_ajax_post(request, query, **kwargs)
        else:
            return render(request, self.template_name, {})

    def handle_ajax_post(self, request, query, **kwargs):
        result = {'aaData': [], 'iTotalRecords': 0, 'iTotalDisplayRecords': 0}
        try:
            business = kwargs['account']
            total = 0
            list_result = []
            start = int(request.POST.get('iDisplayStart'))
            length = int(request.POST.get('iDisplayLength'))
            zip_obj = Zip.objects.filter(business_id=business.id).filter(query).order_by('-id')
            total = zip_obj.count()
            zips = zip_obj[start:start + length]

            for zip_ in zips:
                url_descarga = None
                zip_id = render_to_string('zips/strings/number.html', {'number': zip_.id}, request)
                upload_id = render_to_string('zips/strings/number.html', {'number': zip_.upload_id}, request)
                filename = zip_.name
                date = zip_.date_created
                total_zips = render_to_string('zips/strings/number.html', {'number': zip_.total_zip}, request)
                total_txts = render_to_string('zips/strings/number.html', {'number': zip_.total_txt}, request)
                status = render_to_string('zips/strings/status.html', {'status': zip_.task_status}, request)

                if zip_.file:
                    url_descarga = reverse('download_zip', kwargs={'zip_id': zip_.id})

                options = render_to_string('zips/strings/options.html', {'zip': zip_, 'url_descarga': url_descarga},
                                           request)

                list_result.append([
                    zip_id,
                    upload_id,
                    filename,
                    date.strftime("%Y-%m-%d %H:%M:%S"),
                    total_zips,
                    total_txts,
                    status,
                    options,
                ])

            result['aaData'] = list_result
            result['iTotalRecords'] = total
            result['iTotalDisplayRecords'] = total

        except Exception as e:
            print('Exception in ListZipsView => {}'.format(str(e)))

        return JsonResponse(result)
      

@method_decorator(login_required(login_url='user:login'), name='dispatch')
@method_decorator(require_http_methods(["GET"]), name='get')
class DownloadZipView(View):
    def get(self, request, zip_id, *args, **kwargs):
        try:
            zip_obj = Zip.objects.get(id=zip_id)
            zip_string = zip_obj.file.read()
            try:
                zip_string = zip_string.encode('utf-8')
            except:
                pass
            response = HttpResponse(zip_string, content_type='application/zip text/zip')
            response['Content-Disposition'] = 'attachment; filename=%s' % zip_obj.name
            return response
        except Exception as e:
            print('Error al descargar zip ==> %s' % str(e))
            raise Http404
          
class UploadOptionsView(View):
    template_name = 'your_template_name.html'

    def post(self, request, *args, **kwargs):
        response = {"success": False, "message": u"Error, contacte a soporte Técnico"}

        try:
            if request.is_ajax():
                business_obj = kwargs['account']
                oper = request.POST.get('oper', None)
                upload_id = int(request.POST.get('object_id'))
                upload_filter = Upload.objects.filter(id=upload_id, business_id=business_obj.id)

                if upload_filter.exists():
                    upload_obj = upload_filter.first()

                    if oper == "consult":
                        payroll_filter = PayRoll.objects.filter(upload_id=upload_id)
                        payroll_filter_pending = payroll_filter.filter(status='P')

                        if payroll_filter_pending.count() > 0:
                            response['message'] = "ZIP en proceso"

                        status_result = payroll_filter.values('status').annotate(total=Count('status')).order_by()

                        for status_total in status_result:
                            total = status_total['total']
                            if status_total['status'] == 'S':
                                upload_obj.total_txt_good = total
                                upload_obj.save()
                            elif status_total['status'] == 'E':
                                upload_obj.total_txt_error = total
                                upload_obj.save()

                        upload_obj.status = 2
                        upload_obj.task_status = 'SUCCESS'
                        upload_obj.save()

                        upload_obj.send_report_mail()

                        for payroll_obj in payroll_filter.filter(status='S'):
                            if settings.ASYNC_PROCCESS:
                                send_mail_payroll.apply_async((payroll_obj.id,))
                            else:
                                payroll_obj.send_mail()

                        response['success'] = True

                    elif oper == "proccess":
                        if settings.ASYNC_PROCCESS:
                            task_upload = import_upload.apply_async((upload_obj.id,),)
                            upload_obj.refresh_from_db()
                            upload_obj.task_id = task_upload.id
                            upload_obj.task_status = task_upload.status
                            upload_obj.save()
                            response['message'] = u"Se inicio el procesamiento de la carga seleccionada de forma exitosa."
                        else:
                            import_upload(upload_obj.id)
                            response['message'] = u"El procesamiento de la carga seleccionada finalizo de forma exitosa."
                        response['success'] = True

                    else:
                        response['message'] = u"Opción invalida"

                else:
                    response['message'] = u"El registro de carga no existe"

        except Exception as e:
            print('Exception in UploadOptionsView => {}'.format(str(e)))

        return JsonResponse(response)
      

class GenerateReportView(View):

    def post(self, request, query, *args, **kwargs):
        success = False
        message = "Error no controlado, favor de comunicarse a soporte técnico"

        try:
            if request.is_ajax():
                business_obj = kwargs['account']

                ids = list(PayRoll.objects.filter(query).filter(status__in=['S', 'C']).order_by('-id')
                           .values_list('details', flat=True))

                if request.user.role == "E":
                    tasks = generate_report_payrolls_employee.apply_async((business_obj.id, ids),)
                else:
                    tasks = generate_report_payrolls.apply_async((business_obj.id, ids),)
                message = "El reporte se comenzó a generar, una vez que este listo se enviara por email a: {}".format(
                    ', '.join(business_obj.email))
                success = True
            else:
                message = "Petición invalida"

        except Exception as e:
            print('Exception in GenerateReportView => {}'.format(str(e)))

        response = {"success": success, "message": message}
        return JsonResponse(response)


class DownloadPayrollsMasiveView(View):

    def post(self, request, query, *args, **kwargs):
        success = False
        message = "Error no controlado, favor de comunicarse a soporte técnico"

        try:
            if request.is_ajax():
                business_obj = kwargs['account']
                role = kwargs['role']

                xml = json.loads(request.POST.get('xml', 'false'))
                pdf = json.loads(request.POST.get('pdf', 'false'))
                is_employee = json.loads(request.POST.get('empleado', 'false'))
                split_path = json.loads(request.POST.get('split_path', 'false'))

                if is_employee:
                    if xml or pdf:
                        payrolls_filter = PayRoll.objects.filter(query).filter(status__in=['S', 'C'])
                        for payroll_obj in payrolls_filter:
                            send_mail_payroll.apply_async((payroll_obj.id, ))
                        message = "Nóminas enviadas"
                        success = True
                    else:
                        message = "Debes de seleccionar por lo menos un tipo de archivo."
                else:
                    if xml or pdf:
                        ids = list(PayRoll.objects.filter(query).filter(status__in=['S', 'C']).order_by('-id')
                                   .values_list('id', flat=True))

                        payroll_report_obj = PayrollReport.objects.create(
                            xml=xml,
                            pdf=pdf,
                            invoices_ids=ids,
                        )
                        if role == "E":
                            payroll_report_obj.employee = business_obj
                        else:
                            payroll_report_obj.business = business_obj

                        payroll_report_obj.save()

                        tasks_id = payroll_report_obj.create_payroll_zip(split_path)

                        message = "El reporte se comenzó a generar, una vez que este listo se enviara por email a: {}".format(
                            ', '.join(business_obj.email))
                        success = True
                    else:
                        message = "Debes de seleccionar por lo menos un tipo de archivo."
            else:
                message = "Petición invalida"

        except Exception as e:
            print('Exception in DownloadPayrollsMasiveView => {}'.format(str(e)))

        response = {"success": success, "message": message}
        return JsonResponse(response)
      

class BusinessLogoOptionsView(View):

    def post(self, request, *args, **kwargs):
        success = False
        message = "Error no controlado, intenta más tarde!"

        try:
            if request.is_ajax():
                option = request.POST.get('option', '')
                business_id = request.POST.get('business_id', False)

                if not business_id:
                    raise Exception("Negocio no encontrado")

                business_obj = Business.objects.get(id=business_id)

                if option == "get_logo":
                    message = business_obj.get_logo()
                    success = True

                elif option == "update_logo":
                    logo = request.FILES.get('logo')
                    business_obj.logo = logo
                    business_obj.save()
                    message = {
                        "message": u"Actualización exitosa",
                        "logo": business_obj.get_logo(),
                    }
                    success = True

                else:
                    message = u"Opción inválida"

            else:
                message = u"Petición inválida"

        except Exception as e:
            print("Exception in BusinessLogoOptionsView => {}".format(str(e)))

        response = {"success": success, "message": message}
        return JsonResponse(response)
      
class DownloadZipPayrollTemplateView(View):

    def get(self, request, secrete_key=None, *args, **kwargs):
        try:
            if not secrete_key:
                return HttpResponseForbidden()

            report_id = signing.loads(secrete_key)

            payroll_report_filter = PayrollReport.objects.filter(id=report_id)
            if not payroll_report_filter.exists():
                return HttpResponseNotFound()

            payroll_report_obj = payroll_report_filter[0]

            extra_content = {"payroll_report_obj": payroll_report_obj}
            return TemplateResponse(request, 'zips/download_zip.html', extra_content)

        except Exception as e:
            print("Exception in DownloadZipPayrollTemplateView => {}".format(str(e)))
            print("secrete_key => {}".format(secrete_key))
            return HttpResponseForbidden()

class DownloadZipPayrollCheckPasswordView(View):

    def post(self, request, *args, **kwargs):
        success, message = False, u"Contraseña Inválida"

        try:
            if request.is_ajax():
                report_id_encrypted = request.POST.get("report_id")

                if report_id_encrypted:
                    password = request.POST.get("password", '')

                    if password:
                        report_id = signing.loads(report_id_encrypted)
                        payroll_report_filter = PayrollReport.objects.filter(id=report_id)

                        if payroll_report_filter.exists():
                            payroll_report_obj = payroll_report_filter.first()

                            if payroll_report_obj.get_decrypted_password() == password.strip():
                                message = reverse('download_zip_payroll', kwargs={"secrete_key": report_id_encrypted})
                                success = True

        except Exception as e:
            print("Exception in DownloadZipPayrollCheckPasswordView => {}".format(str(e)))

        return JsonResponse({"success": success, "message": message})

class DownloadZipPayrollView(TemplateView):

    def get(self, request, secrete_key, *args, **kwargs):
        try:
            report_id = signing.loads(secrete_key)
            payroll_report_filter = PayrollReport.objects.filter(id=report_id)

            if payroll_report_filter.exists():
                payroll_report_obj = payroll_report_filter.first()
                zip_string = payroll_report_obj.file.read()
                
                try:
                    zip_string = zip_string.encode('utf-8')
                except:
                    pass

                response = HttpResponse(zip_string, content_type='application/zip text/zip')
                response['Content-Disposition'] = 'attachment; filename=%s' % payroll_report_obj.get_file_name()
                return response

            else:
                return HttpResponseNotFound()

        except Exception as e:
            print("Exception in DownloadZipPayrollView => {}".format(str(e)))
            return HttpResponseForbidden()


class DownloadZipPayrollTemplateView(TemplateView):

    def get(self, request, secrete_key=None, *args, **kwargs):
        try:
            if not secrete_key:
                return HttpResponseForbidden()

            report_id = signing.loads(secrete_key)

            payroll_report_filter = PayrollReport.objects.filter(id=report_id)
            if not payroll_report_filter.exists():
                return HttpResponseNotFound()

            payroll_report_obj = payroll_report_filter[0]

            extra_content = {"payroll_report_obj": payroll_report_obj}
            return TemplateResponse(request, 'zips/download_zip.html', extra_content)

        except Exception as e:
            print("Exception in DownloadZipPayrollTemplateView => {}".format(str(e)))
            print("secrete_key => {}".format(secrete_key))
            return HttpResponseForbidden()
          
class UpdateBusinessView(View):

    def post(self, request, *args, **kwargs):
        success = False
        message = 'Error'

        try:
            if request.is_ajax() and request.method == 'POST':
                option = request.POST.get('option')

                if option in ('get_info_business', 'edit_info_business'):
                    taxpayer_id = request.POST.get("taxpayer_id")
                    business_id = int(request.POST.get("business_id"))

                    business_filter = Business.objects.filter(id=business_id, taxpayer_id=taxpayer_id)
                    if business_filter.exists():
                        business_obj = business_filter.first()

                        if option == "get_info_business":
                            message = {
                                "name": business_obj.name,
                                "taxpayer_id": business_obj.taxpayer_id,
                                "emails": ','.join(business_obj.email),
                                "estado": business_obj.address.state,
                                "municipio": business_obj.address.municipality,
                                "localidad": business_obj.address.locality,
                                "cp": business_obj.address.zipcode,
                                "calle": business_obj.address.street,
                                "number_ext": business_obj.address.external_number,
                                "number_int": business_obj.address.internal_number,
                            }
                            success = True
                        elif option == "edit_info_business":
                            logo = request.FILES.get("logo")
                            name = request.POST.get("name")
                            emails = request.POST.get("emails")[:-1].split(',')

                            state = request.POST.get("state")
                            municipality = request.POST.get("municipality")
                            locality = request.POST.get("locality")
                            zip_code = request.POST.get("zip_code")
                            street = request.POST.get("street")
                            external_number = request.POST.get("external_number")
                            internal_number = request.POST.get("internal_number")

                            business_obj.name = name
                            business_obj.email = emails
                            if logo:
                                business_obj.logo = logo
                            business_obj.save()

                            address_obj = business_obj.address
                            address_obj.state = state
                            address_obj.municipality = municipality
                            address_obj.locality = locality
                            address_obj.zipcode = zip_code
                            address_obj.street = street
                            address_obj.neighborhood = street
                            address_obj.internal_number = internal_number
                            address_obj.external_number = external_number
                            address_obj.save()

                            message = u'Información actualizada exitosamente'
                            success = True

                    else:
                        message = u"Negocio no encontrado"

                else:
                    message = u"Opción no válida"

        except Exception as e:
            print("Exception in UpdateBusinessView => {}".format(str(e)))

        response = {"success": success, "message": message}
        return JsonResponse(response)
      
class GenerateOnlyPdfView(View):

    def post(self, request, *args, **kwargs):
        success = False
        message = u"Error no controlado, favor de comunicarse a soporte técnico"

        try:
            if request.is_ajax():
                business_obj = kwargs['account']
                ids = list(PayRoll.objects.filter(query).filter(status__in=['S', 'C']).order_by('-id').values_list('id', flat=True))
                payroll_report_obj = PayrollReport.objects.create(
                    xml=False,
                    pdf=True,
                    invoices_ids=ids,
                    business=business_obj
                )

                tasks_id = payroll_report_obj.create_only_pdf()

                message = "El archivo PDF se comenzó a generar, una vez que este listo se enviará por email a: {}. En caso de tener algún error favor de comunicarse a soporte técnico y especificar el siguiente id:{}".format(', '.join(business_obj.email), tasks_id)
                success = True

            else:
                message = u'Petición inválida'

        except Exception as e:
            print("Exception in GenerateOnlyPdfView => {}".format(str(e)))

        return JsonResponse({"success": success, "message": message})


class ListCSDView(View):

    def post(self, request, *args, **kwargs):
        satfile_list_result = []
        total = 0

        try:
            if request.is_ajax() and request.method == 'POST':
                taxpayer_id = request.POST.get('taxpayer_id', None)
                if taxpayer_id is not None:
                    start = int(request.POST.get('iDisplayStart'))
                    length = int(request.POST.get('iDisplayLength'))

                    satfile_filter = SatFile.objects.filter(business__taxpayer_id=taxpayer_id)
                    total = satfile_filter.count()
                    satfile_filter = satfile_filter[start:start+length]

                    for satfile_obj in satfile_filter:
                        satfile_list_result.append([
                            satfile_obj.business.taxpayer_id,
                            satfile_obj.business.name,
                            satfile_obj.serial_number,
                            satfile_obj.get_status_display(),
                        ])

        except Exception as e:
            print("Exception in ListCSDView => {}".format(str(e)))

        response = {
            'aaData': satfile_list_result,
            'iTotalRecords': total,
            'iTotalDisplayRecords': total,
        }
        return JsonResponse(response)
      
class AddViewCSD(View):

    def post(self, request, *args, **kwargs):
        success = False
        message = "Error"

        try:
            if request.method == 'POST' and request.is_ajax():
                # Obtener datos de la petición
                public_cer = request.FILES.get("cer", None)
                private_key = request.FILES.get("key", None)
                pwd_key = request.POST.get("csd_password", None)
                business_id = request.POST.get("business_id", None)

                if public_cer is not None and private_key is not None and pwd_key is not None and business_id is not None:
                    # Obtener Business
                    business_obj = Business.objects.get(id=business_id)

                    # Crear archivos temporales
                    public_cer_string = public_cer.read()
                    private_key_string = private_key.read()
                    tmp_private_key = tempfile.NamedTemporaryFile(delete=False)
                    tmp_private_key.write(private_key_string)
                    tmp_private_key.close()
                    tmp_pem_key = tempfile.NamedTemporaryFile(delete=False)
                    tmp_pem_key.close()
                    tmp_public_cer = tempfile.NamedTemporaryFile(delete=False)
                    tmp_public_cer.write(public_cer_string)
                    tmp_public_cer.close()
                    tmp_pem_cer = tempfile.NamedTemporaryFile(delete=False)
                    tmp_pem_cer.close()

                    # Verificar que el pass corresponda con el key
                    command_key = 'openssl pkcs8 -inform DER -in %s -out %s -passin pass:\'%s\'' % (
                        tmp_private_key.name, tmp_pem_key.name, pwd_key)
                    is_valid_key = os.system(command_key)
                    if is_valid_key != 0:
                        raise Exception('Error, la clave no es la correcta')

                    # Verificar que sea CSD
                    command_cer = 'openssl x509 -inform DER -in %s -pubkey -out %s' % (
                        tmp_public_cer.name, tmp_pem_cer.name)
                    is_valid_cer = os.system(command_cer)
                    if is_valid_cer != 0:
                        raise Exception(u'Error, Certificado (.cer) inválido o está dañado el archivo')
                    cert = X509.load_cert(tmp_pem_cer.name)
                    evp = EVP.load_key(tmp_pem_key.name)
                    serial = hex(cert.get_serial_number())[3:-1:2]
                    subject = cert.get_subject().__str__()
                    certificate_type = 'C' if "OU" in subject else 'F'
                    if certificate_type != 'C':
                        raise Exception(u'Error, Los archivos corresponden a la FIEL')

                    # Verificar caducidad
                    datetime_now = datetime.now()
                    expiration_date = cert.get_not_after().get_datetime().replace(tzinfo=None)
                    expedition_date = cert.get_not_before().get_datetime().replace(tzinfo=None)
                    if expedition_date > datetime_now:
                        raise Exception(u'Error, el certificado no se encuentra Vigente')
                    if expiration_date <= datetime_now:
                        raise Exception(u'Error, el certificado está revocado o caducó')

                    # Registrar en FINKOK
                    response, client = FinkokWS().edit(business_obj.taxpayer_id, 'A',
                                                      public_cer_string.encode('base64'),
                                                      private_key_string.encode('base64'),
                                                      pwd_key, business_obj.finkok_account)
                    if hasattr(response, 'success'):
                        if response.success:
                            if response.message != "Account was Activated successfully":
                                message = "Error al registrar los certificados, asegúrate de que sean los correctos"
                                raise Exception(message)
                        else:
                            message = "Error al registrar los certificados, asegúrate de que sean los correctos"
                            raise Exception(message)
                    else:
                        message = "Error al registrar los certificados, asegúrate de que sean los correctos"
                        raise Exception(message)

                    # Almacenar en el modelo
                    sat_file_obj, created = SatFile.objects.get_or_create(business_id=business_obj.id,
                                                                          serial_number=serial)
                    sat_file_obj.cer_file = public_cer
                    sat_file_obj.key_file = private_key
                    sat_file_obj.status = 'A'
                    sat_file_obj.passphrase = pwd_key
                    sat_file_obj.default = True
                    sat_file_obj.save()

                    success = True
                    message = "Certificados registrados exitosamente"
                else:
                    message = u"Datos inválidos"
            else:
                message = u"Petición inválida"
        except Exception as e:
            message = str(e)
            print("Exception in AddViewCSD => {}".format(str(e)))

        return JsonResponse({"success": success, "message": message})