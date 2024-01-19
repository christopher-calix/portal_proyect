#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Juan Pérez and Abimelec Chávez'
__copyright__ = 'Copyright (C) 2017  S.A. de C.V., Proyecto: X'
__credits__ = ['Alfredo Herrejón', 'Alexis Martínez', 'Juan Pérez', 'Abimelec Chávez']
__licence__ = 'Privativo'
__version__ = '1.4'
__maintainer__ = 'Alfredo Herrejón, Alexis Martínez, Juan Pérez and Abimelec Chávez'
__email__ = ['desarrollo@quadrum.com.mx']
__status__ = 'Development'


from django.conf import settings

import os
from suds.client import Client
from lxml import etree
from datetime import datetime
import logging
import ssl
if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context


class FinkokWS(object):

  #PRODUCTION = True
  PRODUCTION = False
  #STAMP_URL = 'https://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl'
  STAMP_URL = settings.FK_STAMP_URL
  CANCEL_URL = settings.FK_CANCEL_URL
  UTILITIES_URL = settings.FK_UTILITIES_URL
  REGISTRATION_URL = settings.FK_REGISTRATION_URL
  INC_URL = settings.FK_INC_URL
  USERNAME = settings.FK_USERNAME
  PASSWORD = settings.FK_PASSWORD

  if PRODUCTION:
    #STAMP_URL = 'https://facturacion.finkok.com/servicios/soap/stamp.wsdl'
    #CANCEL_URL = 'https://facturacion.finkok.com/servicios/soap/cancel.wsdl'
    #USERNAME = 'cem@finkok.com'
    #PASSWORD = 'x<!GS_4A'
    pass


  def __init__(self, demo=True):
    pass


  @staticmethod
  def stamp(xml_string, attempts=1, business_obj=None):
       response = None
       client = None
       stamp_url = FinkokWS.STAMP_URL
       username, password = business_obj.get_fk_account()
       print('El negocio:{} va ha timbrar con las credenciales username:{} password:{}'.format(
           business_obj.taxpayer_id, username, password))
       try:
           if attempts < 5:
               client = Client(stamp_url, location=stamp_url, cache=None, timeout=120)
               response = client.service.sign_stamp(bytes(xml_string, 'utf-8').encode('base64'), username, password)
       except Exception as e:
           print("Exception in FinkokWS[stamp] => {}".format(str(e)))
           errors_timeout = ['time-out', 'timeout', 'timedout', 'timed-out', '504', 'gateway', 'timed out']
           if any(x in str(e).lower() for x in errors_timeout):
               attempts += 1
               response, client = FinkokWS.stamp(xml_string, attempts=attempts, business_obj=business_obj)
       return response, client

  @staticmethod
  def cancel(UUID=None, rfc=None, cer=None, key=None):
    try:
      response = None
      client = None
      cancel_url = FinkokWS.CANCEL_URL
      username = FinkokWS.USERNAME
      password = FinkokWS.PASSWORD 
      store_p = False
      
      client = Client(cancel_url, location=cancel_url, cache=None)
      invoices_list = client.factory.create("UUIDS")
      invoices_list.uuids.string = [UUID]
      response = client.service.cancel(invoices_list, username, password, rfc, cer, key, store_p)
    except Exception as e:
      print ("Exception cancel() => %s" % str(e))
    
    return response, client

  def registration_add(self, taxpayer_id, type_user, cer, key, passphrase):
    try:
      response = None
      client = None
      registartion_url = FinkokWS.REGISTRATION_URL

      # FIX TEMPORAL POR SEPARACION DE CUENTAS DE TIMBRADO
      if taxpayer_id == "IPS210624259":
        username = "pae_IPS210624259@finkok.com"
        password = "z+nE6FWm5ja>5h#g"
      elif taxpayer_id == "WVP2106246M0":
        username = "pae_WVP2106246M0@finkok.com"
        password = "Gn=CD&4j9#?cVxQD"
      else:
        username = FinkokWS.USERNAME
        password = FinkokWS.PASSWORD
      # END FIX TEMPORAL POR SEPARACION DE CUENTAS DE TIMBRADO

      client = Client(registartion_url, location=registartion_url, cache=None)
      response = client.service.add(
        reseller_username= username,
        reseller_password = password,
        taxpayer_id = taxpayer_id,
        type_user = type_user,
        coupon= '',
        added = '',
        cer = cer,
        key = key,
        passphrase = passphrase
      )

    except Exception as e:
      print ("Exception registration_add() => %s" % str(e))

    return response, client
  
  @staticmethod
  def get_xml(uuid, taxpayer_id):
    try:
      response = None
      client = None
      utilities_url = FinkokWS.UTILITIES_URL
      username = FinkokWS.USERNAME
      password = FinkokWS.PASSWORD

      client = Client(utilities_url, location=utilities_url, cache=None)
      response = client.service.get_xml(username, password, uuid, taxpayer_id)

    except Exception as e:
      print ("Exception in FinkokWS[stamp] => {}".format(str(e)))

    return response, client

  @staticmethod
  def inc(taxpayer_id):
    response = None
    client = None
    inc_url = FinkokWS.INC_URL
    username = FinkokWS.USERNAME
    password = FinkokWS.PASSWORD
    try:
      client = Client(inc_url, location=inc_url, cache=None)
      response = client.service.check(taxpayer_id, username, password)
    except Exception as e:
      print ("Exception in FinkokWS[inc] => {}".format(str(e)))

    return response, client

  @staticmethod
  def report_total(taxpayer_id=None, date_from=None, date_to=None, fk_account_obj=None):
    response = None
    client = None
    try:
      if not taxpayer_id:
        raise Exception("taxpayer_id is empty")

      if not date_from:
        raise Exception("date_from is empty")

      if not date_to:
        raise Exception("date_to is empty")

      if not fk_account_obj:
        raise Exception("fk_account_obj is empty")

      url = FinkokWS.UTILITIES_URL
      username = fk_account_obj.username
      password = fk_account_obj.password

      client = Client(url, location=url, cache=None)
      response = client.service.report_total(username, password, taxpayer_id, date_from, date_to, 'I')
    except Exception as e:
      print ("Exception in FinkokWS[report_total] => {}".format(str(e)))

    return response, client

  def edit(self, taxpayer_id, status, cer, key, passphrase, fk_account_obj):
    response = None
    client = None

    try:

      if not taxpayer_id:
        raise Exception("taxpayer_id is empty")

      if not status:
        raise Exception("staus is empty")

      if not cer:
        raise Exception("cer is empty")

      if not key:
        raise Exception("key is empty")

      if not passphrase:
        raise Exception("passphrase is empty")

      if not fk_account_obj:
        raise Exception("fk_account_obj is empty")

      registartion_url = FinkokWS.REGISTRATION_URL
      username = fk_account_obj.username
      password = fk_account_obj.password

      client = Client(registartion_url, location=registartion_url, cache=None)
      response = client.service.edit(username, password, taxpayer_id, status, cer, key, passphrase)

    except Exception as e:
      print ("Exception in FinkokWS[edit] => {}".format(str(e)))

    return response, client
    


