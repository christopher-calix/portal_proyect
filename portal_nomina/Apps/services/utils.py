# -*- coding: utf-8 -*-
from Apps.nomina_app.models import PayRoll, PayRollDetail, Perception, Deduction, OtherPayment, Inability
from Apps.nomina_app.models import Account
from Apps.nomina_app.models import DetailsHistory
from Apps.nomina_app.models import History
from Apps.nomina_app.models import Business, Employee
from Apps.nomina_app.utils import valiate_nomina, get_values, send_notification, create_employee
from Apps.nomina_app.stamp import FINKOKWS
from Apps.users.models import User

from pdb import set_trace
from lxml import etree
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage, BadHeaderError

# import pycurl
try:
    import StringIO 
except ImportError:
    from io import StringIO 

def proccess_data(xml_string, user):
  #set_trace()
  success, message  = False, 'Error al procesar Archivo'
  try:
    total_files, success_files, failed_files = 0,0,0
    uuid = None
    account = Business.objects.get(user=user)
    taxpayer_id = account.taxpayer_id
    success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer_id)
    print ('--------------------- Result ---------------------')
    print (success_validate, message_validate)
    print ('--------------------------------------------------')
    if success_validate:
      status, notes = 'A', 'Comprobante cargado con exito'
      try:
        data_dict = get_values(xml_string)
        uuid = data_dict['uuid']
        data_dict['xml'] = xml_string
        data_dict['business_id'] = account.id
        employee = Employee.objects.get(taxpayer_id=data_dict['rtaxpayer_id'])
        data_dict['employee_id'] = employee.id
        payroll = PayRoll(**data_dict)
        payroll.save()
        try:
          name = data_dict['receiver_name']
          emission_date = data_dict['emission_date']
          issuer_name = data_dict['issuer_name']
          rtaxpayer_id = data_dict['rtaxpayer_id']
          taxpayer_id = data_dict['taxpayer_id']
          url = '%s/dashboard/invoices/?uuid=%s' %(settings.DOMAIN,uuid)
          to_user = data_dict['employee']
          to_emails = data_dict['employee'].email
          context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }
          send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
        except:
          pass
        success, message = True, 'Comprobante cargado con exito'
      except Exception as e:
        print ("Error al guardar datos en BD => %s" % str(e))
      success_files = success_files+1 
    else:
      try:
        xml_etree = etree.fromstring(xml_string)
        uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
      except:
        pass
      status = 'R'
      notes = message_validate
      message = message_validate
      failed_files = failed_files+1
    try:
      data_dict = get_values(xml_string)
      history = History(business=data_dict['business'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
      history.save()
      details_history = DetailsHistory(uuid=uuid if uuid else None, status=status, notes=notes, history=history, name='Archivo procesado por WS')
      details_history.save()
    except Exception as e:
      print ("Error al guardar datos del hitorial ==> {}".format(str(e)))
  except Exception as e:
    print ("Exception in proccess_data ==> {}".format(str(e)))

  print ('------------------------------------------ Result ------------------------------------------')
  print ('{} ==> {} ==> {}'.format(success, uuid ,message_validate))
  print ('--------------------------------------------------------------------------------------------')
  return success, message

def stamp_data(xml_string, user):
  success, message  = False, 'Error al procesar Archivo'
  try:
    total_files, success_files, failed_files = 0,0,0
    uuid = None
    account = user.account
    taxpayer_id = account.taxpayer_id
    response, client = FINKOKWS.sign_stamp(xml_string, account)
    if hasattr(response, 'CodEstatus') and 'Comprobante timbrado satisfactoriamente' in response.CodEstatus:
      xml_string = response.xml.encode('UTF-8')
      success_validate, message = True, u'Comprobante timbrado satisfactoriamente'
      try:
        xml_etree = etree.fromstring(xml_string)
        namespaces = {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
        rtaxpayer_id = xml_etree.xpath('.//cfdi:Receptor/@Rfc',namespaces=namespaces)[0]
        employee_exists = Employee.objects.filter(taxpayer_id=rtaxpayer_id).exists()
        if not employee_exists:
          create_employee_success = create_employee(xml_etree)
      except Exception as e:
        print('Exception creating USER => {}'.format(str(e)))
      message_validate = message
    elif hasattr(response, 'CodEstatus') and 'Comprobante timbrado previamente' in response.CodEstatus:
      xml_string = response.xml.encode('UTF-8')
      success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer_id)
      if success_validate:
        message = u'Comprobante timbrado previamente'
    elif response.Incidencias:
      success_validate = False
      message_validate = u'Error no clasificado.'
      try:
        error = response.Incidencias.Incidencia[0]
        message_validate = '{} - {}'.format(error.CodigoError, error.MensajeIncidencia)
      except:
        message_validate = u'{} - {}'.format(error.CodigoError, error.MensajeIncidencia)
    if success_validate:
      status, notes = 'A', 'Comprobante cargado con exito'
      try:
        data_dict = get_values(xml_string)
        uuid = data_dict['uuid']
        data_dict['xml'] = xml_string
        payroll = PayRoll(**data_dict)
        payroll.save()
        try:
          name = data_dict['receiver_name']
          emission_date = data_dict['emission_date']
          issuer_name = data_dict['issuer_name']
          rtaxpayer_id = data_dict['rtaxpayer_id']
          taxpayer_id = data_dict['taxpayer_id']
          url = '%s/dashboard/invoices/?uuid=%s' %(settings.DOMAIN,uuid)
          to_user = data_dict['employee']
          to_emails = data_dict['employee'].email
          context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }
          send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
        except:
          pass
        success, message = True, 'Comprobante {} timbrado y cargado con exito'.format(payroll.uuid)
      except Exception as e:
        print ("Error al guardar datos en BD => %s" % str(e))
      success_files = success_files+1 
    else:
      try:
        xml_etree = etree.fromstring(xml_string)
        uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
      except:
        pass
      status = 'R'
      notes = message_validate
      message = message_validate
      failed_files = failed_files+1
    try:
      data_dict = get_values(xml_string)
      history = History(business=data_dict['business'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
      history.save()
      details_history = DetailsHistory(uuid=uuid if uuid else None, status=status, notes=notes, history=history, name='Archivo procesado por WS')
      details_history.save()
    except Exception as e:
      print ("Error al guardar datos del hitorial ==> {}".format(str(e)))
  except Exception as e:
    print ("Exception in proccess_data ==> {}".format(str(e)))
  print ('-------------------------------------------- Result ------------------------------------------')
  try:
    print ('{} ==> {} ==> {}'.format(success, uuid , message_validate.encode('utf-8')))
  except:
    try:
      print ('{} ==> {} ==> {}'.format(success, uuid , message_validate.decode('utf-8')))
    except:
      try:
        print ('{} ==> {} ==> {}'.format(success, uuid , message_validate))
      except:
        try:
          print ('{} ==> {} ==> {}'.format(success, uuid , message_validate))
        except:
          print ('Error ocurrido durante la operacion')
  print ('----------------------------------------------------------------------------------------------')
  return success, message


def proccess_data_zr(content_zip_rar, user):
  #set_trace()
  success, message  = False, 'Error al procesar Archivo'
  try:
    list_details=[]
    total_files, success_files, failed_files = 0,0,0
    uuid = None
    taxpayer_id = user.account.taxpayer_id
    for file in content_zip_rar.namelist():
      uuid = None
      xml_string = content_zip_rar.read(file)
      success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer_id)
      if success_validate:
        status, notes = 'A', 'Comprobante cargado con exito'
        try:
          data_dict = get_values(xml_string)
          uuid = data_dict['uuid']
          data_dict['xml'] = xml_string
          payroll = PayRoll(**data_dict)
          payroll.save()
          try:
            name = data_dict['receiver_name']
            emission_date = data_dict['emission_date']
            issuer_name = data_dict['issuer_name']
            rtaxpayer_id = data_dict['rtaxpayer_id']
            taxpayer_id = data_dict['taxpayer_id']
            url = '%s/dashboard/invoices/?uuid=%s' %(settings.DOMAIN,uuid)
            to_user = data_dict['employee']
            to_emails = data_dict['employee'].email
            context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }
            send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
          except:
            pass
        except Exception as e:
          print ("Error al guardar datos en BD => %s" % str(e))
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
      print ('-------------------------------------------- Result ------------------------------------------')
      print ('{} ==> {} ==> {}'.format(success_validate, uuid ,notes))
      print ('----------------------------------------------------------------------------------------------')
    content_zip_rar.close()
    try:
      data_dict = get_values(xml_string)
      history = History(business=data_dict['business'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
      history.save()
      for details in list_details:
        details_history = DetailsHistory(uuid=details[0], status=details[1], notes=details[2], history=history, name=details[3])
        details_history.save()
      success, message = True, 'Archivo cargado con exito'
    except Exception as e:
      print ("Error al guardar datos del hitorial ==> {}".format(str(e)))
  except Exception as e:
    print ("Exception in proccess_data_zr ==> {}".format(str(e)))
  return success, message

def stamp_data_zr(content_zip_rar, user):
  success, message  = False, 'Error al procesar Archivo'
  try:
    list_details=[]
    total_files, success_files, failed_files = 0,0,0
    uuid = None
    account = Business.objects.get(user=user)
    taxpayer_id = account.taxpayer_id
    for file in content_zip_rar.namelist():
      uuid = None
      xml_string = content_zip_rar.read(file)
      isstamped, message_isstamped = is_stamped(xml_string)
      if isstamped:
        success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer_id)
        if success_validate:
          status, notes = 'A', 'Comprobante cargado con exito'
          try:
            data_dict = get_values(xml_string)
            uuid = data_dict['uuid']
            data_dict['xml'] = xml_string
            payroll = PayRoll(**data_dict)
            payroll.save()
            try:
              name = data_dict['receiver_name']
              emission_date = data_dict['emission_date']
              issuer_name = data_dict['issuer_name']
              rtaxpayer_id = data_dict['rtaxpayer_id']
              taxpayer_id = data_dict['taxpayer_id']
              url = '%s/dashboard/invoices/?uuid=%s' %(settings.DOMAIN,uuid)
              to_user = data_dict['employee']
              to_emails = data_dict['employee'].email
              context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }
              send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
            except:
              pass
          except Exception as e:
            print ("Error al guardar datos en BD => %s" % str(e))
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
      else:
        response, client = FINKOKWS.sign_stamp(xml_string, account)
        if hasattr(response, 'CodEstatus') and 'Comprobante timbrado satisfactoriamente' in response.CodEstatus:
          xml_string = response.xml.encode('UTF-8')
          try:
            xml_etree = etree.fromstring(xml_string)
            namespaces = {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
            rtaxpayer_id = xml_etree.xpath('.//cfdi:Receptor/@Rfc',namespaces=namespaces)[0]
            employee_exists = Employee.objects.filter(taxpayer_id=rtaxpayer_id).exists()
            if not employee_exists:
              create_employee_success = create_employee(xml_etree)
          except Exception as e:
            print('Exception creating USER => {}'.format(str(e)))
          success_validate, message_validate, message = True, u'Comprobante timbrado satisfactoriamente', u'Comprobante timbrado satisfactoriamente'
        elif hasattr(response, 'CodEstatus') and 'Comprobante timbrado previamente' in response.CodEstatus:
          xml_string = response.xml.encode('UTF-8')
          success_validate, message_validate = valiate_nomina(xml_string=xml_string, taxpayer_id=taxpayer_id)
          if success_validate:
            message = u'Comprobante timbrado previamente'
        elif response.Incidencias:
          success_validate = False
          message_validate = u'Error no clasificado.'
          try:
            error = response.Incidencias.Incidencia[0]
            message_validate = '{} - {}'.format(error.CodigoError, error.MensajeIncidencia)
          except:
            message_validate = u'{} - {}'.format(error.CodigoError, error.MensajeIncidencia)
        if success_validate:
          status, notes = 'A', 'Comprobante timbrado y cargado con exito'
          try:
            data_dict = get_values(xml_string)
            uuid = data_dict['uuid']
            data_dict['xml'] = xml_string
            payroll = PayRoll(**data_dict)
            payroll.save()
            try:
              name = data_dict['receiver_name']
              emission_date = data_dict['emission_date']
              issuer_name = data_dict['issuer_name']
              rtaxpayer_id = data_dict['rtaxpayer_id']
              taxpayer_id = data_dict['taxpayer_id']
              url = '%s/dashboard/invoices/?uuid=%s' %(settings.DOMAIN,uuid)
              to_user = data_dict['employee']
              to_emails = data_dict['employee'].email
              context = { 'name': name, 'emission_date': emission_date, 'uuid': uuid, 'issuer_name': issuer_name, 'rtaxpayer_id': rtaxpayer_id, 'taxpayer_id': taxpayer_id, 'url': url }
              send_notification(title='Nuevo CFDI | Portal de Nominas', message='Una nueva nomina ha sido cargada', to_user=to_user, emails=to_emails, html_url='invoices/notification_invoice.html', context=context)
            except:
              pass
            success, message = True, 'Comprobante cargado con exito'
          except Exception as e:
            print ("Error al guardar datos en BD => %s" % str(e))
          success_files = success_files+1 
        else:
          try:
            xml_etree = etree.fromstring(xml_string)
            uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
          except:
            pass
          status = 'R'
          notes = message_validate
          message = message_validate
          failed_files = failed_files+1
      list_details.append([uuid, status, notes, file])
      print ('-------------------------------------------- Result ------------------------------------------')
      try:
        print ('{} ==> {} ==> {}'.format(success, uuid , message_validate.encode('utf-8')))
      except:
        try:
          print ('{} ==> {} ==> {}'.format(success, uuid , message_validate.decode('utf-8')))
        except:
          try:
            print ('{} ==> {} ==> {}'.format(success, uuid , message_validate))
          except:
            try:
              print ('{} ==> {} ==> {}'.format(success, uuid , message_validate))
            except:
              print ('Errorrrrrr')
      print ('----------------------------------------------------------------------------------------------')
    content_zip_rar.close()
    try:
      data_dict = get_values(xml_string)
      history = History(business=data_dict['business'], employee=data_dict['employee'], totales_files=failed_files+success_files,failed_files=failed_files,successful_files=success_files)
      history.save()
      for details in list_details:
        details_history = DetailsHistory(uuid=details[0], status=details[1], notes=details[2], history=history, name=details[3])
        details_history.save()
      success, message = True, 'Archivo cargado con exito'
    except Exception as e:
      print ("Error al guardar datos del hitorial ==> {}".format(str(e)))
  except Exception as e:
    print ("Exception in stamp_data_zr ==> {}".format(str(e)))

  return success, message

def is_stamped(xml_string):
  try:
    success, message = False, u'El CFDI no contiene un timbre'
    xml_etree = etree.fromstring(xml_string)
    tfd = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces= {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})
    if tfd:
      success, message = True, u'CFDI timbrado'
  except Exception as e:
    print (u'Exception in is_stamped ==> {}'.format(str(e)))
  return success, message


def send_notifation(uuid):
  try:
    success, message = False, 'Error al enviar notificacion'
    subject = u'Notificación de Comprobante Fiscal de Nómina'
    invoice = PayRoll.objects.get(uuid=uuid)
    from_email = settings.DEFAULT_FROM_EMAIL
    name_receiver=invoice.receiver_name
    name_issuer=invoice.issuer_name
    taxpayer_receiver=invoice.rtaxpayer_id
    taxpayer_issuer=invoice.taxpayer_id
    date=invoice.emission_date
    data_receiver=str(date)
    date_final=(data_receiver[:10])
    url = '%s/dashboard/invoices/?uuid=%s' %(settings.DOMAIN,uuid)
    to_email = Account.objects.get(taxpayer_id='VAAM130719H60').user.email
    #redirigimos valores uno por defecto por rfc del emisor
    extra_dic = {'url':url, 'receiver_name':name_receiver, 'emision_date':date_final, 'uuid':uuid, 'issuces_name':name_issuer, 'taxpayer_id':taxpayer_issuer, 'rtaxpayer_id':taxpayer_receiver}
    html_content = render_to_string('email_template.html', extra_dic)
    if subject and from_email and html_content and to_email:
      try:
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = "html"
        msg.send()
        success, message = True, 'Correo Enviado satisfactoriamente %s' % (to_email)
      except Exception as e:
        print ('Error al enviar correo ==> %s' % str(e))
        message = 'Error al enviar correo'
  except Exception as e:
    print ('Exception in send_notifation => %s' % (str(e)))
    message = str(e)

  print (success, message)


def import_payroll(business_id, parser_dict):
    try:
        email = None
        user_obj = None
        extras = parser_dict.get('Extras', {})
        receptor = parser_dict.get('Receptor')
        nom_receptor = parser_dict.get('Nominas')[0].get('Receptor')

        employee_filter = Employee.objects.filter(taxpayer_id=receptor['Rfc'])

        if employee_filter.exists():  # Si existe
          employee_obj = employee_filter[0]
          # Hay que asignarle el negocio si no tiene ese negocio
          if business_id not in list(employee_obj.businesses.values_list('id', flat=True)):
            business_obj = Business.objects.get(id=business_id)
            employee_obj.businesses.add(business_obj)
          
          employee_obj.name = receptor['Nombre']
          employee_obj.curp = nom_receptor['Curp']
          employee_obj.mbid = nom_receptor['NumEmpleado']
          employee_obj.puesto = nom_receptor['Puesto']
          employee_obj.department = nom_receptor['Departamento'].split('-')[0]
          employee_obj.position = nom_receptor['Puesto']
          employee_obj.bank = nom_receptor['Banco']
          employee_obj.bank_account = nom_receptor['CuentaBancaria']
          employee_obj.nss = nom_receptor['NumSeguridadSocial']
          employee_obj.antiquity = nom_receptor['Antiguedad']
          employee_obj.contract_type = nom_receptor['TipoContrato']
          employee_obj.working_type = nom_receptor['TipoJornada']
          employee_obj.regime_type = nom_receptor['TipoRegimen']
          employee_obj.joined_date = nom_receptor['FechaInicioRelLaboral']
          employee_obj.risk = nom_receptor['RiesgoPuesto']
          employee_obj.periodicity = nom_receptor['PeriodicidadPago']
          employee_obj.base_salary = nom_receptor['SalarioBaseCotApor']
          employee_obj.daily_salary = nom_receptor['SalarioDiarioIntegrado']
          employee_obj.entfed = nom_receptor['ClaveEntFed']
          employee_obj.unionized = nom_receptor['Sindicalizado']
          employee_obj.status = 'A'
          employee_obj.save()

        else: # Si no existe, hay que crear el empleado

          # Si la empresa es 94-BIGDATA, tomar el email del ATI
          if business_id in (94,) and 'email' in extras.keys():
            email = extras.get('email')
          else: # si no es 94-BIGDATA continuar el proceso normal
            email = '{}@archlatam.com'.format(receptor['Rfc'])

          if email is not None:
            user_obj, user_create = User.objects.get_or_create(email=email)
            if user_create:
              user_obj.role = 'E'
              user_obj.is_active = True
              user_obj.name = receptor['Nombre']
              user_obj.set_password(receptor['Rfc'])
              user_obj.save()

          employee_obj = Employee.objects.create(taxpayer_id=receptor['Rfc'])
          business_obj = Business.objects.get(id=business_id)
          employee_obj.businesses.add(business_obj)
          if user_obj is not None:
            employee_obj.user_id = user_obj.id
          employee_obj.name = receptor['Nombre']
          employee_obj.curp = nom_receptor['Curp']
          employee_obj.mbid = nom_receptor['NumEmpleado']
          employee_obj.puesto = nom_receptor['Puesto']
          employee_obj.department = nom_receptor['Departamento'].split('-')[0]
          employee_obj.position = nom_receptor['Puesto']
          employee_obj.bank = nom_receptor['Banco']
          employee_obj.bank_account = nom_receptor['CuentaBancaria']
          employee_obj.nss = nom_receptor['NumSeguridadSocial']
          employee_obj.antiquity = nom_receptor['Antiguedad']
          employee_obj.contract_type = nom_receptor['TipoContrato']
          employee_obj.working_type = nom_receptor['TipoJornada']
          employee_obj.regime_type = nom_receptor['TipoRegimen']
          employee_obj.joined_date = nom_receptor['FechaInicioRelLaboral']
          employee_obj.risk = nom_receptor['RiesgoPuesto']
          employee_obj.periodicity = nom_receptor['PeriodicidadPago']
          employee_obj.base_salary = nom_receptor['SalarioBaseCotApor']
          employee_obj.daily_salary = nom_receptor['SalarioDiarioIntegrado']
          employee_obj.entfed = nom_receptor['ClaveEntFed']
          employee_obj.unionized = nom_receptor['Sindicalizado']
          employee_obj.status = 'A'
          employee_obj.save()

          #Enviar notificación de creacion del usuario
          # if business_id in (94,):
          #   if 'email' in extras.keys():
          #     email_ = extras.get('email')
          #     employee_obj.send_register_email(email_)

        # FIX para univar y almacenar el lugar de pago
        if bool(extras):
          state = extras.get('state', None)
          municipality = extras.get('municipality', None)
          if state is not None and municipality is not None:
            employee_obj.state = extras.get('state', None)
            employee_obj.municipality = extras.get('municipality', None)
            employee_obj.save()
        # FIX para univar y almacenar el lugar de pago

        comprobante = parser_dict.get('Comprobante')
        emisor = parser_dict.get('Emisor')
        nominas = parser_dict.get('Nominas')
        payroll_obj, created_payroll = PayRoll.objects.get_or_create(business_id=business_id, serial=comprobante['Serie'], folio=comprobante['Folio'])
        if payroll_obj.status in ('E', 'P'):
            payroll_obj.version = comprobante['Version']
            payroll_obj.employee = employee_obj
            payroll_obj.taxpayer_id = emisor['Rfc']
            payroll_obj.name = emisor['Nombre']
            payroll_obj.rtaxpayer_id = receptor['Rfc']
            payroll_obj.rname = receptor['Nombre']
            payroll_obj.emission_date = comprobante['Fecha']
            payroll_obj.subtotal = comprobante['SubTotal']
            payroll_obj.total = comprobante['Total']
            payroll_obj.discount = comprobante['Descuento']
            payroll_obj.payment_way = comprobante.get('FormaPago', '')
            payroll_obj.payment_method = comprobante['MetodoPago']
            payroll_obj.notes = parser_dict.get('Observaciones', {'Observacion': None}).get('Observacion')
            payroll_obj.observations = parser_dict.get('Observaciones', {'Observacion': None}).get('Observacion')
            payroll_obj.payroll_num = len(nominas)
            payroll_obj.mbid = nom_receptor['NumEmpleado']
            if business_id in (94,):
                payroll_obj.email = extras.get('email')
        
            relation_type = parser_dict['CfdiRelacionados']['TipoRelacion'] if 'CfdiRelacionados' in parser_dict and 'TipoRelacion' in parser_dict['CfdiRelacionados'] else None
            cfdis_relacionado = parser_dict['CfdiRelacionados']['CfdiRelacionado'] if 'CfdiRelacionados' in parser_dict else []
            payroll_obj.relation_type = relation_type
            payroll_obj.relation_lst = [relation['UUID'] for relation in cfdis_relacionado]
            payroll_obj.save()

        for nomina in nominas:
            nomina_ = nomina.get('Nomina')
            payrolldetail_obj = PayRollDetail.objects.create(
                # business_id=business_id,
                payroll=payroll_obj,
                version=nomina_['Version'],
                payroll_type=nomina_['TipoNomina'],
                paid_date=nomina_['FechaPago'],
                paid_date_from=nomina_['FechaInicialPago'],
                paid_date_to=nomina_['FechaFinalPago'],
                total_oth=nomina_['TotalOtrosPagos'] if nomina_['TotalOtrosPagos'] else 0.0,
                total_ded=nomina_['TotalDeducciones'] if nomina_['TotalDeducciones'] else 0.0,
                total_per=nomina_['TotalPercepciones'] if nomina_['TotalPercepciones'] else 0.0,
                paid_days=nomina_['NumDiasPagados'],
                perceptions_json={
                    'TotalGravado': nomina.get('Percepciones', {}).get('TotalGravado', None),
                    'TotalExento': nomina.get('Percepciones', {}).get('TotalExento', None),
                    'TotalSueldos': nomina.get('Percepciones', {}).get('TotalSueldos', None),
                    'TotalSeparacionIndemnizacion': nomina.get('Percepciones', {}).get('TotalSeparacionIndemnizacion', None),
                    'TotalJubilacionPensionRetiro': nomina.get('Percepciones', {}).get('TotalJubilacionPensionRetiro', None),
                },
                deductions_json={
                    'TotalOtrasDeducciones': nomina.get('Deducciones', {}).get('TotalOtrasDeducciones', None),
                    'TotalImpuestosRetenidos': nomina.get('Deducciones', {}).get('TotalImpuestosRetenidos', None),
                },
                retirement=nomina.get('SeparacionIndemnizacion', None),
                separation=nomina.get('JubilacionPensionRetiro', None),
                registropatronal=nomina.get('Emisor', {}).get('RegistroPatronal', None)
            )
            department_split = nom_receptor['Departamento'].split('-')
            payrolldetail_obj.business_number = department_split[1]
            payrolldetail_obj.period = department_split[2]
            payrolldetail_obj.departament = department_split[0]
            payrolldetail_obj.save()

            percepciones = nomina.get('Percepciones')
            for percepcion in percepciones['Percepcion']:
                extra_hrs_lst = []
                for extra_hr in percepcion['HorasExtra']:
                    extra_hrs_lst.append({
                        'days': extra_hr.get('Dias'),
                        'type': extra_hr.get('TipoHoras'),
                        'extra_hrs': extra_hr.get('HorasExtra'),
                        'amount': extra_hr.get('ImportePagado'),
                    })
                percepcion_json = {
                    'type': percepcion.get('TipoPercepcion'),
                    'code': percepcion.get('Clave'),
                    'concept': percepcion.get('Concepto'),
                    'amount_exp': percepcion.get('ImporteExento'),
                    'amount_grav': percepcion.get('ImporteGravado'),
                    'extra_hrs': extra_hrs_lst
                }
                percepcion_obj = Perception.objects.create(payroll=payrolldetail_obj, **percepcion_json)

            deducciones = nomina.get('Deducciones')
            for deduccion in deducciones['Deduccion']:
                deduccion_json = {
                    'type': deduccion.get('TipoDeduccion'),
                    'code': deduccion.get('Clave'),
                    'concept': deduccion.get('Concepto'),
                    'amount': deduccion.get('Importe'),
                }
                deduccion_obj = Deduction.objects.create(payroll=payrolldetail_obj, **deduccion_json)

            otrospagos = nomina.get('OtrosPagos')

            for otropago in otrospagos['OtroPago']:
                otropago_json = {
                    'type': otropago.get('TipoOtroPago'),
                    'code': otropago.get('Clave'),
                    'concept': otropago.get('Concepto'),
                    'amount': otropago.get('Importe'),
                }
                otropago_obj = OtherPayment.objects.create(payroll=payrolldetail_obj, **otropago_json)

            incapacidades = nomina.get('Incapacidades')
            for incapacidad in incapacidades.get('Incapacidad'):
                incapacidad_json = {
                    'type': incapacidad.get('TipoIncapacidad'),
                    'days': incapacidad.get('DiasIncapacidad'),
                    'amount': incapacidad.get('ImporteMonetario'),
                }
                incapacidad_obj = Inability.objects.create(payroll=payrolldetail_obj, **incapacidad_json)
    except Exception as e:
        print('Exception in import_payroll => {}'.format(str(e)))
        import sys, os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return False, u'Error al importar información a la base de datos'

    return True, ''

def consulta_qr_sat(uuid, taxpayer_id, rtaxpayer_id, total):
  response_obj = None
  response_dic = {}

  try:
    rre = taxpayer_id.upper()
    rr = rtaxpayer_id.upper()
    tt = "%0.6f" % float(total)
    uuid = uuid.upper()

    while len(tt) < 17:
      tt = '0%s' % tt

    data_tpl = """
      <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
          <s:Body>
              <tem:Consulta>
                  <tem:expresionImpresa>?re=%s&amp;rr=%s&amp;tt=%s&amp;id=%s</tem:expresionImpresa>
              </tem:Consulta>
          </s:Body>
      </s:Envelope>
    """

    data = data_tpl % (rre, rr, tt, uuid)

    headers = [
      'Host: consultaqr.facturaelectronica.sat.gob.mx',
      #'POST: https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc HTTP/1.1',
      #'POST: https://srvconsultacfdiuat.cloudapp.net/ConsultaCFDIService.svc HTTP/1.1',
      'POST: https://pruebacfdiconsultaqr.cloudapp.net/ConsultaCFDIService.svc HTTP/1.1',
      'SOAPAction: http://tempuri.org/IConsultaCFDIService/Consulta',
      'Content-Type: text/xml; charset=utf-8',
      'Connection: keep-Alive'
    ]

    b = StringIO.StringIO()
    r = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://pruebacfdiconsultaqr.cloudapp.net/ConsultaCFDIService.svc?wsdl')
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.HTTPHEADER, headers)
    c.setopt(pycurl.POSTFIELDS, data.encode('utf8'))
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.HEADERFUNCTION, r.write)
   
    c.perform()

    response_obj = b.getvalue()
    response_headers = r.getvalue()

    response_obj = etree.fromstring(response_obj)

    try:
        consulta = response_obj.xpath('//tmp:ConsultaResult', namespaces={'tmp':'http://tempuri.org/'})[0]
        codigo_estatus = consulta.xpath('//a:CodigoEstatus', namespaces={'a':'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'})[0]
        estado = consulta.xpath('//a:Estado', namespaces={'a':'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'})[0]
        es_cancelable = consulta.xpath('//a:EsCancelable', namespaces={'a':'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'})[0]
        estatus_cancelacion = consulta.xpath('//a:EstatusCancelacion', namespaces={'a':'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'})[0]
        response_dic = {'codigo_estatus': codigo_estatus.text, 'estado': estado.text, 'es_cancelable': es_cancelable.text, 'estatus_cancelacion': estatus_cancelacion.text}
    except:
        faultcode = response_obj.xpath('//faultcode')[0].text
        faultstring = response_obj.xpath('//faultstring')[0].text

  except Exception as e:
    print("Exception in consulta_qr_sat => {}".format(str(e)))
    print('uuid:{}'.format(uuid))
    print('taxpayer_id:{}'.format(taxpayer_id))
    print('rtaxpayer_id:{}'.format(rtaxpayer_id))
    print('total:{}'.format(total))

  return response_obj, response_dic
