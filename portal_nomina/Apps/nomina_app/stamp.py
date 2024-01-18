import ssl
import os
from zeep import Client
from lxml import etree
from datetime import datetime
import logging
from django.conf import settings


class FINKOKWS:

    def __init__(self, demo=True):
        pass

    @staticmethod
    def stamp(xml_string):
        response = None
        client = None
        stamp_url = settings.FK_STAMP_URL
        username = settings.FK_USERNAME
        password = settings.FK_PASSWORD

        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        client = Client(stamp_url)
        response = client.service.stamp(xml_string.encode('base64'), username, password)

        return response, client

    @staticmethod
    def sign_stamp(xml_string, account):
        response = None
        client = None
        stamp_url = settings.FK_STAMP_URL
        #username = settings.FK_USERNAME
        #password = settings.FK_PASSWORD
        username = account.finkok_account
        password = account.finkok_password

        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        client = Client(stamp_url)
        response = client.service.sign_stamp(xml_string.encode('base64'), username, password)
        return response, client

    @staticmethod
    def sign_cancel(uuid, taxpayer_id, motive, folio, serial=None, business_obj=None):
        response = None
        client = None
        cancel_url = settings.FK_CANCEL_URL
        # username = settings.FK_USERNAME
        # password = settings.FK_PASSWORD
        username, password = business_obj.get_fk_account()
        print('El negocio:%s va ha timbrar con las credenciales username:%s password:%s' % (business_obj.taxpayer_id, username, password))

        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        client = Client(cancel_url)
        invoices_obj = client.factory.create("ns0:UUID")
        invoices_obj._UUID = uuid
        invoices_obj._Motivo = motive
        invoices_obj._FolioSustitucion = folio
        if False and reason == '01':
            invoices_obj._FolioSustitucion = replacement
        invoices_list = client.factory.create("ns0:UUIDArray")
        invoices_list.UUID.append(invoices_obj)
        response = client.service.sign_cancel(invoices_list, username, password, taxpayer_id, serial, False)

        return response, client

    @staticmethod
    def get_xml(uuid, taxpayer_id, invoice_type='I'):
        response = None
        client = None
        utilities_url = settings.FK_UTILITIES_URL
        username = settings.FK_USERNAME
        password = settings.FK_PASSWORD

        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        client = Client(utilities_url)
        response = client.service.get_xml(username, password, uuid, taxpayer_id, invoice_type)
        xml = response.xml
        try:
            xml = xml.encode('UTF-8')
        except:
            pass
        return xml

    @staticmethod
    def accept_rejects(uuid, rtaxpayer_id, answer, cer, key):
        try:
            response = None
            client = None
            cancel_url = settings.FK_CANCEL_URL
            username = settings.FK_USERNAME
            password = settings.FK_PASSWORD
    
            try:
                client = Client(cancel_url)  # No es necesario especificar location
                uuids_ar = client.factory.create('ns0:UUIDS_AR')  # Use el namespace correcto
                uuids_ar.uuids_ar.UUID_AR.append({'uuid': uuid, 'respuesta': answer})
                response = client.service.accept_reject(uuids_ar, username, password, rtaxpayer_id, cer, key)
            except Exception as e:  # Captura excepciones específicas
                print('Error al crear el cliente SOAP o realizar la llamada:', e)
    
            print('[accept_reject] ==> {}'.format(response))
            return response
        except Exception as e:
            print('Exception in accept_rejects() ==> {}'.format(e))
