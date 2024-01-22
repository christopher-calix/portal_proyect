
@login_required(login_url='/')
@get_query_history
@get_default_account
def history(request, query, *args, **kwargs):
  #import pdb; pdb.set_trace()
  #locale.setlocale(locale.LC_ALL, "es_MX.UTF-8")
  try:
    if request.method == "POST":
      if request.is_ajax():
        total = 0
        list_result = []
        start = int(request.POST.get('iDisplayStart'))h
        length = int(request.POST.get('iDisplayLength'))
        account = kwargs['account']
        active_taxpayer_id = kwargs['active_taxpayer_id']
        try:
          list_history = History.objects.filter(query).order_by('-date')
          #list_history = list_history.filter(business__taxpayer_id=active_taxpayer_id)
          if request.user.role in ('B', 'S', 'A'):
            list_history = list_history.filter(business__taxpayer_id=active_taxpayer_id)
          elif request.user.role == 'E':
            list_history = list_history.filter(employee=account)
          total = list_history.count()
          list_history = list_history[start:start+length]
          for history in list_history.iterator():
            #print(history.id)
            options_dict = {'details': {
              'detail': reverse('details_history', kwargs={'id_history': history.id})
              }
            }
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
        except Exception, e:
          print 'Exception in list_invoices_1 ==> {}'.format(str(e))
        result = {
          'aaData' : list_result,
          'iTotalRecords': total,
          'iTotalDisplayRecords': total,
        }
        return JsonResponse(result)
    else:
      template = 'history/history.html'
      return TemplateResponse(request, template) 
  except Exception, e:
    print str(e)


@login_required(login_url='/')
@get_default_account
def details_history(request, id_history, *args, **kwargs):
  #locale.setlocale(locale.LC_ALL, "es_MX.UTF-8")
  try:
    if request.method == "POST":
      if request.is_ajax():
        user = request.user
        total = 0
        list_result = []
        start = int(request.POST.get('iDisplayStart'))
        length = int(request.POST.get('iDisplayLength'))
        try:
          query = Q(history_id=id_history)
          list_history = DetailsHistory.objects.filter(query).order_by('status')
          if list_history[0].history.business == kwargs['account'] or user.role in ['S', 'A']:
            total = list_history.count()
            list_history = list_history[start:start+length]
            for history in list_history.iterator():
              list_result.append([
                history.name,
                history.uuid,
                DETAILS_STATUS_HISTORY[history.status],
                history.notes
              ])
        except Exception, e:
          print 'Exception in POST details_history ==> {}'.format(str(e))
        result = {
          'aaData' : list_result,
          'iTotalRecords': total,
          'iTotalDisplayRecords': total,
        }
        return JsonResponse(result)
    else:
      template = 'history/details.html'
      return TemplateResponse(request, template) 
  except Exception, e:
    print 'Exception in details_history ==> {}'.format(str(e))

'''
@login_required(login_url='/')
@get_default_account
def upload(request, *args, **kwargs):
  try:
    if request.method == 'POST' and request.is_ajax() and request.FILES and request.user.role == 'B':
      success, message  = False, ['Error al Cargar Archivo']
      total_files, success_files, failed_files = 0,0,0
      user = request.user
      uuid = None
      taxpayer = kwargs['active_taxpayer_id'] #Account.objects.get(user=user).taxpayer_id
      xml_file = request.FILES.get('file_data')
      if xml_file.content_type in ('text/xml', 'application/xml'):
        xml_string = xml_file.read()
        success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer)
        print '--------------------- Result ---------------------'
        print success_validate, message_validate
        print '--------------------------------------------------'
        if success_validate:
          status, notes = 'A', 'Comprobante cargado con exito'
          try:
            data_dict = get_values(xml_string)
            uuid = data_dict['uuid']
            data_dict['business'] = kwargs['account']
            data_dict['xml'] = xml_string
            ######### SENDING NOTIFICATION ##########
            name = data_dict['receiver_name']
            emission_date = data_dict['emission_date']
            issuer_name = data_dict['issuer_name']
            rtaxpayer_id = data_dict['rtaxpayer_id']
            taxpayer_id = data_dict['taxpayer_id']
            url = request.build_absolute_uri(reverse('list_news'))
            to_user = Employee.objects.get(taxpayer_id=rtaxpayer_id)
            data_dict['employee'] = Employee.objects.get(taxpayer_id=rtaxpayer_id, business=kwargs['account'])
            to_emails = data_dict['employee'].email

            context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }

            payroll = PayRoll(**data_dict)
            payroll.save()
            success, message = True, 'Comprobante cargado con exito'

            send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
            #########################################
          except Exception as e:
            print "Error al guardar datos en BD => %s" % str(e)
          success_files = success_files+1 
        else:
          try:
            xml_etree = etree.fromstring(xml_string)
            uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
          except:
            pass
          status = 'R'
          notes = message_validate
          message = [message_validate]
          failed_files = failed_files+1
        try:
          history = History(business=kwargs['account'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
          history.save()
          details_history = DetailsHistory(uuid=uuid if uuid else None, status=status, notes=notes, history=history, name=xml_file.name)
          details_history.save()
        except Exception as e:
          print "Error al guardar datos del hitorial ==> {}".format(str(e))
        
      elif xml_file.content_type in ('text/zip', 'application/zip'):
        print'------------ UPLOAD ZIP -------------'
        list_details=[]
        zf = zipfile.ZipFile(xml_file, 'r')
        for file in zf.namelist():
          xml_string = zf.read(file)
          success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer)
          print '--------------------- Result ---------------------'
          print success_validate, message_validate
          print '--------------------------------------------------'
          if success_validate:
            status, notes = 'A', 'Comprobante cargado con exito'
            try:
              data_dict = get_values(xml_string)
              uuid = data_dict['uuid']
              data_dict['business'] = kwargs['account']
              data_dict['xml'] = xml_string
              ######### SENDING NOTIFICATION ##########
              name = data_dict['receiver_name']
              emission_date = data_dict['emission_date']
              issuer_name = data_dict['issuer_name']
              rtaxpayer_id = data_dict['rtaxpayer_id']
              taxpayer_id = data_dict['taxpayer_id']
              url = request.build_absolute_uri(reverse('list_news'))
              to_user = Employee.objects.get(taxpayer_id=rtaxpayer_id)
              data_dict['employee'] = Employee.objects.get(taxpayer_id=rtaxpayer_id, business=kwargs['account'])
              to_emails = data_dict['employee'].email

              context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }

              payroll = PayRoll(**data_dict)
              payroll.save()
              success, message = True, 'Comprobante cargado con exito'

              send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
              #########################################
            except Exception as e:
              print "Error al guardar datos en BD => %s" % str(e)
            success_files = success_files+1 
          else:
            try:
              xml_etree = etree.fromstring(xml_string)
              uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
            except:
              pass
            status = 'R'
            notes = message_validate
            failed_files = failed_files+1
          list_details.append([uuid, status, notes, file])
        zf.close()
        try:
          history = History(business=kwargs['account'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
          history.save()
          for details in list_details:
            details_history = DetailsHistory(uuid=details[0], status=details[1], notes=details[2], history=history, name=details[3])
            details_history.save()
          success, message = True, 'Archivo zip cargado con exito'
        except Exception as e:
          print "Error al guardar datos del hitorial ==> {}".format(str(e))
      elif xml_file.content_type in ('text/rar', 'application/vnd.rar', 'application/x-rar'):
        print'------------ UPLOAD RAR -------------'
        list_details=[]
        zf = rarfile.RarFile(xml_file, 'r')
        for file in zf.namelist():
          xml_string = zf.read(file)
          success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer)
          print '--------------------- Result ---------------------'
          print success_validate, message_validate
          print '--------------------------------------------------'
          if success_validate:
            status, notes = 'A', 'Comprobante cargado con exito'
            try:
              ######### SENDING NOTIFICATION ##########
              name = data_dict['receiver_name']
              emission_date = data_dict['emission_date']
              issuer_name = data_dict['issuer_name']
              rtaxpayer_id = data_dict['rtaxpayer_id']
              taxpayer_id = data_dict['taxpayer_id']
              url = request.build_absolute_uri(reverse('list_news'))
              to_user = Employee.objects.get(taxpayer_id=rtaxpayer_id)
              data_dict['employee'] = Employee.objects.get(taxpayer_id=rtaxpayer_id, business=kwargs['account'])
              to_emails = data_dict['employee'].email

              context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }

              payroll = PayRoll(**data_dict)
              payroll.save()
              success, message = True, 'Comprobante cargado con exito'

              send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
              #########################################
            except Exception as e:
              print "Error al guardar datos en BD => %s" % str(e)
            success_files = success_files+1 
          else:
            try:
              xml_etree = etree.fromstring(xml_string)
              uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
            except:
              pass
            status = 'R'
            notes = message_validate
            failed_files = failed_files+1
          list_details.append([uuid, status, notes, file])
        zf.close()
        try:
          history = History(business=kwargs['account'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
          history.save()
          for details in list_details:
            details_history = DetailsHistory(uuid=details[0], status=details[1], notes=details[2], history=history, name=details[3])
            details_history.save()
          success, message = True, 'Archivo zip cargado con exito'
        except Exception as e:
          print "Error al guardar datos del hitorial ==> {}".format(str(e))

  except Exception as e:
    print 'Exception in UPLOAD XML ==> {}'.format(str(e))

  data = {'success': success, 'message': message}
  return JsonResponse(data)
'''

