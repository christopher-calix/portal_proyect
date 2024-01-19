#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import datetime, date
from app.services.utils import proccess_data, stamp_data
from Apps.nomina_app.models import Account
from lxml import etree as ET
import glob, os

class Command(BaseCommand):
  help = 'weekly payroll import'

  def add_arguments(self, parser):
    pass

  def handle(self, *args, **options):
    subject = "Portal de Nómina | weekly payroll import"
    try:
      path = '/tmp/nominas/'
      if not os.path.exists(path):
        raise Exception ('path {} not exists'.format(path))
      for xml in glob.glob('{}/*.xml'.format(path)):
        with open(xml) as xml_file:
          xml_string = xml_file.read()
          xml_file.close()
        xml_obj = ET.fromstring(xml_string)
        xml_obj.set("Sello","")
        date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        xml_obj.set("Fecha",date_now)
        pay_date = date.today().isoformat()
        namespaces = {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
        xml_obj.find('cfdi:Complemento/nomina12:Nomina',namespaces=namespaces).set('FechaPago', pay_date)
        xml_obj.find('cfdi:Complemento/nomina12:Nomina',namespaces=namespaces).set('FechaFinalPago', pay_date)
       
        taxpayer_id = xml_obj.xpath('.//cfdi:Emisor/@Rfc', namespaces=namespaces)[0]
        user = Account.objects.get(taxpayer_id=taxpayer_id).user
        xml_string = ET.tostring(xml_obj)
        xml_string = xml_string.replace('Antig&#252;edad', 'Antigüedad')
        success, message = stamp_data(xml_string, user)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.SMTP_TO_EMAIL], fail_silently=True)
    except Exception as e:
      print( "Exception in weekly payroll import => %s" % str(e))
      message = "Exception => %s" % str(e)
      send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.SMTP_TO_EMAIL], fail_silently=True)
    
