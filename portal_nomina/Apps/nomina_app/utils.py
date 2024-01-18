import secrets
# -*- coding: utf-8 -*-
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _  # Use gettext instead of ugettext

import os
import re
import time
import uuid
import base64
import urllib.parse  # Use urllib.parse instead of urllib
import pprint
import hashlib
import xml.etree.ElementTree as ET
import urllib.request  # Use urllib.request instead of urllib2
import datetime
import M2Crypto
import traceback
from .models import PayRoll, Account, TokensUser, News, Business, Employee
from lxml import etree
from xml.dom import minidom
from io import StringIO  # Use io.StringIO instead of StringIO
from zeep import Client  # Use zeep instead of suds
from collections import defaultdict
import os
import glob
from moneda import numero_a_letras
from lxml import etree
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    SimpleDocTemplate,
    Frame,
    Paragraph,
    Image,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import landscape, letter, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import logging
from .utils_choices import *
from reportlab.graphics.barcode import code93, code128, code39
import sys
import locale
import math
import ssl
from PIL import Image as im
import logging
from decimal import Decimal
from lxml import etree as ET
from django.contrib.staticfiles.templatetags.staticfiles import static
try:
    locale.setlocale(locale.LC_ALL, "en_US.utf-8")
except:
    locale.setlocale(locale.LC_ALL, "english-US")
from Apps.users.models import User
from .models import Employee
import dropbox

#SAT_FILE_MANAGER = FileManager(valid_types=['octet-stream'])

if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context
    
XML_INVOICE_NAMESPACE = "{http://www.sat.gob.mx/cfd/3}%s"
XML_TFD_NAMESPACE = "{http://www.sat.gob.mx/TimbreFiscalDigital}%s"
XML_XSD_CFDI_VERSION = "3.2"
XML_XSD_CDF_NAME = "cfdv32.xsd"
XML_XSLT_CDF_NAME = "cadenaoriginal_3_2.xslt"

NSMAP_CFDI32 = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}




class SealValidator(object):

  def __init__(self, cfd_seal, x509_cert, original_string, invoice_type='I', xml_string = '', version='3.2'):
    
    self.valid = True
    self.error = ''
    self.invoice_type = invoice_type
    self.sign = cfd_seal
    try:
      self.seal_is_valid = False

      self.x509_cert = x509_cert
      self.original_string = original_string

      self.decoded_sign = base64.decodestring(self.sign)

      if self.original_string is None or self.original_string == "":
        os_obj = OriginalString(xml_string, invoice_type, version=version)
        self.original_string = os_obj.get_original_string()

      rsa = self.x509_cert.get_pubkey().get_rsa()
      pubkey = M2Crypto.EVP.PKey()
      pubkey.assign_rsa(rsa)
      if version in ('3.2', '1.0'):
        pubkey.reset_context(md='sha1')
      elif version == '3.3':
        pubkey.reset_context(md='sha256')
      pubkey.verify_init()
      pubkey.verify_update(self.original_string)
      self.seal_is_valid = bool(pubkey.verify_final(self.decoded_sign))
    except Exception as e:
      self.valid = False
      self.error = str(e)  
   
  
  def is_valid(self):
    if self.valid and self.seal_is_valid:
      result = {
        "success" : True,
        "message" : "The seal is valid for this CFDI",
        "original_string" : self.original_string,
        "sign" : self.sign
      }
    else:
      result = {
        "success" : False,
        "message" : "The seal is not valid for this CFDI",
        "original_string" : self.original_string,
        "sign" : self.sign
      }
    #print result
    return result
  

class OriginalString:

    def __init__(self, xml, invoice_type='I', version='3.2'):

        self.xml_invoice = xml
        self.XSLT_STYLE = None
        self.invoice_type = invoice_type

        if version == '3.2':
            
            self.XSLT_STYLE = settings.XSLT_STYLE_32 
        elif version == '3.3':
            
            self.XSLT_STYLE = settings.XSLT_STYLE_33  

        self.parse_xml()

    def parse_xml(self):
        try:
            doc = ET.fromstring(self.xml_invoice)  # Use ET.fromstring for parsing
            result = self.XSLT_STYLE.applyStylesheet(doc, None)
            self.original_string = str(result)
            self.original_string = self.original_string.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')
            self.original_string = self.original_string.replace('\n','')
            self.original_string = self.original_string.replace('&quot;', '"')
            self.original_string = self.original_string.replace('&lt;', '<')
            self.original_string = self.original_string.replace('&gt;', '>')
            self.original_string = self.original_string.replace('&apos;', '´')
            self.original_string = self.original_string.replace('&amp;', '&')
            self.original_string = self.original_string.strip()
        except Exception as e:  # Correct exception syntax for Python 3
            print(e)  

    def get_original_string(self):
        return self.original_string


class SubjectDNValidator(object):
  
  def __init__(self, taxpayer_id, x509_cert):
    
    self.valid = True
    self.error = ''

    try:
      self.x509_cert = x509_cert

      self.issuer_dn = self.x509_cert.get_subject().as_text()
      self.issuer_dn = self.issuer_dn.decode("utf-8", "replace")

      self.rfc = taxpayer_id
      
    except Exception as e:
      self.valid = False
      self.error = str(e)
  
  
  def is_valid(self):
    result = {
      "success" : False,
      "message" : "The issuer CSD not corresponds to RFC sender by proof comes as fiscal invoice"
    }
    try:
      test_rfc = self.rfc.replace(u'\xd1','N')
      
      test_issuer_dn = unicode(self.issuer_dn)
      test_issuer_dn = test_issuer_dn.replace(u'\\xD1','N').replace(u'\xD1', 'N')      
      
      if self.valid and (test_rfc in test_issuer_dn):
        result = {
          "success" : True,
          "message" : "The issuer CSD corresponds to RFC sender by proof comes as fiscal invoice"
        }
    except (Exception, e):
      self.error = str(e)
      pass
    #print result
    return result
    

class XMLValidator():
  """
  This class is responsible of validate a XML string vs an XMLSchema.
  
  @author: Alfredo Herrejon
  """
  
  def __init__(self, xml_etree=None, invoice_type='I', version = '3.2'):
    import pdb; pdb.set_trace()
    self.xml_string = self.remove_addenda(xml_etree)
    self.namespace = XML_INVOICE_NAMESPACE
    if version == '3.2':
      self.XSD_PARSER = settings.XSD_PARSER_32
    elif version == '3.3':
      self.XSD_PARSER = settings.XSD_PARSER_33
  
  def remove_addenda(self, xml_etree=None):
    to_remove = None
    try:
      to_remove = xml_etree.find(self.namespace % "Addenda")
    except:      
      pass
    if to_remove is not None:      
      xml_etree.remove(to_remove)    
    self.addenda = to_remove
    invoice_utf = etree.tostring(xml_etree, encoding='UTF-8')
    return invoice_utf
      
  def is_valid(self):
    import pdb; pdb.set_trace()
    success = False
    message = "The XML invoice document is valid in the version XSD %s" % XML_XSD_CFDI_VERSION
    try:
      root = etree.fromstring(self.xml_string, self.XSD_PARSER)
      success = True
    except Exception as e:
      message = str(e)
      success = False
    data = {
      'addenda' : self.addenda,
      'success' : success,
      'message' : message
    }
    
    return data 



class AmountValidator():
  """
  This class is responsible of validate the amounts in the XML.
  
  @author: Alfredo Herrejon
  """
  
  def __init__(self, xml_etree=None):

    self.valid = True
    self.xml_etree = xml_etree
    self.subtotal = float(xml_etree.get('subTotal'))
    self.total = float(xml_etree.get('total'))
    try:
      self.totalImpuestosTraslados = float(xml_etree.xpath('sum(.//cfdi:Impuestos/@totalImpuestosTrasladados)', namespaces=NSMAP_CFDI32))
      self.totalImpuestosRetenidos = float(xml_etree.xpath('sum(.//cfdi:Impuestos/@totalImpuestosRetenidos)', namespaces=NSMAP_CFDI32))
      self.check_concepts()
      if self.valid:
        if abs(self.subtotal-self.total_concepts) > 0.01:
          self.valid = False
          self.error = "Los Conceptos y el SubTotal no Concuerdan"
      else:
        self.check_taxes()
        if self.valid:
          self.check_complements()

    except (Exception, e):
      self.valid = False

  def check_concepts(self):
    
    self.total_concepts = 0.0
    self.concepts_node = self.xml_etree.findall('.//cfdi:Conceptos/cfdi:Concepto', namespaces=NSMAP_CFDI32)
    for concept in self.concepts_node:
      quantity = float(concept.get('cantidad'))
      unit_price = float(concept.get('valorUnitario'))
      amount = float(concept.get('importe'))
      if abs(amount - total) > 0.01:
        self.valid = False
        desc = concepto.get('descripcion')
        self.error = "Las cantidades en el concepto %s no concuerdan %s <> %s" % (description, str(total), str(amount))
        break
      else:
        self.total_concepts += amount

  def check_taxes(self):   
    #@ TODO: copy method
    pass

  def check_complements(self):   
    #@ TODO: copy method
    pass

