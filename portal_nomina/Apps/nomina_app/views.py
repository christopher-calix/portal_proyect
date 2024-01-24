from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .views_choices import *

from django.contrib.auth.decorators import login_required

from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
###########################################3333

# -*- coding: utf-8 -*-


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



@method_decorator(login_required(login_url='/'), name='dispatch')
class Dashboard(View):
    template_name = 'views/main_views/dashboard.html'

    def get(self, request, *args, **kwargs):
        extra_content = {}
    
        if request.user.is_authenticated == True and request.user.profile.role == 'E':
            taxpayer_id = request.session.get('active_account', None)
            
            if not taxpayer_id:
                taxpayer_id = request.user.profile.employee.taxpayer_id

        elif request.user.is_authenticated == True and request.user.profile.role == 'S':
            return redirect('company/') 

        return render(request, self.template_name, extra_content)
     

     
     
@method_decorator(login_required(login_url='/'), name='dispatch')     
#pendiente el quer_get

class Company(TemplateView):
     template_name = 'views/main_views/companies.html'
     
     def get(self, request, *args, **kwargs):
        template = 'admin/business.html'
        return render(request, template)

     def post(self, request, *args, **kwargs):
         query = request.POST.get('query')
 
         if request.is_ajax():
             start = int(request.POST.get('iDisplayStart'))
             length = int(request.POST.get('iDisplayLength'))
             ltype = request.POST.get('ltype')
             role = request.user.role
 
             try:
                 accounts = Business.objects.filter(query).exclude(status='R').order_by("taxpayer_id")
                 active_account = request.session.get('active_account', None)
                 if active_account and request.user.role == 'B':
                     accounts = accounts.filter(taxpayer_id=active_account)
                 total = accounts.count()
                 accounts = accounts[start:start+length]
 
                 users_list = []
                 for account in accounts.iterator():
                     user = account.user.filter(role='B')[0]
                     email = user.email
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
     template_name = 'views/main_views/users.html'
     
     #def get(self, request, *args, **kwargs):
     #   template = 'admin/users.html'
     #   return render(request, template)

     def post(self, request, query, *args, **kwargs):
        try:
            if request.is_ajax():
                start = int(request.POST.get('iDisplayStart'))
                length = int(request.POST.get('iDisplayLength'))
                users = User.objects.filter(query).order_by("id")[start:start+length]
                total = users.count()
                users_list = []
                for user in users:
                    role = user.role
                    status = user.is_active
                    last_login = user.last_login
                    name = user.name
                    email = user.email
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
     template_name = 'admin/userOptions'
     
     def  post(self, request, query, *args, **kwargs):
          
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
                   user = User.objects.get(id=user_id)
                   name = user.name
                   email = user.email
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
      
                     user = User.objects.get(id=user_id)
                     user.username = username
                     user.email = username
                     user.name = name
                     if new_password is not None:
                       user.set_password(new_password)
      
                     # Edit groups just for Employees (staff)
                     if user.role == 'S':
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
                         user, created = User.objects.get_or_create(email=username, is_superuser=False)
                         if created:
                           user.email = username
                           user.name = name
                           user.is_active = True
                           user.role = _type
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
                       exists_email = User.objects.filter(email=email).exists()
                       exists_taxpayer_id = Business.objects.filter(taxpayer_id=taxpayer_id).exists()
                       if not exists_email:
                         if not exists_taxpayer_id:
                           user = User(email=email, role='B', is_active=bool(int(status)))
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
                       exists_email = User.objects.filter(email=email).exists()
                       exists_taxpayer_id = Employee.objects.filter(taxpayer_id=taxpayer_id).exists()
                       if not exists_email:
                         if not exists_taxpayer_id:
                           curp = request.POST.get('curp')
                           #company = request.POST.get('company')
                           department = request.POST.get('department')
                           puesto = request.POST.get('puesto')
                           mbid = request.POST.get('mbid')
      
                           if curp and mbid and department and puesto:
                             is_active = status == "A"
                             user = User(email=email, role='E', is_active=is_active)
                             user.set_password(pass1)
                             user.save()
      
                             account = Employee()
                             account.name = name
                             account.email = [email]
                             account.curp = curp
                             account.taxpayer_id = taxpayer_id
                             account.status = status
                             #account.business_id = company
                             #if active_account:
                             #  account.business_id = active_account.id
                             #if active_account:
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
                 user = User.objects.get(id=user_id)
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
                       #set_trace()
                       account_id = request.POST.get('account_id')
                       #if active_account:
                       #    account = active_account
                       #else:
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
                       #if active_account:
                       #    account = active_account
                       #else:
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
                       #if active_account:
                       #    account = active_account
                       #else:
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
                       #if active_account:
                       #    account = active_account
                       #else:
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
                         "Correo": employee_obj.user.email,
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
                       user_obj = employee_obj.user
      
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
     template_name = 'views/main_views/employees.html'

class Vouchers(TemplateView):
     template_name = 'views/main_views/vouchers.html'

class Uploads(TemplateView):
     template_name = 'views/main_views/uploads.html'
     
     
     
####################################################################################################