@login_required(login_url='/')
@get_default_account
def upload(request, *args, **kwargs):
  try:
    success, message = False, 'Error al Cargar Archivo'
    # if request.method == 'POST' and request.is_ajax() and request.FILES and request.user.role == 'B':
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
        # import pdb; pdb.set_trace()
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
    print('Exception in upload_zip ==> {}'.format(str(e)))
  return JsonResponse({"success":success, "message":message})

@login_required(login_url='/')
@get_query
@get_default_account
def list_invoices(request, query, *args, **kwargs):
  try:

    if request.method == "POST":
      if request.is_ajax():
        total = 0
        list_result = []
        start = int(request.POST.get('iDisplayStart'))
        length = int(request.POST.get('iDisplayLength'))

        account = kwargs['account']
        active_taxpayer_id = kwargs['active_taxpayer_id']

        try:
          list_invoices = PayRoll.objects.filter(query)
          if request.user.role == "E":
            # list_invoices = list_invoices.exclude(status='E')
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
              }
            }
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
        except Exception, e:
          print 'Exception in list_invoices_1 ==> {}'.format(str(e))
        result = {
          'aaData' : list_result,
          'iTotalRecords': total,
          'iTotalDisplayRecords': total,
        }
        return JsonResponse(result)
    else:
      template = 'invoices/status.html'
      return TemplateResponse(request, template) 
  except Exception, e:
    print 'Exception in list_invoices ==> {}'.format(str(e))

@login_required(login_url='/')
@get_default_account
def list_payrolls_last(request, *args, **kwargs):
  try:
    list_result = []
    total = 0
    if request.method == "POST" and request.is_ajax():
      start = int(request.POST.get('iDisplayStart'))
      length = int(request.POST.get('iDisplayLength'))
      list_invoices = PayRoll.objects.filter(rtaxpayer_id=kwargs['active_taxpayer_id'], status='S').order_by('-emission_date')[0:10]
      total = list_invoices.count()
      list_invoices = list_invoices[start:start+length]
      for invoice in list_invoices.iterator():
        list_result.append([
          str(invoice.uuid).upper(),
          invoice.serial,
          invoice.folio,
          invoice.total
        ])
  except Exception as e:
    print 'Excepcion in list_payrolls_last ==> {}'.format(str(e))
  result = {
    'aaData' : list_result,
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  }
  return JsonResponse(result)

from django.shortcuts import redirect
@login_required(login_url='/')

def dashboard(request, type=None):
  extra_content = {}
  try:
    if request.method == 'GET' and request.user.role == 'E':
      taxpayer_id = request.session.get('active_account')
      if not taxpayer_id:
        taxpayer_id = Employee.objects.filter(user=request.user)[0].taxpayer_id
      extra_content = get_extra_content(taxpayer_id, request.user.role)
  except Exception, e:
    pass
  if request.user.role in ('S',):
    return redirect('/dashboard/business/')
  return TemplateResponse(request, 'dashboard.html', extra_content)

@require_http_methods(["POST"])
@login_required(login_url='/')
def stuffs(request, *args, **kwargs):
  context = {}
  oper = request.POST.get('oper')
  if request.is_ajax():
    if oper == 'set-business':
      try:
        business_id = request.POST.get('business')
        role = request.user.role
        if role in ('A','S','B'):
          business = Business.objects.get(id=business_id)
        else:
          business = Employee.objects.get(id=business_id)
        request.session['business_id'] = business.id
        request.session['active_taxpayer_id'] = business.taxpayer_id
        context['success'] = True
      except Exception, e:
        print 'Exception on core stuffs view {}'.format(str(e))
        context['success'] = False
        context['message'] = 'No existe el negocio o no cuentas con suficientes permisos.'
  return JsonResponse(context)
  

@login_required(login_url='/')
@get_query_business
#@get_default_account
def list_business(request, query, *args, **kwargs):

  try:
    if request.method == 'POST':
      #set_trace()
      total = None
      users_list = []
      append = users_list.append
      role = request.user.role
      if request.is_ajax():
        start = int(request.POST.get('iDisplayStart'))
        length = int(request.POST.get('iDisplayLength'))
        ltype = request.POST.get('ltype')
        accounts = []

        active_account = None
        if request.user.role == 'B':
          active_account = request.session.get('active_account', None)
        #active_taxpayer_id = kwargs['active_taxpayer_id']
        #/home/ccalix/Documentos/Proyecto/portal/app/core/views.py 
        try:
          #import pdb;pdb.set_trace()
          
          
          accounts = Business.objects.filter(query).exclude(status='R').order_by("taxpayer_id")
          if active_account:
            accounts = accounts.filter(taxpayer_id=active_account)
          total = accounts.count()
          accounts = accounts[start:start+length]
          for x in accounts.iterator():
            
            
            user = x.user.last()
            status  = x.status
            user = x.user.filter(role='B')[0] 
            # user = ""
            email = user.email
           # email = ""
            options = render_to_string('admin/business_options.html', {'status': status, 'account_id': x.id, 'user_id': x.user.last().id, 'role': role, 'taxpayer_id': x.taxpayer_id})
            emails = render_to_string('admin/business_emails.html', {'emails': x.email})
            append([x.taxpayer_id, x.name, email, emails, STATUS_ACCOUNT[x.status], options])
        except Exception, e:
          print "error al listar los negocios", str(e)  
        #import pdb;pdb.set_trace()
        result = {
          'aaData' : users_list,
          'iTotalRecords': total,
          'iTotalDisplayRecords': total,
          #'draw' :1,
        }
        return JsonResponse(result)
      else:
        raise Http404
    else:
        template = 'admin/business.html'
        #parameters = get_counter_invoices(request.user.account)
        return TemplateResponse(request, template)#, parameters) 
  except :
    raise HttpResponseRedirect(reverse('dashboard'))