class SendNotification(object):
  def __init__(self, invoice):
    if not invoice:
      raise('Empty Invoice')
    self.provider = invoice.provider
    self.account = invoice.account
    
class SatValidator(object):
  
  def __init__(self, parameter):
    self.parameter = parameter
    self.ws_sat = settings.SAT_CONSULTA_URL
    self.message = ''
    self.valid = False

  def get_status(self):

    try:

      if settings.DEBUG:
        self.valid = True
        return

      client = Client(self.ws_sat, cache=None, location=self.ws_sat)
      response = client.service.Consulta(self.parameter)
      if not response.Estado in ['Vigente','No Encontrado','Cancelado']:
        self.message = response.Estado
        return
      elif response.Estado == 'No Encontrado':
        self.message = 'El comprobante no se encontro en el SAT.'
        self.pending_validate = True      
        return
      elif response.Estado == 'Cancelado.':
        self.message = 'El comprobante se encuentra cancelado'
        return
      self.valid = True
    except (Exception, e):
      self.message = 'El proceso termino inesperadamente.'
      self.pending_validate = True

  def is_valid(self):
    self.get_status()

    return {
      'success': self.valid,
      'message': self.message,
      'pending_validate': self.pending_validate,
    }


def etree_to_dict(t):
  try:
    tag = t.tag.replace('{http://www.sat.gob.mx/cfd/3}', '')
    tag = tag.replace('{http://www.sat.gob.mx/TimbreFiscalDigital}', '')
  except:
    tag.tag
  d = {tag: {} if t.attrib else None}
  children = list(t)
  if children:
    dd = defaultdict(list)
    for dc in map(etree_to_dict, children):
      for k, v in dc.iteritems():
        dd[k].append(v)
    d = {tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
  if t.attrib:
    d[tag].update((k, v) for k, v in t.attrib.iteritems())
  if t.text:
    text = t.text.strip()
    if children or t.attrib:
      if text:
        d[tag]['text'] = text
    else:
      d[tag] = text
  return d


################################CREATE PDF##############################
linux = False
windows = False

LOCALDEV = True

oSys = sys.platform
if oSys == 'linux2':
  linux = True
elif oSys in ('win32', 'win64'):
  windows = True



#bg_color = colors.Color(red=(0.401), green=(0.172), blue=(0.160))
bg_color = colors.Color(red=(0.070), green=(0.254), blue=(0.431))

style = getSampleStyleSheet()
basic_center = ParagraphStyle('Caption', fontSize=6, alignment=TA_CENTER, leading=9, spaceAfter=0, spaceBefore=0)
basic_left = ParagraphStyle('Caption', fontSize=6, alignment=TA_LEFT, leading=8, spaceAfter=0, spaceBefore=0)
basic_left_justify = ParagraphStyle('Caption', fontSize=6, alignment=TA_JUSTIFY, leading=8, spaceAfter=0, spaceBefore=0)
basic_left_justify_2 = ParagraphStyle('Caption', fontSize=4.5, alignment=TA_JUSTIFY, leading=8, spaceAfter=0, spaceBefore=0)
total_style = ParagraphStyle('Caption', fontSize=8.5, alignment=TA_RIGHT, leading=10.5, spaceAfter=0, spaceBefore=0)
_8_right = ParagraphStyle('Caption', fontSize=7, alignment=TA_RIGHT, leading=9, spaceAfter=0, spaceBefore=0)
_8_center = ParagraphStyle('Caption', fontSize=7, alignment=TA_CENTER, leading=9, spaceAfter=0, spaceBefore=0)
_8_left = ParagraphStyle('Caption', fontSize=7, alignment=TA_LEFT, leading=9, spaceAfter=0, spaceBefore=0)
_9_center = ParagraphStyle('Caption', fontSize=8, alignment=TA_CENTER, leading=10, spaceAfter=0, spaceBefore=0)
_9_right = ParagraphStyle('Caption', fontSize=8, alignment=TA_RIGHT, leading=10, spaceAfter=0, spaceBefore=0)
_9_left = ParagraphStyle('Caption', fontSize=8, alignment=TA_LEFT, leading=10, spaceAfter=0, spaceBefore=0)
basic_right = ParagraphStyle('Caption', fontSize=6, alignment=TA_RIGHT, leading=8, spaceAfter=0, spaceBefore=0)
title_style = ParagraphStyle('Caption', fontSize=8, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_RIGHT)
folio_style = ParagraphStyle('Caption', fontSize=9, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_RIGHT, textColor='red')
style_white_10 = ParagraphStyle('Caption', fontSize=9, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_CENTER, textColor='white')
style_white = ParagraphStyle('Caption', fontSize=7, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_CENTER, textColor="white")
taxpayer_name = ParagraphStyle('Caption', fontSize=9, leading=12, spaceAfter=0, spaceBefore=0, alignment=TA_CENTER, textColor=bg_color)
titles_tfd = ParagraphStyle('Caption', fontSize=9, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_LEFT)
s = Paragraph('', basic_center)

##########################################################################################################################################

if linux:
  PATH_QR = "/tmp/"
elif windows:
  PATH_QR = "%s\\" % os.environ['tmp']

class CreatePDF(object):

  def __init__(self, xml_path, filename, business_number):
    xml_file = open(xml_path, 'r')
    xml_string = xml_file.read()
    xml_file.close()
    self.success = False
    self.filename = filename
    self.business_number = business_number
    
    try:
      xml_parser = etree.XMLParser(remove_blank_text=True)
      try:
        try:
          xml_encoded = xml_string.encode('utf-8')
        except:
          xml_encoded = xml_string.decode('utf-8')
        xml_etree = etree.XML(xml_encoded.encode('utf-8'), parser=xml_parser)
      except:
        xml_etree = etree.XML(xml_string, parser=xml_parser)
      
      try: 
        self.version = xml_etree.get('Version')
        self.version_ = self.version[0]
        n_comp = xml_etree.xpath('//cfdi:Comprobante', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/{}'.format(self.version_)})[0]
        self.folio = n_comp.get('Folio') if n_comp.get('Folio') else ''
        self.serie = n_comp.get('Serie') if n_comp.get('Serie') else ''
        self.date = n_comp.get('Fecha')
        self.currency = n_comp.get('Moneda')
        self.serial_cfdi = n_comp.get('NoCertificado')
        self.expedition_place = n_comp.get('LugarExpedicion') 
        self.pay_method = METODO_PAGO[n_comp.get('MetodoPago')] if n_comp.get('MetodoPago') else ''
        self.way_payment = FOR_PA[n_comp.get('FormaPago')] if n_comp.get('FormaPago') else ''
        #self.descuentos = n_comp.get('Descuento') if n_comp.get('Descuento') else '0.00'
        self.exchange_rate = n_comp.get('TipoCambio') if n_comp.get('TipoCambio') else '1'
        self.invoice_type = n_comp.get('TipoDeComprobante')
        self.total = n_comp.get('Total')
        self.amount_in_writting = ''
        try:
          self.amount_in_writting = numero_a_letras(float(self.total))
        except:
          pass
        self.sub_total = n_comp.get('SubTotal')
        self.payment_terms = n_comp.get('CondicionesDePago') if n_comp.get('CondicionesDePago') else ''
      except Exception as e:
        print ("Exception get node Comprobante => %s" % str(e))
        raise Exception(e)
      
      # Emisor
      try:
        n_emisor = xml_etree.find('cfdi:Emisor', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/{}'.format(self.version_)})   
        self.taxpayer_id = n_emisor.get('Rfc')
        self.business_obj = Business.objects.get(taxpayer_id=self.taxpayer_id)
        self.name = self.business_obj.name
        self.regimen = REG_FIS[n_emisor.get('RegimenFiscal')]
      except Exception as e:
        print ("Exception get node Emisor => %s" % str(e))
        raise Exception(e)

      # Receptor
      try: 
        n_receptor = xml_etree.find('cfdi:Receptor', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/{}'.format(self.version_)})
        self.rtaxpayer_id =  n_receptor.get('Rfc')
        self.rname = n_receptor.get('Nombre')
        self.uso_cfdi = n_receptor.get('UsoCFDI')
        self.domicilio_fiscal_receptor = n_receptor.get('DomicilioFiscalReceptor')
        self.regimen_fiscal_receptor = n_receptor.get('RegimenFiscalReceptor')
      except Exception as e:
        print ("Exception get node Receptor => %s" % str(e))
        raise Exception(e)
      
      # Conceptos
      try:
        self.conceptos = xml_etree.find('cfdi:Conceptos/cfdi:Concepto', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/{}'.format(self.version_)})
        self.c_clave_prodserv = self.conceptos.get('ClaveProdServ', '')
        self.c_cantidad = self.conceptos.get('Cantidad', '')
        self.c_cveunidad = self.conceptos.get('ClaveUnidad', '')
        self.c_descripcion = self.conceptos.get('Descripcion', '')
        self.v_unitario = self.conceptos.get('ValorUnitario', '0.00')
        self.c_importe = self.conceptos.get('Importe', '0.00')
        self.c_descuento = self.conceptos.get('Descuento', '0.00')
      except:
        self.conceptos = None
        print( "Exception get node Conceptos => %s" % str(e) )  
        raise Exception(e)

      # total impuestos trasladados
      try:
        self.total_tra = xml_etree.xpath('//cfdi:Comprobante/cfdi:Impuestos/@TotalImpuestosTrasladados', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/{}'.format(self.version_)})[0]
      except:
        self.total_tra = '0.00'
      
      # total impuestos retenidos
      try:
        self.total_ret = xml_etree.xpath('//cfdi:Comprobante/cfdi:Impuestos/@TotalImpuestosRetenidos', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/{}'.format(self.version_)})[0]
      except:
        self.total_ret = '0.00'

      try:
        n_nomina = xml_etree.xpath('//tmp:Nomina', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
        self.tot_ded = n_nomina.get('TotalDeducciones')
        self.tot_per = n_nomina.get('TotalPercepciones')
        self.tot_otpa = n_nomina.get('TotalOtrosPagos')
        self.paid_date = n_nomina.get('FechaPago') 
        self.fe_exped = n_nomina.get('FechaFinalPago')
        self.paid_days = n_nomina.get('NumDiasPagados')
        paid_from = n_nomina.get('FechaInicialPago')
        paid_from_2 = datetime.strptime(paid_from, '%Y-%m-%d').strftime('%d/%b/%Y').upper()
        
        # NODO RECEPTOR NOMINA#
        self.inicio_relaboral = ''
        if self.business_number in ('4469', '4473', '4470', '4472', '4225', '4242'):
          n_receptor = n_nomina.xpath('.//tmp:Receptor', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
          inicio_relaboral = n_receptor.get('FechaInicioRelLaboral')
          if inicio_relaboral:
            str_date = datetime.strptime(inicio_relaboral, '%Y-%m-%d')
            month = FORMATO_FECHAS[str_date.month]
            self.inicio_relaboral = '{}/{}/{}'.format("{:02d}".format(str_date.day), month, str_date.year).upper()
            self.inicio_relaboral = '<b>Inicio relacion laboral: </b>%s' % self.inicio_relaboral
        paid_to = n_nomina.get('FechaFinalPago')
        paid_to_2 = datetime.strptime(paid_to, '%Y-%m-%d').strftime('%d/%b/%Y').upper()
        
        self.period = "%s al %s" % (paid_from_2, paid_to_2)

        # Emisor Nomina
        self.employer_regist = xml_etree.xpath('string(//tmp:Emisor/@RegistroPatronal)', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})
        

        # Receptor Nomina
        n_receptor = xml_etree.xpath('//tmp:Receptor', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
        self.emp_num = n_receptor.get('NumEmpleado')
        self.curp = n_receptor.get('Curp')
        self.imss = n_receptor.get('NumSeguridadSocial','')
        self.depart = n_receptor.get('Departamento','').split('-')[0]
        self.posit = n_receptor.get('Puesto','')
        self.s_diario = n_receptor.get('SalarioDiarioIntegrado')
        self.ss_no = n_receptor.get('NumSeguridadSocial','')
        self.emp_regimen = n_receptor.get('TipoRegimen')
        self.clave_entfed = n_receptor.get('ClaveEntFed')

        # Deducciones
        if len(xml_etree.xpath('//tmp:Deducciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          self.deducciones = xml_etree.xpath('//tmp:Deducciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
          self.tot_isr = self.deducciones.get('TotalImpuestosRetenidos') if self.deducciones.get('TotalImpuestosRetenidos') else '0.00'
          self.tot_ded = self.deducciones.get('TotalOtrasDeducciones') if self.deducciones.get('TotalOtrasDeducciones') else '0.00'
        else:
          self.deducciones = []
          self.tot_isr = '0.00'
          self.tot_ded = '0.00'
        
        # Percepciones
        if len(xml_etree.xpath('//tmp:Percepciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          self.percepciones = xml_etree.xpath('//tmp:Percepcion', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})
        else:
          self.percepciones = []
        
        # OtrosPagos
        self.otros_p = False
        if len(xml_etree.xpath('//tmp:OtrosPagos', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          try:
            self.n_otros_pago = xml_etree.xpath('//tmp:OtrosPagos', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
            self.otros_p = True
          except:
            self.otros_p = False
            pass
        else:
          pass
        
        # Incapacidades
        if len(xml_etree.xpath('//tmp:Incapacidades', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          #set_trace()
          self.n_incapacidades = []
          self.nodos_incapacidades = xml_etree.xpath('//tmp:Incapacidades', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})
          
          for nodo_inc in self.nodos_incapacidades:
            for inc in nodo_inc:
              self.n_incapacidades.append(inc)
          self.incapacidades = True
        else:
          self.incapacidades = False
          pass
      except (Exception, e):
        print ("Exception Datos de Nómina => %s" % str(e))
        self.message = "Exception Datos de Nómina => %s" % str(e)
        return

      self.horas_extra_etree = xml_etree.xpath(
        './/tmp:Nomina/tmp:Percepciones/tmp:Percepcion/tmp:HorasExtra',
        namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})
      self.horas_extra_exists = bool(self.horas_extra_etree)
      
      # TFD
      try: 
        n_tfd = xml_etree.xpath('//tfd:TimbreFiscalDigital', namespaces={'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
        self.uuid = n_tfd.get('UUID')
        self.seal_cfd = n_tfd.get('SelloCFD')
        self.seal_sat = n_tfd.get('SelloSAT')
        self.serial_sat = n_tfd.get('NoCertificadoSAT')
        self.date_cert = n_tfd.get('FechaTimbrado')
        self.original_string_tfd = '||1.1|%s|%s|%s|%s||' % (self.uuid, self.date_cert, self.seal_cfd, self.serial_sat)
      except Exception as e:
        print ("Exception get node TFD => %s" % str(e))
        raise Exception(e)
     
      account = Business.objects.get(taxpayer_id=self.taxpayer_id)
      self.taxpayer_address = u"<b>Dirección:</b> %s <br/><b>RFC:</b> %s <b>Régimen Fiscal:</b> %s <br/> <b>Registro Patronal:</b> %s  <b>Efecto del Comprobante: </b> Nómina<b>  Versión: </b> %s" % (account.address, self.taxpayer_id, self.regimen, self.employer_regist, self.version) #Registro Patronal: %s</b> self.registro_patronal
      self.signature_legend = u"""RECIBÍ DE CONFORMIDAD EL 'CFDI' EMITIDO POR "%s", CORRESPONDIENTE A LA FECHA QUE EN EL SE INDICA, POR LA CANTIDAD INDICADA QUE CUBRE EL IMPORTE DE MI SALARIO, SÉPTIMO DÍA Y TODAS LAS PERCEPCIONES Y PRESTACIONES A LAS QUE TENGO DERECHO SIN QUE SE ME ADEUDE CANTIDAD ALGUNA POR CUALQUIER OTRO CONCEPTO. PARA LOS EFECTOS DE LOS ART. 27 FRAC. V, EN CUMPLIMIENTO DEL ART. 99 FRAC. III DE LA LISR Y ART. 29 FRAC. 29 V DEL CFF, LOS ACUSES DE RECIBO SON POR CONDUCTO DE LA PÁGINA DE INTERNET WWW.PAE.CC""" % self.name
      self.success = self.tables_builder()
    except Exception as e:
      print ("Exeption Constructor | %s" % str(e))

  def createqr(self):
    try:
      import qrcode
       
      qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=0,
      )
      total = self.total.rstrip('+-0').lstrip('+-0')
      total = total.rstrip('.')
      seal = self.seal_cfd[-8:]
      qr.add_data("https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id=%s&re=%s&rr=%s&tt=%s&fe=%s" % (self.uuid, self.taxpayer_id, self.rtaxpayer_id, total, seal))

      qr.make(fit=True)
      img = qr.make_image()
      f = open('%s/%s.png' % (PATH_QR, self.uuid), "wb")
      img.save(f)
      img.close()
      f.close()
    except Exception as e:
      print ("Error al crear el CodigoQR => %s" % str(e))

  
  def settings(self, canvas, doc):
    try: 
      canvas.saveState()
      canvas.setFont('Helvetica-Bold', 6.5)
      #~ Set PDF Properties
      canvas.setTitle('Recibo de Nómina')
      canvas.setSubject('Recibo de Nómina')
      canvas.setAuthor('CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V')
      canvas.setKeywords(['CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V', 'CFDI 3.3', 'Nómina 1.2', 'SAT'])
      canvas.setCreator('CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V')
      #~ Draw table with canvas
      self.header(canvas)
      canvas.restoreState()
    except Exception as e:
      print ("Exception header() =>  %s" % str(e))
      self.message = "Exception header() =>  %s" % str(e)

  def tables_builder(self):
    try:
      success = False
      story=[]
      if self.version == '4.0':
        story.append(Spacer(0,15))  
      table_concepts_comp = self.concepts_comprobante()
      story.append(table_concepts_comp)
      story.append(Spacer(0,4))
      table_concepts = self.concepts()
      story.append(table_concepts)
      story.append(Spacer(0,6))
      try:
        table_otros_pagos_n = self.otros_pagos_n()
        story.append(table_otros_pagos_n)
      except:
        pass
      if self.horas_extra_exists:
        story.append(Spacer(0,6))
        table_horas_extra = self.horas_extra()
        story.append(table_horas_extra)

      story.append(Spacer(0,9))
      table_totales = self.totales()
      story.append(table_totales)
      story.append(Spacer(0,1))
      table_signature = self.employe_signature()
      story.append(table_signature)
      story.append(Spacer(0,5))
      table_tfd_data = self.tfd_data()
      story.append(table_tfd_data)
      story.append(Spacer(0,4))
      table_tfd = self.tfd_seals()
      story.append(table_tfd)
      #import pdb; pdb.set_trace()
      frame = Frame(inch, 95, 465, 545)
      header = PageTemplate(id='header', frames=frame, onPage=self.settings)
      #PDF_PATH = settings.INVOICE_STORAGE
      PDF_PATH = '/tmp'
      self.path_pdf_ = '{}/{}.pdf'.format(PDF_PATH,  self.filename.replace(".txt", "").replace(".xml", ""))
      self.doc = BaseDocTemplate('%s/%s.pdf' % (PDF_PATH, self.filename.replace(".txt", "").replace(".xml", "")), pageTemplates=[header], pagesize=letter)
      try:
        self.doc.build(story, canvasmaker=NumberedCanvas)
      except:
        self.doc.build(story, canvasmaker=NumberedCanvas)
      success = True
    except Exception as e:
      print ("Exception tables_builder() | %s" % str(e))
    return success

  def header(self, canvas):
    try:
     
      # Emisor ================================================================================
      try:
        #from pdb import set_trace; set_trace()
        logo = ''
        
        account = Business.objects.get(taxpayer_id=self.taxpayer_id)
        
        logo_path = account.logo.path if account.logo else None #static('img/nomina.png')
        if logo_path:
          img=im.open(logo_path)
          if img.size[0] > img.size[1]:
            logo = Image(logo_path, width=1.5*inch, height=0.7*inch)
          else:
            logo = Image(logo_path, width=1*inch, height=1*inch)
          logo.hAlign = 'CENTER'
      except Exception as e:
        print ('Error al obtener el LOGO para el PDFF ==> {}'.format(str(e)))

      emisor_data = [
              [Paragraph("<b>Recibo de Nómina</b>", style_white_10), Paragraph('<b>%s</b>' % self.name, taxpayer_name)],
              [logo, Paragraph(self.taxpayer_address, title_style)],
          ]

      if self.version == '4.0':
        emisor_data = emisor_data + [[s, s]]

      table_emisor = Table(emisor_data, colWidths=[4*cm, 15.05*cm], style=[
              # ('GRID', (0,0), (-1,-1), 1, colors.gray),
              ('VALIGN', (0,0), (-1,-1), "MIDDLE"),
              ('BACKGROUND', (0,0), (0,0), bg_color),
              ('TOPPADDING', (0,0), (-1,-1), 2.5), 
              ('BOTTOMPADDING', (0,0), (-1,-1), 2.5), 
              ('BOTTOMPADDING', (-1,0), (-1,0), 5), 
      ])

      if self.version == '4.0':
        table_emisor.wrapOn(canvas, 1.2*cm, 25.6*cm)
        table_emisor.drawOn(canvas, 1.2*cm, 24.6*cm)
      else:
        table_emisor.wrapOn(canvas, 1.2*cm, 26.5*cm)
        table_emisor.drawOn(canvas, 1.2*cm, 25.0*cm)
        
      # Emisor END ================================================================================
      
      # Receptor ================================================================================
      receiver_data = [
              [Paragraph('<b>RECEPTOR</b>', style_white), s],
              [Paragraph('<b>No. Empleado: </b>%s' % self.emp_num, _8_left), Paragraph('<b>Depto.: </b>%s' % self.depart, _8_left)],
              [Paragraph('<b>Nombre: </b>%s' % self.rname, _8_left), Paragraph('<b>Puesto: </b>%s' % self.posit, _8_left)],
              [Paragraph('<b>CURP: </b>%s' % self.curp, _8_left), Paragraph('<b>Periodo del: </b>%s' % self.period, _8_left)],
              [Paragraph('<b>RFC: </b>%s' % self.rtaxpayer_id, _8_left), Paragraph('<b>Días pagados: </b>%s' % self.paid_days, _8_left)],
              [Paragraph('<b>No. Seguridad Social: </b>%s' % self.ss_no, _8_left), Paragraph('<b>Régimen del trabajador: </b>%s' % self.emp_regimen, _8_left)],
              [Paragraph(self.inicio_relaboral, _8_left),s],
              [Paragraph('<b>Clave Entidad Federativa: </b>%s' % self.clave_entfed, _8_left), Paragraph('<b>Uso de CFDI: </b>%s' % self.uso_cfdi, _8_left)],
              # [Paragraph('<b>Código Postal: </b>%s' % self.clave_entfed, _8_left), ''],
      ]

      if self.version == '4.0':
        receiver_data = receiver_data + [
          [Paragraph('<b>Domicilio Fiscal: </b>%s' % self.domicilio_fiscal_receptor, _8_left), Paragraph('<b>Régimen fiscal: </b>%s' % self.regimen_fiscal_receptor, _8_left)]
        ]

      table_receiver = Table(receiver_data, colWidths=[9.55*cm, 9.5*cm], style=[
              #('GRID', (0,0),(-1,-1), 1, colors.gray),
              ('BACKGROUND', (0,0),(-1,0), bg_color),
              ('TOPPADDING', (0,0),(-1,-1), 0.5),
              ('BOTTOMPADDING', (0,0),(-1,-1), 0.5),
              ('SPAN', (0,0),(-1,0)),
              ('VALIGN', (0,1),(-1,-1), 'TOP'),
        ])

      if self.version == '4.0':
        table_receiver.wrapOn(canvas, 1.2*cm, 21.9*cm)
        table_receiver.drawOn(canvas, 1.2*cm, 21.9*cm)
      else:
        table_receiver.wrapOn(canvas, 1.2*cm, 22.5*cm)
        table_receiver.drawOn(canvas, 1.2*cm, 22.3*cm)
      # Receptor ================================================================================
      
    except Exception as e:
      print ("Exception header() => %s" % str(e))

  def concepts_comprobante(self):
    try:

      concept_data = [
        [Paragraph('<b>CONCEPTO</b>', style_white), s, s, s, s, s, s],
        [Paragraph('<b>ClaveProdSev</b>', basic_center), Paragraph('<b>Cantidad</b>', basic_center), Paragraph('<b>Clave Unidad</b>', basic_center), Paragraph('<b>Descripción</b>', basic_center), Paragraph('<b>ValorUnitario</b>', basic_center), Paragraph('<b>Importe</b>', basic_center), Paragraph('<b>Descuento</b>', basic_center)],
        [Paragraph('%s' % self.c_clave_prodserv, basic_center), Paragraph('%s' % self.c_cantidad, basic_center), Paragraph('%s' % self.c_cveunidad, basic_center), Paragraph('%s' % self.c_descripcion, basic_center), Paragraph('%s' % self.v_unitario, basic_center), Paragraph('%s' % self.c_importe, basic_center), Paragraph('%s' % self.c_descuento, basic_center)],
      ]
      
      #set_trace()
      table_concepts=Table(concept_data, colWidths=[2.2*cm, 2.0*cm, 2.0*cm, 6*cm, 2.0*cm, 2.5*cm, 2.5*cm, 2.5*cm], repeatRows=2, style=[
        ('GRID', (0,0),(-1,-1), 1, colors.white),
        ('BACKGROUND', (0,0),(6,0), bg_color),
        #('BACKGROUND', (0,1),(6,1), bg_color),
        ('SPAN', (0,0),(6,0)), # CABECERA
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('VALIGN', (0,0),(-1,-1), 'TOP'),
        ('RIGHTPADDING', (0,0),(-1,-1), 2.5),
        ('LEFTPADDING', (0,0),(-1,-1), 2.5),
        ('TOPPADDING', (0,0),(-1,-1), 0.5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 0.5),
        ('BOTTOMPADDING', (0,1),(-1,1), 2),
        ('LINEBELOW',(0,1),(6,1), 1, bg_color), # Draw a line below headers PERCEPCIONES
       
      ])

    except Exception as e:
      print ("Exception concepts_comprobante() | %s" % str(e))
    return table_concepts

  def concepts(self):
    try:

      per_ded_data = [
        [Paragraph('<b>PERCEPCIONES</b>', style_white), s, s, s, Paragraph('<b>DEDUCCIONES</b>', style_white), s, s],
        [Paragraph('<b>Clave</b>', basic_center), Paragraph('<b>Descripción</b>', basic_left), Paragraph('<b>Importe</b>', basic_right), s, Paragraph('<b>Clave</b>', basic_center), Paragraph('<b>Descripción</b>', basic_left), Paragraph('<b>Importe</b>', basic_right)],
      ]
      
      #set_trace()
      if len(self.percepciones) >= len(self.deducciones):
        pos = 0
        for percepcion in self.percepciones:
          clave_ded = ''
          concepto_ded = ''
          importe_ded = ''

          try:
            clave_ded = self.deducciones[pos].get('Clave')
          except:
            pass
          
          try:
            concepto_ded = self.deducciones[pos].get('Concepto')
          except:
            pass
          
          try:
            importe_ded = self.deducciones[pos].get('Importe')
            importe_ded = self.truncate(Decimal(importe_ded), 2)
          except:
            pass

          per_ded_data.append(
            [
              Paragraph(percepcion.get('Clave'), basic_center),
              Paragraph(percepcion.get('Concepto'), basic_left),
              Paragraph(self.truncate(Decimal('%.2f' % (float(percepcion.get('ImporteExento')) + float(percepcion.get('ImporteGravado')))), 2), basic_right), 
              s, Paragraph(clave_ded, basic_center), Paragraph(concepto_ded, basic_left),
              Paragraph(importe_ded, basic_right)]
          ),
          pos += 1
      elif  len(self.percepciones) < len(self.deducciones):
        pos = 0
        for deduccion in self.deducciones:
          clave_per = ''
          concepto_per = ''
          importe_per = ''

          try:
            clave_per = self.percepciones[pos].get('Clave')
          except:
            pass
          
          try:
            concepto_per = self.percepciones[pos].get('Concepto')
          except:
            pass
          
          try:
            importe_per = '%.2f' % (float(self.percepciones[pos].get('ImporteGravado')) + float(self.percepciones[pos].get('ImporteExento')))
            importe_per = self.truncate(Decimal(importe_per), 2)
          except:
            pass

          per_ded_data.append([Paragraph(clave_per, basic_center), Paragraph(concepto_per, basic_left), Paragraph(importe_per, basic_right), s, Paragraph(deduccion.get('Clave'), basic_center), Paragraph(deduccion.get('Concepto'), basic_left), Paragraph(self.truncate(Decimal('%.2f' % float(deduccion.get('Importe'))), 2), basic_right)]),
          pos += 1
      
      table_per_ded=Table(per_ded_data, colWidths=[1.2*cm, 6*cm, 2.1*cm, 0.45*cm, 1.2*cm, 6*cm, 2.1*cm], repeatRows=2, style=[
        #('GRID', (0,0),(-1,-1), 1, colors.black),
        #('BOX', (0,0),(-1,-1), 1, bg_color),
        ('BACKGROUND', (0,0),(2,0), bg_color),
        ('BACKGROUND', (4,0),(-1,0), bg_color),
        ('SPAN', (0,0),(2,0)), # PERCEPCIONES
        ('SPAN', (4,0),(-1,0)), # DEDUCCIONES
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('VALIGN', (0,2),(-1,-1), 'TOP'),
        ('RIGHTPADDING', (0,0),(-1,-1), 2.5),
        ('LEFTPADDING', (0,0),(-1,-1), 2.5),
        ('TOPPADDING', (0,0),(-1,-1), 0.0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 0.0),
        # ('BOTTOMPADDING', (0,1),(-1,1), 0.5),
        ('LINEBELOW',(0,1),(2,1), 1, bg_color), # Draw a line below headers PERCEPCIONES
        ('LINEBELOW',(4,1),(-1,1), 1, bg_color), # Draw a line below headers DEDUCCIONES
        ('LINEBELOW',(0,-1),(2,-1), 1, bg_color), # Draw a line after last row PERCEPCIONES
        ('LINEBELOW',(4,-1),(-1,-1), 1, bg_color), # Draw a line after last row DEDUCCIONES
        ('LINEBELOW',(0,"splitlast"),(2,"splitlast"), 1, bg_color),
        ('LINEBELOW',(4,"splitlast"),(-1,"splitlast"), 1, bg_color),
        # ('BOTTOMPADDING',(0,-1),(-1,-1), 0.5),
        #('LINEBELOW',(0,"splitlast"),(-1,"splitlast"), 1, colors.gray),
      ])

    except Exception as e:
      print ("Exception concepts() | %s" % str(e))
    return table_per_ded

  def otros_pagos_n(self):
    try:
      if self.otros_p:
        otros_pagos_data = [
          [Paragraph('<b>OTROS PAGOS</b>', style_white), s, s, s],
          [Paragraph('<b>Tipo otro pago</b>', basic_center), Paragraph('<b>Clave</b>', basic_center), Paragraph('<b>Concepto</b>', basic_center), Paragraph('<b>Importe</b>', basic_center)],
          ]
        for otro_pago in self.n_otros_pago:
          tipo_otro_pago = otro_pago.get('TipoOtroPago', '')
          clave = otro_pago.get('Clave', '')
          concepto = otro_pago.get('Concepto', '0.00')
          importe = otro_pago.get('Importe', '0.00')

          otros_pagos_data.append([Paragraph(tipo_otro_pago, basic_center), Paragraph(clave, basic_center), Paragraph(concepto, basic_center), Paragraph(importe, basic_center)])

        table_otros_pagos_n=Table(otros_pagos_data, colWidths=[2.2*cm, 2.0*cm, 12.0*cm, 3.0*cm], repeatRows=2, style=[
          ('BACKGROUND', (0,0),(3,0), bg_color),
          ('SPAN', (0,0),(3,0)), # CABECERA
          ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
          ('VALIGN', (0,0),(-1,-1), 'TOP'),
          ('RIGHTPADDING', (0,0),(-1,-1), 2.5),
          ('LEFTPADDING', (0,0),(-1,-1), 2.5),
          ('TOPPADDING', (0,0),(-1,-1), 0.5),
          ('BOTTOMPADDING', (0,0),(-1,-1), 0.5),
          ('LINEBELOW',(0,1),(3,1), 1, bg_color), # Draw a line below headers PERCEPCIONES

          
        ])
    except Exception as e:
      print ("Exception otros_pagos() | %s" % str(e))
    return table_otros_pagos_n

  def horas_extra(self):
    table_horas_extra = []
    try:
      if self.horas_extra_exists:
        table_horas_extra_data = [
          [Paragraph('<b>HORAS EXTRAS</b>', style_white), s, s, s],
          [Paragraph('<b>Dias</b>', basic_center), Paragraph('<b>Tipo horas</b>', basic_center), Paragraph('<b>Horas Extra </b>', basic_center), Paragraph('<b>Importe pagado</b>', basic_center)],
        ]

        for hora_extra_etree in self.horas_extra_etree:
          table_horas_extra_data.append(
            [
              Paragraph(hora_extra_etree.get("Dias", ""), basic_center),
              Paragraph(CATALOGO_TIPOHORAS[hora_extra_etree.get("TipoHoras")], basic_center),
              Paragraph('{} Hrs.'.format(hora_extra_etree.get("HorasExtra")), basic_center),
              Paragraph(hora_extra_etree.get("ImportePagado"), basic_center)
            ]
          )

        table_horas_extra=Table(table_horas_extra_data, colWidths=[2.2*cm, 2.0*cm, 12.0*cm, 3.0*cm], repeatRows=2, style=[
          ('BACKGROUND', (0,0),(3,0), bg_color),
          ('SPAN', (0,0),(3,0)), # CABECERA
          ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
          ('VALIGN', (0,0),(-1,-1), 'TOP'),
          ('RIGHTPADDING', (0,0),(-1,-1), 2.5),
          ('LEFTPADDING', (0,0),(-1,-1), 2.5),
          ('TOPPADDING', (0,0),(-1,-1), 0.5),
          ('BOTTOMPADDING', (0,0),(-1,-1), 0.5),
          ('LINEBELOW',(0,1),(3,1), 1, bg_color), # Draw a line below headers PERCEPCIONES
        ])

    except Exception as e:
      print ("Exception horas_extra() | %s" % str(e))
    return table_horas_extra

  def totales(self):
    try:

      total_per_ = 0.00
      if self.sub_total is not None:
        total_per_ = self.truncate(Decimal(self.sub_total), 2)

      total_ded_ = 0.00
      if self.tot_ded is not None:
        total_ded_ = self.truncate(Decimal(self.tot_ded), 2)

      isr_retenido = 0.0
      if self.tot_isr is not None:
        isr_retenido = self.truncate(Decimal(self.tot_isr), 2)
      
      total_otpa = 0.00
      if self.tot_otpa is not None:
        total_otpa = self.truncate(Decimal(self.tot_otpa), 2)

      if self.version == '3.3':
        way_payment_ = Paragraph('<b>Forma de pago: </b>%s' % self.way_payment, _8_left)
      elif self.version == '4.0':
        way_payment_ = Paragraph('', _8_left)

      total_data = [
            [way_payment_, Paragraph('<b>Total Percepciones</b>', _8_right), Paragraph('%s' % total_per_, _8_right)],
            [Paragraph(u'<b>Método de pago: </b>%s' % self.pay_method, _8_left), Paragraph('<b>Total deducciones sin ISR</b>', _8_right), Paragraph('- %s' % total_ded_, _8_right)],
            [s, Paragraph('<b>Total Otros Pagos</b>', _8_right), Paragraph('%s' % total_otpa, _8_right)],
            [Paragraph('<b>Total con letra:</b>', _9_left), Paragraph('<b>ISR Retenido</b>', _8_right), Paragraph('- %s' % isr_retenido, _8_right)],
            [Paragraph(self.amount_in_writting, _8_left), Paragraph('<b>Total</b>', total_style), Paragraph('$ %s' % self.truncate(Decimal(self.total), 2), total_style)],
        ]

      table_totales = Table(total_data, colWidths=[12.05*cm, 4*cm, 3*cm ], style=[
        #('GRID', (0,0), (-1, -1), 1, colors.gray),
        ('LINEBELOW', (1,3),(-1,3), 1, bg_color),
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('VALIGN', (1,2),(-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0),(0,0), 0.3),
        ('TOPPADDING', (0,1),(-1,-1), 0.2),
        ('LEFTPADDING', (0,0),(0,-1), 0),
        ('RIGHTPADDING', (-2,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,1),(-1,-1), 0.2),
      ])
    
    except Exception as e:
      print ("Exception totales() | %s" % str(e))
    return table_totales

  def employe_signature(self):
    try:
      try:
        logo = ''
        logo_path = firma = PayRoll.objects.get(uuid=self.uuid).sign.path
        img=im.open(logo_path)
        if img.size[0] > img.size[1]:
          logo = Image(logo_path, width=1.3*inch, height=0.6*inch, hAlign='CENTER')
        else:
          logo = Image(logo_path, width=1*inch, height=1*inch, hAlign='CENTER')
          logo.hAlign = 'LEFT'
      except Exception as e:
        # print 'Error al obtener el LOGO para el PDF ==> {}'.format(str(e))
        pass

      signature_data = [
              #[s, s, logo],
              [Paragraph(self.signature_legend, basic_left_justify_2), Paragraph('FIRMA:', basic_right), logo],
      ]

      table_signature = Table(signature_data, colWidths=[14*cm, 1*cm, 4.0*cm], style=[
              #('GRID', (0,0),(-1,-1), 1, colors.gray),
              ('LINEBELOW', (-1,0),(-1,0), 1, bg_color),
              ('RIGHTPADDING', (0,0),(-1,-1), 0.3),
              ('LEFTPADDING', (0,0),(-1,-1), 0.3),
              ('BOTTOMPADDING', (0,0),(-1,-1), 0),
              ('VALIGN', (0,0),(-1,-1), 'BOTTOM'),
        ])
    except Exception as e:
      print ("Exception employe_signature() => %s" % str(e))
    return table_signature

  def tfd_data(self):
    try:
      tfd_data = [
            [Paragraph('<b>COMPROBANTE FISCAL DIGITAL POR INTERNET</b>', style_white), s, s],
            [Paragraph('<b>Folio fiscal: </b>%s' % self.uuid, _8_left), s, Paragraph('<b>Lugar de emisión: </b>%s' % self.expedition_place, _8_left)],
            [Paragraph('<b>Fecha y hora de certificación: </b>%s' % self.date_cert, _8_left), s, Paragraph('<b>Fecha y hora de emisión: </b>%s' % self.date, _8_left)],
            [Paragraph('<b>No. de serie del CSD del SAT: </b>%s' % self.serial_sat, _8_left), s, Paragraph('<b>No. de serie del CSD del emisor: </b>%s' % self.serial_cfdi, _8_left)],
            [Paragraph('<b>Fecha Pago: </b>%s' % self.paid_date, _8_left), s, s],
            [s, s, s],
      ]

      table_tfd = Table(tfd_data, colWidths=[9.5*cm, 0.05*cm, 9.5*cm], style=[
            #('GRID', (0,0),(-1,-1), 1, colors.gray),
            ('SPAN', (0,0),(-1,0)),
            ('BACKGROUND', (0,0),(-1,0), bg_color),
            ('TOPPADDING', (0,0),(-1,-1), 1),
            ('BOTTOMPADDING', (0,0),(-1,-1), 1),
        ])
    except Exception as e:
      print ("Exception tfd_data() | %s" % str(e))
    return table_tfd

  def tfd_seals(self):
    try:
      self.createqr()
      QR = Image('%s%s.png' % (PATH_QR, self.uuid), 1.3*inch, 1.3*inch)
      
      data_tfd = [
        [QR, Paragraph('<b>Cadena Original del Complemento de Certificación Digital del SAT</b>', titles_tfd)],
        [s, Paragraph(self.original_string_tfd , basic_left)],
        [s, Paragraph('<b>Sello Digital del Contribuyente Emisor</b>', titles_tfd)],
        [s, Paragraph(self.seal_cfd, basic_left)],
        [s, Paragraph('<b>Sello Digital del SAT</b>', titles_tfd)],
        [s, Paragraph(self.seal_sat , basic_left)],
      
      ]

      table_tfd =Table(data_tfd, colWidths=[4*cm, 15.05*cm], style=[
       
        ('LINEAFTER',(0,0),(0,-1), 1, bg_color),
        ('SPAN',(0,0),(0,-1)), # QR CODE
     
        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1), 'CENTER'),
        #('TOPPADDING',(0,0),(-1,-1), 2.5),
        ('TOPPADDING', (1,0),(-1,0), 0.5),
        ('BOTTOMPADDING', (1,-1),(-1,-1), 1.5),
        
        ('TOPPADDING', (1,1),(1,1), 0), # Cadena
        ('BOTTOMPADDING', (1,1),(1,1), 0.5), # Cadena

        ('TOPPADDING', (1,3),(1,3), 0), # Sello Emisor
        ('BOTTOMPADDING', (1,3),(1,3), 0.5), # Sello Emisor

        ('TOPPADDING', (1,5),(1,5), 0), # Sello SAT
        ('BOTTOMPADDING', (1,5),(1,5), 0.5), # Sello SAT
        
      ])

    except Exception as e:
      print ("Exception tfd_seals() | %s" % str(e))
    return table_tfd

  def truncate(self, f, n):
    try:
      '''Truncates/pads a float f to n decimal places without rounding'''
      s = '{:,}'.format(f)
      if 'e' in s or 'E' in s:
          return '{0:.{1}f}'.format(f, n)
      i, p, d = s.partition('.')
      return '.'.join([i, (d+'0'*n)[:n]])
    except Exception as e:
      print( "Exception truncate() | %s" % str(e))
    
class NumberedCanvas(canvas.Canvas):
  def __init__(self, *args, **kwargs):
    canvas.Canvas.__init__(self, *args, **kwargs)
    self._saved_page_states = []

  def showPage(self):
    self._saved_page_states.append(dict(self.__dict__))
    self._startPage()

  def save(self):
    """add page info to each page (page x of y)"""
    num_pages = len(self._saved_page_states)
    for state in self._saved_page_states:
      self.__dict__.update(state)
      self.draw_page_number(num_pages)
      canvas.Canvas.showPage(self)
    canvas.Canvas.save(self)

  def draw_page_number(self, page_count):
    
    self.setFont('Helvetica-Bold', 9)
    self.setFillColor(HexColor('#000000'))
    self.drawString(2.6*inch, 0.2*inch, 'Este documento es una representación impresa de un CFDI')
    
    self.setFont('Helvetica-Bold', 8)
    self.setFillColor(HexColor('#555759'))
    self.drawString(7.2*inch, 0.1*inch, "Página %d de %d" % (self._pageNumber, page_count))
    

def validate_password(password):
  success = True
  message = u'Password Correcta'
  try:
    upper_letter = False
    lower_letter = False
    number_letter  = False
    special_letter = False
    uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lowers = 'abcdefghijklmnopqrstuvwxyz'
    numbers = '123456789'
    if not len(password) >= 8:
      return False, u'Las Contraseñas deben de ser de 8 caracters como mínimo.'
    for c in password:
      if c in uppers:
        upper_letter = True
      elif c in lowers:
        lower_letter = True
      elif c in numbers:
        number_letter =  True
      elif re.search(r'\W+', c):
        special_letter = True

    if not upper_letter:
      return False, u'Las Contraseñas válidas contienen al menos una letra MAYÚSCULA'
    if not lower_letter:
      return False, u'Las Contraseñas válidas contienen al menos una letra minuscula'
    if not number_letter:
      return False, u'Las Contraseñas válidas continen al menos un dígito'
    if not special_letter:
      return False, u'Las Contraseñas válidas continen al menos un caracter especial'
  except Exception as e:
    print ('Exception in validate_password ==> {}'.format(str(e)))
    message = u'Las Contraseñas válidas contienen al menos una letra MAYÚSCULA, un dígito y un caracter especial y deben de ser de 8 caracters como mínimo.'
    success = False

  return success, message


def WS_validate(xml_string):
  success = False
  message = 'Estructura invalida'
  try:
    #import pdb; pdb.set_trace()
    url = 'https://demo-facturacion.finkok.com/servicios/soap/validation.wsdl'
    if settings.VALIDATE_CFDI:
      url = 'https://demo-facturacion.finkok.com/servicios/soap/validation.wsdl'
    client = Client(url, location=url, cache=None)
    result = client.service.validate(xml_string.encode('base64'), settings.USERNAME_FK, settings.PASSWORD_FK)
    try:
      xml = result.xml
      sello = result.sello
      sello_sat = result.sello_sat
      if xml and sello and sello_sat:
        success, message = True, 'Successful'
      else:
        message = result.error.encode('utf8')
    except:
      try:
        try:
          message = result.error.encode('utf8')
        except:
          message = result.error.decode('utf8')
      except: 
        message = result.error
  except Exception as e:
    print ('Error in WS_validate ==> {}'.format(str(e)))

  return success, message


def valiate_nomina(xml_etree=None, xml_string=None, xml_file=None, taxpayer_id=None):
  try:
    if not xml_etree:
      if xml_file:
        xml_string = open(xml_file, 'r').read()
      xml_etree = etree.fromstring(xml_string)
    namespaces = {'cfdi':'http://www.sat.gob.mx/cfd/3' , 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
    try:
      tfd = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital', namespaces=namespaces)[0]
      uuid = tfd.get('UUID').upper()
      try:
        invoice = PayRoll.objects.get(uuid=uuid)
        return False, 'Registro duplicado'
      except PayRoll.DoesNotExist:
        pass
    except:
      return False, 'XML sin timbrar'
    tipo_comprobante = xml_etree.get('TipoDeComprobante')
    if tipo_comprobante != 'N':
      return False, u'Comprobante no corresponde a Nómina'
    taxpayer_id_ = xml_etree.xpath('.//cfdi:Emisor/@Rfc',namespaces=namespaces)[0]
    if taxpayer_id_ != taxpayer_id:
      return False, u'Nómina no corresponde al emsior'
    if settings.VALIDATE_CFDI:
      #'Mandar llamar metodo Validate'#
      success, message = WS_validate(xml_string)
      if not success:
        return False, message
    rtaxpayer_id = xml_etree.xpath('.//cfdi:Receptor/@Rfc',namespaces=namespaces)[0]
    employee_exists = Employee.objects.filter(taxpayer_id=rtaxpayer_id).exists()
    if not employee_exists:
      create_employee_success = create_employee(xml_etree)
  except Exception as e:
    print ('EXCEPTION IN VALIDATE NOMINA ==> {}'.format(str(e)))
    return False, 'Estructura invalida'
  
  return True, 'Comprobante cargado con exito'

def get_values(xml_string):
  try:
    data_dict = {
      #'account' : None,
      'business' : None,
      'employee' : None,
      'version' : '3.3', 
      'uuid' : None, 
      'taxpayer_id' : None, 
      'issuer_name' : None, 
      'rtaxpayer_id' : None, 
      'receiver_name' : None,
      'serial' : None,
      'folio' : None, 
      'emission_date' : None, 
      'stamping_date' : None, 
      'payroll_type' : 'O', 
      'paid_date' : None, 
      'paid_days' : None, 
      'total' : 0.00, 
      'paid_date_from' : None, 
      'paid_date_to' : None, 
      'total_per' : 0.00, 
      'total_ded' : 0.00, 
      'total_oth' : 0.00, 
      'status' : 'V', 
      'type' : 'N', 
      'notes' : None
    }
    namespaces = {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
    xml_etree = etree.fromstring(xml_string)
    try:
      version = xml_etree.get('Version')
      data_dict['version'] = version
    except:
      pass
    try:
      uuid = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID', namespaces=namespaces)[0]
      data_dict['uuid'] = uuid.upper()
    except:
      pass
    try:
      taxpayer_id = xml_etree.xpath('.//cfdi:Emisor/@Rfc', namespaces=namespaces)[0]
      data_dict['taxpayer_id'] = taxpayer_id
      business = Business.objects.get(taxpayer_id=taxpayer_id)
      data_dict['business'] = business
    except:
      pass
    try:
      issuer_name = xml_etree.xpath('.//cfdi:Emisor/@Nombre', namespaces=namespaces)[0]
      data_dict['issuer_name'] = issuer_name
    except:
      pass
    try:
      rtaxpayer_id = xml_etree.xpath('.//cfdi:Receptor/@Rfc', namespaces=namespaces)[0]
      data_dict['rtaxpayer_id'] = rtaxpayer_id
      try:
        employee_exists = Employee.objects.filter(taxpayer_id=rtaxpayer_id).exists()
        if not employee_exists:
          create_employee_success = create_employee(xml_etree)
        employee = Employee.objects.get(taxpayer_id=rtaxpayer_id)
        data_dict['employee'] = employee
      except:
        pass
    except:
      pass
    try:
      receiver_name = xml_etree.xpath('.//cfdi:Receptor/@Nombre', namespaces=namespaces)[0]
      data_dict['receiver_name'] = receiver_name
    except:
      pass
    try:
      serial = xml_etree.get('Serie')
      data_dict['serial'] = serial
    except:
      pass
    try:
      folio = xml_etree.get('Folio')
      data_dict['folio'] = folio
    except:
      pass
    try:
      emission_date = xml_etree.get('Fecha')
      data_dict['emission_date'] = emission_date
    except:
      pass
    try:
      stamping_date = xml_etree.xpath('.//cfdi:Complemento/tfd:TimbreFiscalDigital/@FechaTimbrado', namespaces=namespaces)[0]
      data_dict['stamping_date'] = stamping_date
    except:
      pass
    try:
      payroll_type = xml_etree.xpath('.//cfd:Complemento/nomina12:Nomina/@TipoNomina', namespaces=namespaces)[0]
      data_dict['payroll_type'] = payroll_type.upper()
    except:
      pass
    try:
      paid_date = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@FechaPago', namespaces=namespaces)[0]
      data_dict['paid_date'] = paid_date
    except:
      pass
    try:
      paid_days = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@NumDiasPagados', namespaces=namespaces)[0]
      data_dict['paid_days'] = paid_days
    except:
      pass
    try:
      total = xml_etree.get('Total')
      data_dict['total'] = total
    except:
      pass
    try:
      paid_date_from = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@FechaInicialPago', namespaces=namespaces)[0]
      data_dict['paid_date_from'] = paid_date_from
    except:
      pass
    try:
      paid_date_to = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@FechaFinalPago', namespaces=namespaces)[0]
      data_dict['paid_date_to'] = paid_date_to
    except:
      pass
    try:
      total_per = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@TotalPercepciones', namespaces=namespaces)[0]
      data_dict['total_per'] = total_per
    except:
      pass
    try:
      total_ded = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@TotalDeducciones', namespaces=namespaces)[0]
      data_dict['total_ded'] = total_ded
    except:
      pass
    try:
      total_oth = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/@TotalOtrosPagos', namespaces=namespaces)[0]
      data_dict['total_oth'] = total_oth
    except:
      pass
    try:
      type_ = xml_etree.get('TipoDeComprobante')
      data_dict['type'] = type_.upper()
    except:
      pass
  except Exception as e:
    print ('Exception in get_values ==> {}'.format(str(e)))
  
  return data_dict


from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def send_email(subject, html_url, context, to_email):
  success = False
  message = ''
  try:
    html_content = render_to_string(html_url, context)
    msg = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, to_email)
    msg.content_subtype = "html"
    msg.send()
    success = True
    message = 'Correo de invitacion enviado'
  except (Exception, e):
    print('Exception in send_email =>', e)
    message = 'Error al enviar correo de invitacion'

  return success, message

############### INIT FIREBASE ###############

from pyfcm import FCMNotification
# import pyrebase

push_service = FCMNotification(api_key='AAAATcJCEL0:APA91bHCX6N_HWFi1SaD5z98ok8QF6oJT3qHQVNapCIWSipYtLn7gb18wDL9NABNLJQvxx_dgPnYhLCmvafN04YqG0pZlQm40i4T6ZzL8FmNcJTZIsUYj733TgMKur9mSWyAmMXyLMHa')
config = { 
  "apiKey": "AIzaSyA9N_PJal542SdQfHYGNrVEpF4Jvrcrolc", 
  "authDomain": "nominas-fk.firebaseapp.com", 
  "databaseURL": "https://nominas-fk.firebaseio.com", 
  "projectId": "nominas-fk", 
  "storageBucket": "", 
  "messagingSenderId": "333971591357" 
}
# firebase = pyrebase.initialize_app(config)
firebase = ''
message_title = 'Nueva Notificacion de Nominas'

#############################################

def send_push(title, message, to_user):
  try:
    icon = '/static/img/nomina.ico'
    registration_ids = []
    tokens = TokensUser.objects.filter(user=to_user.user)

    for token in tokens:
      registration_ids.append(token.token)
    push_service.notify_multiple_devices(registration_ids=registration_ids, message_icon=icon, message_title=title, message_body=message)
  except (Exception, e):
    print ('Error in send_push => %s' % e)

def send_bell(title, message, to_role, to_user):
  try:
    if to_role == 'B':
      News.objects.create(title=title, description=message, business=to_user)
    elif to_role == 'E':
      News.objects.create(title=title, description=message, employee=to_user)
    else:
      News.objects.create(title=title, description=message)
  except (Exception, e):
    print ('Exception in send_bell => %s' % e)

def send_notification(title, message, to_user, emails, html_url, context, to_role='E'):
  send_bell(title, message, to_role, to_user)
  send_push(title, message, to_user)
  #send_email(title, html_url, context, emails)

def create_employee(xml_etree):
  create_employee_success = False
  namespaces = {'cfdi':'http://www.sat.gob.mx/cfd/3', 'nomina12':'http://www.sat.gob.mx/nomina12', 'tfd':'http://www.sat.gob.mx/TimbreFiscalDigital'}
  try:
    rtaxpayer_id = xml_etree.xpath('.//cfdi:Receptor/@Rfc', namespaces=namespaces)[0]
    receiver_name = xml_etree.xpath('.//cfdi:Receptor/@Nombre', namespaces=namespaces)[0]
    taxpayer_id = xml_etree.xpath('.//cfdi:Emisor/@Rfc', namespaces=namespaces)[0]
    n_receptor = xml_etree.xpath('.//cfdi:Complemento/nomina12:Nomina/nomina12:Receptor', namespaces=namespaces)[0]
    email = '{}@pruebas.com'.format(rtaxpayer_id)
    user, create = User.objects.get_or_create(email=email)
    user.role = 'E'
    user.is_active = True
    user.set_password("Pruebas_123!")
    user.save()
    account, Ecreate = Employee.objects.get_or_create(user=user)
    account.name = receiver_name
    account.email = [email]
    account.curp = n_receptor.get('Curp')
    account.taxpayer_id = rtaxpayer_id
    business = Business.objects.get(taxpayer_id=taxpayer_id).id
    account.business_id = business
    account.department = n_receptor.get('Puesto','')
    account.puesto = n_receptor.get('Puesto','')
    account.mbid = n_receptor.get('NumEmpleado','')
    account.user = user
    account.save()
    create_employee_success = True
  except Exception as e:
    print ('Exception in create_employee => {}'.format(str(e)) )
  return create_employee_success

def upload_file_to_dropbox(path):
  try:

    if not os.path.exists(path):
      raise Exception("Path:{} not exists".format(path))
    
    #OBTENER NOMBRE DEL ARCHIVO
    filename = os.path.basename(path)

    #CREAR CONEXION
    dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)

    #CARGAR ARCHIVO
    with open(path, 'rb') as f:
        dbx.files_upload(f.read(), '/' + filename)

    # OBTENER URL DE DESCARGA
    url = dbx.sharing_create_shared_link('/' + filename).url

    return True, url

  except Exception as e:
    print("Exception in upload_file_to_dropbox => {}".format(str(e)))

  return False, None