class FinkokWSRetentions(object):

  PRODUCTION = False
  STAMP_URL = 'https://demo-facturacion.finkok.com/servicios/soap/retentions.wsdl'
  UTILITIES_URL = 'https://demo-facturacion.finkok.com/servicios/soap/utilities.wsdl'
  USERNAME = 'dev_iusa@finkok.com'
  PASSWORD = 'e_7bwebyPbk%'


  if PRODUCTION:
    STAMP_URL = 'https://facturacion.finkok.com/servicios/soap/retentions.wsdl'
    USERNAME = 'iusa_nomina@finkok.com'
    PASSWORD = 'Biep$Umoa8r-'


  def __init__(self, demo=True):
    pass


  @staticmethod
  def stamp(xml_string, demo=True):
    response = None
    client = None
    stamp_url = FinkokWSRetentions.STAMP_URL
    username = FinkokWSRetentions.USERNAME
    password = FinkokWSRetentions.PASSWORD 

    client = Client(stamp_url, location=stamp_url, cache=None)
    response = client.service.stamp(xml_string.encode('base64'), username, password)

    return response, client

  @staticmethod
  def cancel(UUID=None, rfc=None, cer=None, key=None):
    try:
      response = None
      client = None
      cancel_url = FinkokWS.CANCEL_URL
      username = FinkokWS.USERNAME
      password = FinkokWS.PASSWORD 
      store_p = False
      
      client = Client(cancel_url, location=cancel_url, cache=None)
      invoices_list = client.factory.create("UUIDS")
      invoices_list.uuids.string = [UUID]
      response = client.service.cancel(invoices_list, username, password, rfc, cer, key, store_p)
    except Exception as e:
      print ("Exception cancel() => %s" % str(e) ) 
    
    return response, client