@login_required(login_url='/')
@get_query_employee
def list_employee(request, query, *args, **kwargs):
  try:
    if request.method == 'POST':
      total = None
      users_list = []
      append = users_list.append
      role = request.user.role
      if request.is_ajax():
        start = int(request.POST.get('iDisplayStart'))
        length = int(request.POST.get('iDisplayLength'))
        accounts = []

        try:
          role = request.user.role
          accounts = Employee.objects.filter(query).order_by("taxpayer_id")
          total = accounts.count()
          accounts = accounts[start:start+length]
          for x in accounts.iterator():
            status  = x.status
            email = x.user.email
            options = render_to_string('admin/options.html', {'status': status, 'account_id': x.id, 'user_id': x.user.id, 'role': role, 'taxpayer_id': x.taxpayer_id})
            append([x.taxpayer_id, x.curp, x.name, email, x.department, x.position, STATUS_ACCOUNT[x.status], options])
        except Exception, e:
          print str(e)  
        
        #import pdb;pdb.set_trace()
        result = {
          'aaData' : users_list,
          'iTotalRecords': total,
          'iTotalDisplayRecords': total,
          #'draw' :1,
        }
        return JsonResponse(result)
      else:
        raise Http404
    else:
        template = 'admin/employee.html'
        #parameters = get_counter_invoices(request.user.account)
        return TemplateResponse(request, template)#, parameters) 
  except :
    raise HttpResponseRedirect(reverse('dashboard'))

@login_required(login_url='/')
@get_query_users
def list_users(request, query, *args, **kwargs):
  try:
    if request.method == 'POST' and request.is_ajax():
      total, users_list = 0, []
      u_append = users_list.append
      start, length = int(request.POST.get('iDisplayStart')), int(request.POST.get('iDisplayLength'))
      users = User.objects.filter(query).order_by("id")
      users = users[start:start+length]
      total = users.count()
      for user in users:
        role = user.role
        status = user.is_active
        last_login = user.last_login
        name = user.name
        email = user.email
        options = render_to_string('admin/user_options.html', {'status': status, 'mail': email, 'user_id': user.id}, request)
        u_append([last_login,name,email,TYPEUSER[status], TYPEROLE[role] ,options])
      result = {
        'aaData' : users_list,
        'iTotalRecords': total,
        'iTotalDisplayRecords': total,
        #'draw' :1,
      }
      return JsonResponse(result)
    else:
        template = 'admin/users.html'
        return TemplateResponse(request, template) 
  except Exception as e:
    raise HttpResponseRedirect(reverse('dashboard'))

@login_required(login_url='/')
@get_default_account
def user_options(request, *args, **kwargs):
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
          print "Exception user_options update-info => Username already exists."
          message = 'Ese usuario ya esta en uso.'
        except Exception, e:
          print "Exception user_options update-info => " + str(e)
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
            except Exception, e:
              print 'Exception user_options => adding user => ' + str(e)
              message = 'Registrando nuevo usuario.'  
          except Exception, e:
            print 'Exception user_options => validate_email => ' + str(e)
            message = 'Correo inválido.'
        except Exception, e:
          print "Exception user_options add-user => " + str(e)
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
            except Exception, e:
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
            except Exception, e:
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
            except Exception, e:
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
            except Exception, e:
              message = 'Error al reactivar'
        except Exception, e:
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
        except Exception, e:
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

  except Exception, e:
    print 'Exception in user_options => %s' % e
  data.update({
    'success': success,
    'message': message,
  })
  return JsonResponse(data)

@login_required(login_url='/')
@require_http_methods(["GET"])
@get_default_account
def download(request, payroll_id, *args, **kwargs):
  try:
    user = request.user
    role = user.role
    account = kwargs['account']
    query = Q(id=payroll_id)
    invoice = PayRoll.objects.get(query)
    inv_account = None
    if role == 'B':
      inv_account = invoice.business
    elif role == 'E':
      inv_account = invoice.employee
    if inv_account == account or user.role in ('S', 'A','B','E'):
      filename = '%s.xml' % invoice.get_filename()
      response = HttpResponse(invoice.xml, content_type='application/xml text/xml')
      response['Content-Disposition'] = 'attachment; filename=%s' % filename
      return response
    else:
      return HttpResponseForbidden()
  except Exception as e:
    print 'Error al descargar XML ==> %s' % str(e)
    raise Http404
    #return HttpResponseRedirect(reverse('list_invoices'))

@login_required(login_url='/')
@require_http_methods(["GET"])
@get_default_account
def txt(request, payroll_id, *args, **kwargs):
  try:
    invoice = PayRoll.objects.get(id=payroll_id)
    filename = '%s.txt' % invoice.get_filename()
    response = HttpResponse(invoice.txt, content_type='application/txt text/txt')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
  except Exception as e:
    print 'Error al descargar XML ==> %s' % str(e)
    raise Http404

@login_required(login_url='/')
@require_http_methods(["GET"])
def download_upload(request, upload_id, *args, **kwargs):
  try:
    upload_obj = Upload.objects.get(id=upload_id)
    upload_string = upload_obj.file.read()
    try:
      upload_string = upload_string.encode('utf-8')
    except:
      pass
    response = HttpResponse(upload_string, content_type='application/zip text/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % upload_obj.name
    return response
  except Exception as e:
    print 'Error al descargar upload ==> %s' % str(e)
    raise Http404

@login_required(login_url='/')
@require_http_methods(["GET"])
def download_zip(request, zip_id, *args, **kwargs):
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
    print 'Error al descargar zip ==> %s' % str(e)
    raise Http404

@login_required(login_url='/')
@require_http_methods(["GET"])
@get_default_account
def pdf(request, uuid, *args, **kwargs):
  try:
    user = request.user
    role = user.role
    account = kwargs['account']
    query = Q(uuid=uuid)
    invoice = PayRoll.objects.get(query)
    inv_account = ''
    business_number = invoice.details.first().business_number
    if role == 'B':
      inv_account = invoice.business
    elif role == 'E':
      inv_account = invoice.employee
    if inv_account == account or user.role in ('S','B','E','A'):
      filename = '%s.xml' % invoice.uuid
      print filename
      XML_PATH = invoice._xml.path
      #PDF_PATH= settings.INVOICE_STORAGE
      PDF_PATH= '/tmp/'
      result_pdf = CreatePDF(xml_path=XML_PATH, filename=filename, business_number=business_number)
      print '--------'
      
      if result_pdf.success:
        print "Creacion de PDF: OK"
        pdf_file=open('%s%s.pdf'%(PDF_PATH, uuid))
        pdf_read = pdf_file.read()
        response = HttpResponse(pdf_read, content_type='application/pdf text/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % invoice.get_filename()
        os.remove('%s/%s.pdf'%(PDF_PATH, uuid))
        return response
      else:
        print u"Creacion de PDF: ERROR"
    else:
      return HttpResponseForbidden()
  except Exception as e:
    print 'Error al descargar PDF ==> %s' % str(e)
    raise Http404


def get_extra_content(taxpayer_id, role):
  try:
    total_nomina, total_per, total_ded, total_oth, max_number = 0,0,0,0,0
    totales = PayRoll.objects.filter(rtaxpayer_id=taxpayer_id, status='S').aggregate(total=Sum('total'), total_per=Sum('total_per'), total_ded=Sum('total_ded'), total_oth=Sum('total_oth'))
    total_nomina = totales['total'] if totales['total'] else 0.00
    total_per = totales['total_per'] if totales['total_per'] else 0.00
    total_ded = totales['total_ded'] if totales['total_ded'] else 0.00
    total_oth = totales['total_oth'] if totales['total_oth'] else 0.00
  except:
    pass
  try:
    import locale
    locale.setlocale(locale.LC_TIME, '')
    list_months, list_total_nomina, list_total_neto_nomina, list_total_per, list_total_ded, list_total_oth = [], [], [], [], [], [] 
    
    date_initial = datetime.now()
    for i in range(5):
      list_months.append((date_initial - relativedelta(months=i)).strftime("%B").capitalize())

    date_initial = datetime.now()
    new_date = date_initial + relativedelta(months=1)
    datestr = '{}-{}-01T00:00:00'.format(new_date.year, new_date.month)
    date_filter = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
    for i in range(5):
      new_date_filter = date_filter - relativedelta(months=1)
      totales_payrolls = PayRoll.objects.filter(rtaxpayer_id=taxpayer_id, status='S').filter(emission_date__range=[new_date_filter, date_filter]).aggregate(total=Sum('total'), total_per=Sum('total_per'), total_ded=Sum('total_ded'), total_oth=Sum('total_oth'))
      list_total_neto_nomina.append(float(totales_payrolls['total']) if totales_payrolls['total'] is not None else 0.0)
      list_total_per.append(float(totales_payrolls['total_per']) if totales_payrolls['total_per'] is not None else 0.0)
      list_total_ded.append(float(totales_payrolls['total_ded']) if totales_payrolls['total_ded'] is not None else 0.0)
      list_total_oth.append(float(totales_payrolls['total_oth']) if totales_payrolls['total_oth'] is not None else 0.0)
      list_total_nomina.append(float(totales_payrolls['total_per'] if totales_payrolls['total_per'] is not None else Decimal(0.00) + totales_payrolls['total_oth'] if totales_payrolls['total_oth'] is not None else Decimal(0.00)))
      date_filter = date_filter - relativedelta(months=1)
    max_number = max(list_total_nomina)
  except Exception as e:
    print 'Exception in get values for graphs ==> {}'.format(str(e))
  #print list_months 
  #print list_total_nomina 
  #print list_total_per 
  #print list_total_ded 
  #print list_total_oth
  total, n, e, v, r, p, f, d, c = 0, 0, 0, 0, 0, 0, 0, 0, 0
  notifications = None
  now = datetime.now() - relativedelta(hours=1)
  try:
    list_invoices = PayRoll.objects.filter((Q(employee__taxpayer_id=taxpayer_id)))
    n = list_invoices.filter(status='N').count()
    e = list_invoices.filter(status='E').count()
    v = list_invoices.filter(status='V').count()
    r = list_invoices.filter(status='R').count()
    p = list_invoices.filter(status='P').count()
    f = list_invoices.filter(status='F').count()
    c = list_invoices.filter(status='C').count()
    d = list_invoices.filter(status='D').count()
    if role == 'E':
      notifications =  Notifications.objects.filter(employee__taxpayer_id=taxpayer_id, status='N', date__gte=now).order_by('date')
    elif role == 'B':
      notifications =  Notifications.objects.filter(business__taxpayer_id=taxpayer_id, status='N', date__gte=now).order_by('date')
    if settings.DEBUG:
      if role == 'E':
        notifications =  Notifications.objects.filter(employee__taxpayer_id=taxpayer_id, status='N').order_by('date')
      elif role == 'B':
        notifications =  Notifications.objects.filter(business__taxpayer_id=taxpayer_id, status='N').order_by('date')
    total =  list_invoices.count()
    #import pdb; pdb.set_trace()
  except:
    pass
  extra_content = {
    'n':n, # En procesos de validacion
    'e':e, # Con Fecha de Pago
    'v':v, # Sin Fecha de Pago
    'p':p, # Pagados sin confirmar
    'd':d, # Fecha de pago vencida
    'f':f, # finalizado pagados
    'c':c, # cancelado
    'r':r, # rechazados
    'total_invoices': total,
    'total_notifications': notifications.count() if notifications else 0,
    'notifications': notifications,
    'total_nomina': total_nomina, 
    'total_per': total_per, 
    'total_ded': total_ded, 
    'total_oth': total_oth,
    'list_months': json.dumps(list_months),
    'list_total_neto_nomina': json.dumps(list_total_neto_nomina),
    'list_total_per': json.dumps(list_total_per),
    'list_total_ded': json.dumps(list_total_ded),
    'list_total_oth': json.dumps(list_total_oth),
    'list_total_nomina': json.dumps(list_total_nomina)
  }
  #print extra_content
  return extra_content

@login_required(login_url='/')
def notification(request):
  #set_trace()
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
    
    if ordered(notification_response) != ordered(notification_cache) or base_path != base_path_cache:
      cache.set('%s-notifications' % (request.user.id) , notification_response)
      cache.set('%s-base_path' % (request.user.id), base_path)
      new_notification = True

    notification_response.update({'new': new_notification, 'notification-count': notification_count})
    
  except Exception, e:
    print str(e)

  return JsonResponse(notification_response)

def ordered(obj):
  if isinstance(obj, dict):
    return sorted((k, ordered(v)) for k, v in obj.items())
  if isinstance(obj, list):
    return sorted(ordered(x) for x in obj)
  else:
    return obj


@login_required(login_url='/')
@get_default_account
def profile(request, *args, **kwargs):
  try:
    if request.method == 'GET':
      country = ''
      state = ''
      municipality = ''
      locality = ''
      street = ''
      external_number = ''
      phone = ''
      account = kwargs['account'] #Account.objects.get(user=request.user)
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
       print 'Exception in profile get taxpayer_id ==> {}'.format(str(e))
      if account.address is not None:
        country = account.address.country if account.address.country else ''
        state = account.address.state if account.address.state else ''
        municipality = account.address.municipality if account.address.municipality else ''
        locality = account.address.locality if account.address.locality else ''
        street = account.address.street if account.address.street else ''
        external_number = account.address.external_number if account.address.external_number else ''
        phone = account.address.phone if account.address.phone else ''
      logo = '/static/img/avatar.png'
      #logo = account.logo.path
      #full_name = account.name.split(' ')
      if request.user.role == 'B':
        logo = account.logo
      context_data = {
        u'person_type': person_type,
        u'name': account.name,#.get_name(),
        u'taxpayer_id': taxpayer_id,
        #u'first_name': account.first_name if account.first_name else '',
        #u'last_name': account.last_name if account.last_name else '',
        #u'second_last_name': account.second_last_name if account.second_last_name else '',
        u'country': country,
        u'state': state,
        u'municipality': municipality,
        u'locality': locality,
        u'street': street,
        u'external_number': external_number,
        u'phone': phone,
        u'logo': logo,
      }

    return TemplateResponse(request, 'profile/info.html', context_data)#, parameters) 
  except Exception as e:
    print 'Exception in profile ==> {}'.format(str(e))


@login_required(login_url='/')
def delete(request):
  #import pdb; pdb.set_trace()
  try:
    uuid = request.POST.get('uuid')
    query = Q(uuid=uuid)
    invoice = PayRoll.objects.get(query)
    path = invoice._xml.path
    os.remove(path)
    invoice.delete()
  except Exception as e:
    print 'Error Al intentar borrar el registro %s' % str(e)
  return HttpResponseRedirect(reverse('list_invoices'))


@login_required(login_url='/')
@get_default_account
def send_simple_message(request, *args, **kwargs):
  success = False
  message = ''
  if request.user.role == 'E':
    business_obj = kwargs['account'].business
  else:
    business_obj = kwargs['account']
  try:
    list_email =  request.POST.get('mail')[:-1].split(',')
    uuid = request.POST.get('uuid')
    query = Q(uuid=uuid)
    invoice = PayRoll.objects.get(query)
    XML_PATH = invoice._xml.path
    #PDF_PATH= settings.INVOICE_STORAGE
    PDF_PATH= '/tmp'
    filename = '%s.xml' % invoice.uuid
    try:
      business_number = invoice.details.first().business_number
      result_pdf = CreatePDF(xml_path=XML_PATH, filename=invoice.filename, business_number=business_number)
      if result_pdf.success:
        print "Creación de PDF: OK"
    except Exception, e:
      print "Exception %s" % str(e)

    ###################################DATOS PARA HTML DEL EMAIL#######################################
    uuid=invoice.uuid
    name_receiver=invoice.rname
    name_issuer=invoice.name
    taxpayer_receiver=invoice.rtaxpayer_id
    taxpayer_issuer=invoice.taxpayer_id
    date=invoice.emission_date
    data_receiver=str(date)
    date_final=(data_receiver[:10])
    filenamepdf = '%s/%s' % (PDF_PATH, invoice.filename.replace('txt', 'pdf'))
    xml = invoice._xml.path
    pdf = open(filenamepdf)
    #################################PARAMETROS PARA ENVIAR EMAIL######################################
    subject = u'Envio de Comprobante Fiscal de Nómina'
    from_email = settings.DEFAULT_FROM_EMAIL
    #set_trace()
    extra_dic = {'receiver_name':name_receiver, 'emision_date':date_final, 'uuid':uuid, 'issuces_name':name_issuer, 'taxpayer_id':taxpayer_issuer, 'rtaxpayer_id':taxpayer_receiver}
    html_content = render_to_string('invoices/send_cfdi.html', extra_dic, request)
    #list_email = ['alfredasio@live.com','tigreac96@gmail.com']
    #list_email = cadena.split(",")
    #print 'destinatarios ==> %s' %list_email
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
      except Exception, e:
        print 'Error al enviar correo ==> %s' % str(e)
        message = 'Error al enviar correo'
    else:
      print 'Error al enviar correo'
      message = 'Error al enviar correo'
  except Exception as e:
    print 'Error al enviar correo ==> %s' % str(e)
    message = 'Error al enviar correo'

  result = {'success': success, 'message': message}
  print result
  return JsonResponse(result)

@login_required(login_url='/')
@get_default_account
def cancel(request, *args, **kwargs):
  try:
    #set_trace()
    result = {'success' : False, 'message': u'Error el cancelar CFDI'}
    if request.method == 'POST' and request.is_ajax():
      uuid = request.POST.get('uuid')
      notes = request.POST.get('notes', '')
      taxpayer_id = request.POST.get('taxpayer_id')
      account = kwargs['account']
      motive = request.POST.get('motive', '')
      folio = request.POST.get('folio', '')

      # sat_file = SatFile.objects.get(business_id=account.id)
      # serial = sat_file.serial_number 
      try:
        print("uuid", uuid)
        print("taxpayer_id", taxpayer_id)
        print("motive", motive)
        print("foliosustitucion", folio)
        response, client = FINKOKWS.sign_cancel(uuid, taxpayer_id, motive, folio, business_obj=account)
        print response
        if response and hasattr(response, 'Folios'):
          status_uuid = response.Folios[0][0].EstatusUUID
          status_cancel = unicode(response.Folios[0][0].EstatusCancelacion)
          if status_uuid in ('201', '202'):
            message = u'Nomina en proceso de cancelación'
            try:
              invoice = PayRoll.objects.get(uuid=uuid)
              url = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?WSDL"
              client = suds_client(url, location=url, cache=None)
              result_ = client.service.Consulta(invoice.get_satquery_str())
              print result_
              if result_.Estado == "Cancelado":
                message = u'Nomina Cancelada'
                invoice.notes = u'{} => {}'.format(message, notes)
                invoice.status = 'C'
                invoice.status_sat = 'C'
                invoice.save()
                print "UUID:{} Cancelado".format(invoice.uuid)
              elif result_.Estado == "Vigente":
                message = u'La nomina aún se encuentra Vigente'
              result['success'], result['message'] = True, message
            except Exception as e:
             print 'Exception update cancellation status ==> {}'.format(str(e))
            #elif status_cancel == u'En proceso':
            #  result['success'], result['message'] = True, u'CFDI en proceso de cancelación.'
            #elif status_cancel == u'No cancelable':
            #  result['success'], result['message'] = True, u'CFDI no cancelable.'
        elif response and hasattr(response, 'CodEstatus'):
          result['message'] = unicode(response['CodEstatus'])
      except Exception as e:
        print 'Exption in WS sign_cancel ==> {}'.format(str(e))
  except Exception as e:
    print 'Exception in cancel CFDI ==> {}'.format(str(e))
  return JsonResponse(result)

@login_required(login_url='/')
@get_default_account
def edit_information(request, *args, **kwargs):
  try:
    result = {'success':False, 'message':u'Error al editar la información'}
    if request.method == 'POST' and request.is_ajax():
      option = request.POST.get('option')
      account = kwargs['account']  #request.user.account
      if option == 'Account':
        try:
          first_name = request.POST.get('first_name')
          last_name = request.POST.get('last_name')
          second_last_name = request.POST.get('second_last_name')
          logo = request.FILES.get('logo')
          account.name = first_name
          #account.last_name = last_name
          #account.second_last_name = second_last_name
          account.logo = logo
          account.save()
          result['success'], result['message'] = True, u'Datos actualizados exitosamente'
        except Exception as e:
          print 'Exception in SAVE ACCOUNT ==> {}'.format(str(e))
      elif option =='Address':
        try:
          country = request.POST.get('country')
          state = request.POST.get('state')
          municipality = request.POST.get('municipality')
          locality = request.POST.get('locality')
          street = request.POST.get('street')
          external_number = request.POST.get('external_number')
          phone = request.POST.get('phone')
          if account.address is None:
            address = Address(
              country = country,
              state = state,
              municipality = municipality,
              locality = locality,
              street = street,
              external_number = external_number,
              phone = phone
            )
            address.save()
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
          print 'Exception in SAVE ADDRESS ==> {}'.format(str(e))
      elif option =='Fiscal':
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
            command_key= 'openssl pkcs8 -inform DER -in %s -out %s -passin pass:\'%s\'' % (tmp_private_key.name, tmp_pem_key.name, pwd_key)
            is_valid_key = os.system(command_key)
            if is_valid_key != 0:
              raise Exception('Error')
            tmp_public_cer = tempfile.NamedTemporaryFile(delete=False)
            tmp_public_cer.write(public_cer.read())
            tmp_public_cer.close()
            tmp_pem_cer = tempfile.NamedTemporaryFile(delete=False)
            tmp_pem_cer.close()
            command_cer = 'openssl x509 -inform DER -in %s -pubkey -out %s' % (tmp_public_cer.name, tmp_pem_cer.name)
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
            #import pdb; pdb.set_trace()
            if certificate_type == 'C':
              account.finkok_account = finkok_account
              account.finkok_password = finkok_password
              sat_file_obj, created = SatFile.objects.get_or_create(business_id=account.id,serial_number=serial)
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
          print 'Exception in SAVE FISCAL ==> {}'.format(str(e))
  except Exception as e:
    print 'Exception in EDIT_INFORMATION ==> {}'.format(str(e))
  print result
  return JsonResponse(result)


#@login_required(login_url='/')
def sign_payroll(request):
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
    print 'Exception in sign_payroll => %s' % (str(e))
  result = {'success':success, 'message':message}
  return JsonResponse(result)

def get_image(absolute_uri, _id):
  print absolute_uri
  img = qrcode.make(absolute_uri)
  #print(type(img))
  #print(img.size)
  # <class 'qrcode.image.pil.PilImage'>
  # (290, 290)
  filename = '{}.png'.format(_id.replace('/', ''))
  image_path = os.path.join(settings.TEMPORARY_QR, filename)
  img.save(image_path)
  return image_path, static('temporary/'+filename)

def get_code(request, *args, **kwargs):
    context = {}
    if request.method == 'GET':
        oper = request.GET.get('oper')
        if oper == 'obtener':
            try:
              #qr_obj = QR.objects.all().order_by('?')[1]
              uuid = request.GET.get('uuid')
              _id = os.urandom(20).encode('base64').strip()
              cache.set(_id, uuid, 600)
              path = reverse('secure', kwargs={'base64string': _id})
              absolute_uri = request.build_absolute_uri(path)
              image_path, static_path = get_image(absolute_uri, _id)
              print(_id, uuid, request.build_absolute_uri(path), image_path, static_path)
              context.update({
                  "success": True,
                  "message": "Secure URL has been generated successfully.",
                  _id: absolute_uri,
                  "qrimage": static_path
              })
            except Exception, e:
                print('Exception', str(e))
                context.update({
                    "success": False,
                    "message": "Something wrong was ocurrs.",
                })
            return JsonResponse(context)
            #raise Exception
    template_name = 'index.html'
    return render(request, template_name)

def sign(request, *args, **kwargs):
  try:
    if request.method == 'GET':
      template_name = 'invoices/sing.html'
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
        print uuid
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
      context = { 'success': success, 'uuid': uuid, 'date':date, 'total_per':total_per, 'total_ded':total_ded, 'total':total, 'total_oth':total_oth }
      return render(request, template_name, context)
  except Exception as e:
    print 'Exception in sign ==> %s' % (str(e))
    raise Http404


@login_required(login_url='/')
def token_add(request):
  token = request.POST.get('token')
  user = request.user
  try:
    get_user_tokens = TokensUser.objects.filter(user=user, token=token)
    if len(get_user_tokens):
      for get_user_token in get_user_tokens:
        if get_user_token.token == token:
          return TemplateResponse(request, 'dashboard.html')
        else:
          TokensUser.objects.create(token=token, user=user)
    else:
      TokensUser.objects.create(token=token, user=user)
  except Exception, e:
    print 'Exception in token_add => %s ' % e
  return TemplateResponse(request, 'dashboard.html')

import re

@login_required(login_url='/')
@get_default_account
def list_news(request, *args, **kwargs):
  if 'read' in request.path:
    if request.user.role in ('B', 'E'):
      try:
        active_account = kwargs['account']
      except:
        active_account = None
      try:
        active_taxpayer_id = kwargs['active_taxpayer_id']
      except:
        active_taxpayer_id = None
      if active_account:
        account = active_account
        if request.user.role == 'B':
          news = News.objects.filter(business=account)
        else:
          news = News.objects.filter(employee=account)
      else:
        try:
          if request.user.role == 'B':
            account = Business.objects.get(user=request.user, taxpayer_id=active_taxpayer_id)
            news = News.objects.filter(business=account)
          elif request.user.role == 'E':
            account = Employee.objects.get(user=request.user, taxpayer_id=active_taxpayer_id)
            news = News.objects.filter(employee=account)
        except Exception, e:
          print 'Exception in list_news function => %s' % e
    else:
      news = News.objects.filter(business=None, employee=None)
    news.update(read=True)
  elif bool(re.findall("[0-9]+", request.path)):
    try:
      new_id = re.findall("[0-9]+", request.path)[0]
      new = News.objects.get(id=new_id)
      new.read = True
      new.save()
    except:
      pass
  return TemplateResponse(request, 'notifications/notifications.html')

@login_required(login_url='/')
@get_default_account
@get_query_uploads
def list_uploads(request, query, *args, **kwargs):
  try:
    if request.method == "POST" and request.is_ajax():
      result = {'aaData' : [], 'iTotalRecords': 0, 'iTotalDisplayRecords': 0,}
      business = kwargs['account']
      total = 0
      list_result = []
      start = int(request.POST.get('iDisplayStart'))
      length = int(request.POST.get('iDisplayLength'))
      uploads_obj = Upload.objects.filter(business_id=business.id).filter(query).order_by('-id')
      total = uploads_obj.count()
      uploads = uploads_obj[start:start+length]
      for upload in uploads:
        url_descarga = None
        upload_id = render_to_string('uploads/strings/number.html', {'number': upload.task_id}, request)
        user = render_to_string('uploads/strings/user.html', {'user':upload.user}, request)
        filename = upload.name
        date = upload.created
        total_txts = render_to_string('uploads/strings/number.html', {'number':upload.total_txt}, request)
        total_txt_good = render_to_string('uploads/strings/number.html', {'number':upload.total_txt_good}, request)
        total_txt_error = render_to_string('uploads/strings/number.html', {'number':upload.total_txt_error}, request)
        status = render_to_string('uploads/strings/status.html', {'status':upload.status}, request)
        if upload.file:
          url_descarga = reverse('download_upload', kwargs={'upload_id': upload.id})
        options = render_to_string('uploads/strings/options.html', {'upload':upload, 'url_descarga':url_descarga}, request)
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
    else:
      template, context = 'uploads/uploads.html', {}
      return render(request, template, context)
  except Exception as e:
    print('Exception in list_uploads => {}'.format(str(e)))
  return JsonResponse(result)

@login_required(login_url='/')
@get_default_account
@get_query_zip
def list_zips(request, query, *args, **kwargs):
  try:
    if request.method == "POST" and request.is_ajax():
      result = {'aaData' : [], 'iTotalRecords': 0, 'iTotalDisplayRecords': 0,}
      business = kwargs['account']
      total = 0
      list_result = []
      start = int(request.POST.get('iDisplayStart'))
      length = int(request.POST.get('iDisplayLength'))
      zip_obj = Zip.objects.filter(business_id=business.id).filter(query).order_by('-id')
      zips = zip_obj[start:start+length]
      for zip_ in zips:
        url_descarga = None
        zip_id = render_to_string('zips/strings/number.html', {'number': zip_.id}, request)
        upload_id = render_to_string('zips/strings/number.html', {'number': zip_.upload_id}, request)
        filename = zip_.name
        date = zip_.date_created
        total_zips = render_to_string('zips/strings/number.html', {'number':zip_.total_zip}, request)
        total_txts = render_to_string('zips/strings/number.html', {'number':zip_.total_txt}, request)
        status = render_to_string('zips/strings/status.html', {'status':zip_.task_status}, request)
        if zip_.file:
          url_descarga = reverse('download_zip', kwargs={'zip_id': zip_.id})
        options = render_to_string('zips/strings/options.html', {'zip':zip_, 'url_descarga':url_descarga}, request)
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
    else:
      template, context = 'zips/zips.html', {}
      return render(request, template, context)
  except Exception as e:
    print('Exception in list_uploads => {}'.format(str(e)))
  return JsonResponse(result)


@login_required(login_url='/')
@get_default_account
def upload_options(request, *args, **kwargs):

  response = {"success": False, "message": u"Error, contacte a soporte Técnico"}
  try:

    if request.method == 'POST' and request.is_ajax():
      business_obj = kwargs['account']
      oper = request.POST.get('oper', None)
      upload_id = int(request.POST.get('object_id'))
      upload_filter = Upload.objects.filter(id=upload_id, business_id=business_obj.id)

      if upload_filter.exists():
        upload_obj = upload_filter[0]

        if oper == "consult":
          payroll_filter = PayRoll.objects.filter(upload_id=upload_id)
          payroll_filter_pending = payroll_filter.filter(status='P')

          # VERIFICAR QUE LOS PAYROLL NO TENGAN ESTATUS P
          if payroll_filter_pending.count() > 0:
            response['message'] = "ZIP en proceso"

          # RECONTAR ERRORES, TIMBRADOS
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

          # ENVIAR REPORTE CORRESPONDIENTE
          upload_obj.send_report_mail()

          # ENVIAR LAS NOMINAS POR CORREO
          for payroll_obj in payroll_filter.filter(status='S'):
              if settings.ASYNC_PROCCESS:
                  send_mail_payroll.apply_async((payroll_obj.id, ))
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
    print('Exception in update_status_task => {}'.format(str(e)))

  return JsonResponse(response)


@login_required(login_url='/')
@get_query
@get_default_account
def generate_report(request, query, *args, **kwargs):

  success = False
  message = u"Error no controlado, favor de comunicarse a soporte técnico"

  try:

    if request.method == "POST" and request.is_ajax():
      business_obj = kwargs['account']

      ids = list(PayRoll.objects.filter(query).filter(status__in=['S', 'C']).order_by('-id').values_list('details', flat=True))

      if request.user.role == "E":
        tasks = generate_report_payrolls_employee.apply_async((business_obj.id, ids),)
      else:
        tasks = generate_report_payrolls.apply_async((business_obj.id, ids),)
      message = "El reporte se comenzó a generar, una vez que este listo se enviara por email a: {}".format(', '.join(business_obj.email))
      success = True

    else:
      message = u"Petición invalida"

  except Exception as e:
    print('Exception in generate_report => {}'.format(str(e)))

  response = {"success": success, "message": message}
  return JsonResponse(response)


@login_required(login_url='/')
@get_query
@get_default_account
def generate_only_pdf(request, query, *args, **kwargs):

  success = False
  message = u"Error no controlado, favor de comunicarse a soporte técnico"

  try:

    if request.method == "POST" and request.is_ajax():

      business_obj = kwargs['account']
      ids = list(PayRoll.objects.filter(query).filter(status__in=['S', 'C']).order_by('-id').values_list('id', flat=True))
      payroll_report_obj = PayrollReport.objects.create(
        xml=False,
        pdf=True,
        invoices_ids=ids,
        business=business_obj
      )

      tasks_id = payroll_report_obj.create_only_pdf()

      message = "El archivo PDF se comenzó a generar, una vez que este listo se enviara por email a: {}. En caso de tener algún error favor de comunicarse a soporte técnico y especificar el siguiente id:{}".format(', '.join(business_obj.email), tasks_id)
      success = True

    else:
      message = u'Petición invalida'

  except Exception as e:
    raise e

  response = {"success": success, "message": message}
  return JsonResponse(response)


@login_required(login_url='/')
@get_query
@get_default_account
def download_payrolls_masive(request, query, *args, **kwargs):
  success = False
  message = u"Error no controlado, favor de comunicarse a soporte técnico"

  try:

    if request.method == "POST" and request.is_ajax():

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
          message = u"Nóminas enviadas"
          success = True
        else:
          message = u"Debes de seleccionar por lo menos un tipo de archivo."

      else:

        if xml or pdf:

          ids = list(PayRoll.objects.filter(query).filter(status__in=['S', 'C']).order_by('-id').values_list('id', flat=True))

          payroll_report_obj = PayrollReport.objects.create(
            xml = xml,
            pdf = pdf,
            invoices_ids = ids,
          )
          if role == "E":
            payroll_report_obj.employee = business_obj
          else:
            payroll_report_obj.business = business_obj

          payroll_report_obj.save()

          tasks_id = payroll_report_obj.create_payroll_zip(split_path)

          message = "El reporte se comenzó a generar, una vez que este listo se enviara por email a: {}".format(', '.join(business_obj.email))
          success = True

        else:
          message = u"Debes de seleccionar por lo menos un tipo de archivo."

    else:
      message = u"Petición invalida"

  except Exception as e:
    print('Exception in download_payrolls_masive => {}'.format(str(e)))

  response = {"success": success, "message": message}
  return JsonResponse(response)



@login_required(login_url='/')
@get_default_account
def business_logo_options(request, *args, **kwargs):

  success = False
  message = "Error no controlado, intenta mas tarde!"

  try:

    if request.method == "POST" and request.is_ajax():
      option = request.POST.get('option', '')
      business_id = request.POST.get('business_id', False)
      if not business_id:
        raise Exception("Negocio no encontrado")
      business_obj = Business.objects.get(id=business_id)
      if option == "get_logo":
        message = business_obj.get_logo()
        success = True

      elif option == "update-logo":
        logo = request.FILES.get('logo')
        business_obj.logo = logo
        business_obj.save()
        message = {
          "message": u"Actualización exitosa",
          "logo": business_obj.get_logo(),
        }
        success = True

      else:
        message = u"opción invalida"

    else:
      message = u"Petición invalida"

  except Exception as e:
    print("Exception in business_logo_options => {}".format(str(e)))

  response = {"success": success, "message": message}
  return JsonResponse(response)


def download_zip_payroll_template(request, secrete_key=None, *args, **kwargs):
  try:

    if request.method != "GET":
      return HttpResponseForbidden()
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
    print("Exception in download_zip_payroll_template => {}".format(str(e)))
    print("secrete_key => {}".format(secrete_key))
    return HttpResponseForbidden()

def download_zip_payroll_check_password(request, *args, **kwargs):
  success, message = False, u"Contraseña Invalida"
  try:

    if request.method == "POST" and request.is_ajax():
      report_id_encrypted = request.POST.get("report_id")
      if report_id_encrypted:
        password = request.POST.get("password", '')
        if password:
          report_id = signing.loads(report_id_encrypted)
          payroll_report_filter = PayrollReport.objects.filter(id=report_id)
          if payroll_report_filter.exists():
            payroll_report_obj = payroll_report_filter[0]
            if payroll_report_obj.get_decrypted_password() == password.strip():

              message = reverse('download_zip_payroll', kwargs={"secrete_key": report_id_encrypted})
              success = True
  except Exception as e:
    print("Exception in download_zip_payroll_check_password => {}".format(str(e)))

  return JsonResponse({"success": success, "message":message})

def download_zip_payroll(request, secrete_key, *args, **kwargs):
  try:

    if request.method == "GET":

      report_id = signing.loads(secrete_key)
      payroll_report_filter = PayrollReport.objects.filter(id=report_id)

      if payroll_report_filter.exists():
        payroll_report_obj = payroll_report_filter[0]
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

    else:
      return HttpResponseForbidden()

  except Exception as e:
    print("Exception in download_zip_payroll => {}".format(str(e)))
    return HttpResponseForbidden()


@login_required(login_url='/')
@get_default_account
def CreateviewBusiness(request, *args, **kwargs):

  success = False
  message = u"Error al registrar el negocio, intenta más tarde!"

  try:

    if request.method == "POST" and request.is_ajax():

      # OBTENER DATOS DEL "POST"
      #  Bussines
      taxpayer_id = request.POST.get("taxpayer_id")
      emails = request.POST.get("emails")
      logo = request.FILES.get('logo')

      #  User
      username = "admin_{}@archlatam.app".format(taxpayer_id)
      letters = string.ascii_letters + string.ascii_uppercase + string.digits
      password = ''.join(random.choice(letters) for i in range(16))
      type_business = request.user.type_business
      if type_business is None:
          type_business = 'L'

      name = request.POST.get("name")

      #  Address
      state = request.POST.get("state")
      municipality = request.POST.get("municipality")
      locality = request.POST.get("locality")
      zip_code = request.POST.get("zip_code")
      street = request.POST.get("street")
      external_number = request.POST.get('external_number')
      internal_number = request.POST.get('internal_number')

      #  SatFiles
      cer_file = request.FILES.get('cer')
      key_file = request.FILES.get('key')
      passphrase = request.POST.get('csd_password')

      try:
        with transaction.atomic():

          # Crear el objeto User
          if User.objects.filter(email=username).exists():
            message = "Usuario previamente registrado"
            raise Exception(message)
          user_obj = User.objects.create(
            email=username,
            role="B",
            type_business=type_business,
            name=name,
            is_active=True,
            is_superuser=False
          )
          user_obj.set_password(password)
          user_obj.save()

          # Crear el objeto Tokens
          if Token.objects.filter(user=user_obj).exists():
            message = "Token previamente registrado"
            raise Exception(message)
          token_obj = Token.objects.create(user=user_obj)

          # Crear el objecto Address
          address_obj = Address.objects.create(
            country="MEXICO",
            state=state,
            municipality=municipality,
            locality=locality,
            zipcode=zip_code,
            street=street,
            neighborhood=street,
            internal_number=internal_number,
            external_number=external_number,
          )

          # crear el objeto Bussines
          if Business.objects.filter(taxpayer_id=taxpayer_id).exists():
            message = "Negocio previamente registrado"
            raise Exception(message)
          business_obj = Business.objects.create(
            taxpayer_id=taxpayer_id,
            name=name,
            address_id=address_obj.id,
            email=emails[:-1].split(','),
            status="A",
            default=True,
            type=type_business
          )
          business_obj.user.add(user_obj)
          if logo:
            business_obj.logo = logo
          business_obj.save()

          # crear el objeto SatFiles
          response, client = FinkokWS().registration_add(
            taxpayer_id,
            'O',
            cer_file.read().encode('base64'),
            key_file.read().encode('base64'),
            passphrase,
          )
          print response
          if hasattr(response, 'success'):
            if response.success:
              if response.message != "Account Created successfully":
                message = "Error al registrar los certificados, asegurate que sean los correctos"
                raise Exception(message)
            else:
              message = "Error al registrar los certificados, asegurate que sean los correctos"
              raise Exception(message)  
          else:
            message = "Error al registrar los certificados, asegurate que sean los correctos"
            raise Exception(message)

          response, client = FinkokWS().inc(taxpayer_id)
          if hasattr(response, 'exists') and response.exists:
            business_obj.sat_name = response.nombre
            business_obj.save()

          # FIX TEMPORAL POR SEPARACION DE CUENTAS DE TIMBRADO
          if taxpayer_id in ('IPS210624259', 'WVP2106246M0'):
            if taxpayer_id == "IPS210624259":
              business_obj.finkok_account_id = 1
            else:
              business_obj.finkok_account_id = 2
          else:
            # Cuenta general de PAE
            business_obj.finkok_account_id = 12
          business_obj.save()
          # END FIX TEMPORAL POR SEPARACION DE CUENTAS DE TIMBRADO

          # Enviar  token en un correo automatico
          html_content = render_to_string(
              'business/notificacion_add.html',
              {"business": business_obj, "token": token_obj.key}
          )

          subject = u'PORTAL DE NÓMINA | REGISTRO DE NUEVA EMPRESA'.format(
              business_obj.name, business_obj.taxpayer_id)

          msg = EmailMessage(
              subject,
              html_content,
              settings.DEFAULT_FROM_EMAIL,
              settings.NOTIFICATION_ADD_BUSINESS_EMAILS,
          )
          msg.content_subtype = "html"
          msg.send()
          print('Correo Enviado satisfactoriamente')

          message = "Empresa Registrada Exitosamente"
          success = True

      except Exception as e1:
        print(u"Error al guardar información en la base de datos")
        print(e1)
        raise Exception(str(e1))

    else:
      message = u"Petición invalida"

  except Exception as e:
    print("Exception in CreateviewBusiness => {}".format(str(e)))

  response = {"success": success, "message": message}
  return JsonResponse(response)


@login_required(login_url='/')
def UpdateviewBusiness(request, *args, **kwargs):
  success = False
  message = 'Error'

  try:

      if request.method == 'POST' and request.is_ajax():

        option = request.POST.get('option')

        if option in ('get_info_business', 'edit_info_business'):
          taxpayer_id = request.POST.get("taxpayer_id")
          business_id = int(request.POST.get("business_id"))

          business_filter = Business.objects.filter(id=business_id, taxpayer_id=taxpayer_id)
          if business_filter.exists():
            business_obj = business_filter[0]

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

              address_obj =  business_obj.address
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
          message = u"Opción no valida"

  except Exception as e:
    print("Exception in UpdateviewBusiness => {}".format(str(e)))

  response = {"success": success, "message": message}
  return JsonResponse(response)


@login_required(login_url='/')
def ListviewCSD(request, *args, **kwargs):
  satfile_list_result = []
  total = 0

  try:
    if request.method == 'POST' and request.is_ajax():
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
    print("Exception in ListCSDview => {}".format(str(e)))

  response = {
    'aaData' : satfile_list_result,
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  }
  return JsonResponse(response)


@login_required(login_url='/')
def AddviewCSD(request, *args, **kwargs):
  success = False
  message = "Error"

  try:
    if request.method == 'POST' and request.is_ajax():

      # Obtener datos de la peticion
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
        command_key= 'openssl pkcs8 -inform DER -in %s -out %s -passin pass:\'%s\'' % (tmp_private_key.name, tmp_pem_key.name, pwd_key)
        is_valid_key = os.system(command_key)
        if is_valid_key != 0:
          raise Exception('Error, la clave no es la correcta')

        # Verificar que sea CSD
        command_cer = 'openssl x509 -inform DER -in %s -pubkey -out %s' % (tmp_public_cer.name, tmp_pem_cer.name)
        is_valid_cer = os.system(command_cer)
        if is_valid_cer != 0:
          raise Exception(u'Error, Certificado (.cer) invalido o esta dañado el archivo')
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
          raise Exception(u'Error, el certificado esta revocado o caduco')

        # Registrar en FINKOK

        response, client = FinkokWS().edit(business_obj.taxpayer_id, 'A', public_cer_string.encode('base64'), private_key_string.encode('base64'), pwd_key, business_obj.finkok_account)
        if hasattr(response, 'success'):
          if response.success:
            if response.message != "Account was Activated successfully":
              message = "Error al registrar los certificados, asegurate que sean los correctos"
              raise Exception(message)
          else:
            message = "Error al registrar los certificados, asegurate que sean los correctos"
            raise Exception(message)  
        else:
          message = "Error al registrar los certificados, asegurate que sean los correctos"
          raise Exception(message)

        # Almacenar en el modelo
        sat_file_obj, created = SatFile.objects.get_or_create(business_id=business_obj.id, serial_number=serial)
        sat_file_obj.cer_file = public_cer
        sat_file_obj.key_file = private_key
        sat_file_obj.status = 'A'
        sat_file_obj.passphrase = pwd_key
        sat_file_obj.default = True
        sat_file_obj.save()

        success = True
        message = "Certificados registrados exitosamente"
      else:
        message = u"Datos invalidos"
    else:
      message = u"Petición invalida"
  except Exception as e:
    message = str(e)
    print("Exception in AddviewCSD => {}".format(str(e)))

  return JsonResponse({"success": success, "message": message})
