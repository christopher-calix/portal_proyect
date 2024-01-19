# -*-  encoding: utf-8 -*-
from .utils import XMLValidator
from .utils import SatValidator
from .utils import SealValidator
from .utils import AmountValidator
from .utils import SubjectDNValidator
from django.conf import settings


from django.core.files.base import ContentFile
from Apps.nomina_app.models import Invoice

from django.utils.translation import gettext as _

from django.conf import settings 
from django.contrib.auth.models import User
from django.db.models import Sum

from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime
from datetime import timedelta
import json
from lxml import etree
import hashlib
import pprint
import re
import os
import base64
import cgi
import M2Crypto



class Receives:
  """This class is responsible for controlling the flow of 
     validation for invoices in XML format
  """
  
  def __init__(self, xml, user=None, original_string=None, signing=True):
    """This is the normal flow of validation of each of the errors 
       mentioned by the SAT and are within diagram validation
    """
   
    self.xml_string = xml
    self.original_string = original_string
    self.user = user

    self.is_valid = True
    self.certificate = None
    self.certificate_string = ''
    self.uuid = None
    self.cfd_seal = None
    self.sat_seal = None
    self.reseller = None
    self.reseller_passphrase = None
    self.complementNode = None
    self.xml_etree = None
    self.incident_list = []
    self.is_external = False    
    self.addenda = None
    self.addenda_string = ''
    self.cod_status = ''
    self.sello_sat = None
    self.certificate_sat = None
    self.sat_original_string = None

    if user is not None:
      self.is_external = True
    
    self.xml_parser = etree.XMLParser(remove_blank_text=True)
    try:
      xml_encoded = self.xml_string.encode('utf-8')
      try:
        self.xml_etree = etree.XML(xml_encoded, parser=self.xml_parser)
      except Exception as e:
        print (str(e))
        self.is_valid = False
        self.incident_list.append('Estructura invalida')
    except:
      try:
        self.xml_etree = etree.XML(self.xml_string, parser=self.xml_parser)
      except Exception as e:
        print (str(e))
        self.is_valid = False
        self.incident_list.append('Estructura invalida')

    self.version = self.xml_etree.get('version')
    if self.version is None:
      self.version = self.xml_etree.get('Version')  
    
    if self.version not in ('3.3', '3.2'):
      self.is_valid = False
      self.incident_list.append('Versión 3.2 no aceptable')

    self.attribute_tfd_uuid = 'UUID'
    self.attribute_tfd_fecha = 'FechaTimbrado'
    if self.version == '3.2':
      self.attribute_seal = 'sello'
      self.attribute_certificate = 'certificado'
      self.attribute_nocertificate  = 'noCertificado'        
      self.attribute_date = 'fecha'
      self.attribute_rfc = 'rfc'
      self.attribute_sat_seal = 'selloSAT'
      self.attribute_tfd_version = 'version'
      self.attribute_tfd_sellocfd='selloCFD'
      self.attribute_tfd_nocertsat = 'noCertificadoSAT'
      
    elif self.version == '3.3':
      self.attribute_seal = 'Sello'
      self.attribute_certificate = 'Certificado'
      self.attribute_nocertificate  = 'NoCertificado'        
      self.attribute_date = 'Fecha'
      self.attribute_rfc = 'Rfc'
      self.attribute_sat_seal = 'SelloSAT'
      self.attribute_tfd_version = 'Version'
      self.attribute_tfd_rfcprov = 'RfcProvCertif'
      self.attribute_tfd_leyenda = 'Leyenda'
      self.attribute_tfd_sellocfd='SelloCFD'
      self.attribute_tfd_nocertsat = 'NoCertificadoSAT'
      
    try:
      self.fecha = self.xml_etree.get(self.attribute_date)
      self.cfd_seal = self.xml_etree.get(self.attribute_seal)
      self.serial_number = self.xml_etree.get(self.attribute_nocertificate)
      self.taxpayer_id = self.xml_etree.xpath('//tmp:Emisor', namespaces={'tmp':'http://www.sat.gob.mx/cfd/3'})[0].get(self.attribute_rfc)
      self.certificate_string, self.certificate = self.get_certificate(self.xml_etree.get(self.attribute_certificate))
      if self.certificate_string is None or self.certificate is None:
        raise NameError('Invalid Certificate / there is no cerfile')   
    except Exception as e:
      #import pdb; pdb.set_trace()
      #incident = SoapError(self.xml_string,301).fault()
      self.incident_list.append('XML mal formado')
      self.is_valid = False
    try:
      if self.serial_number != hex(self.certificate.get_serial_number())[3:-1:2]:
        #incident = SoapError(self.xml_string,712).fault()
        self.incident_list.append('El numero de Certificado es diferente al del numero de certificado del atributo certificado')
        self.is_valid = False
    except:       
      #incident = SoapError(self.xml_string,712).fault()
      self.incident_list.append('El numero de Certificado es diferente al del numero de certificado del atributo certificado')
      self.is_valid = False

    try:
      tfd = None
      tfd = self.xml_etree.xpath('//tmp:TimbreFiscalDigital', namespaces={'tmp':'http://www.sat.gob.mx/TimbreFiscalDigital'})
      self.validate_seal = False
      print (tfd)
      if tfd:
        tfd = tfd[0]
        #TODO: OBTENER ATRIBUTOS
        self.sello_sat = tfd.get(self.attribute_sat_seal)
        self.version_tfd = tfd.get(self.attribute_tfd_version)
        self.uuid_tfd = tfd.get(self.attribute_tfd_uuid)
        self.fecha_tfd = tfd.get(self.attribute_tfd_fecha)
        self.selloCFD_tfd = tfd.get(self.attribute_tfd_sellocfd)
        #self.selloCFD_tfd = self.cfd_seal
        self.nocert_tfd = tfd.get(self.attribute_tfd_nocertsat)
        if self.version_tfd == '1.0':
          self.sat_original_string = '||' + self.version_tfd + '|' + self.uuid_tfd + '|' + self.fecha_tfd + '|' + self.cfd_seal + '|' + self.nocert_tfd + '||'
        elif self.version_tfd == '1.1':
          self.rfcProvCert_tfd = tfd.get(self.attribute_tfd_rfcprov)
          self.leyenda_tfd = tfd.get(self.attribute_tfd_leyenda)
          if not self.leyenda_tfd:
            self.sat_original_string = '||' + self.version_tfd + '|' + self.uuid_tfd + '|' + self.fecha_tfd + '|' + self.rfcProvCert_tfd + '|' + self.cfd_seal + '|' + self.nocert_tfd + '||'
          elif self.leyenda_tfd:
            self.sat_original_string = self.sat_original_string = '||' + self.version_tfd + '|' + self.uuid_tfd + '|' + self.fecha_tfd + '|' + self.rfcProvCert_tfd + '|' + self.leyenda_tfd +  '|' + self.cfd_seal + '|' + self.nocert_tfd + '||'
        
        self.b64certificate_sat = self.get_certificado_sat()

        self.original_string_sat, self.certificate_sat = self.get_certificate(self.b64certificate_sat)
        self.seal_validator_sat()
    except Exception as e:
      print ('EXCEPTION SAT SEAL VALIDATOR')
      print (str(e))
    
    self.xml_validation_is_valid = False
    self.signing_node_exist_is_valid = False
 
    self.xml_validation()
    if self.is_valid:
        self.xml_validation_is_valid = True
    self.signed_by_sat_authority()
    self.fiel_validation()
    self.lco_validator()

    self.seal_validator()

    if tfd:
      self.seal_validator_sat()

    
  def get_certificate(self, certificate_string=''):
    try:
      split_string_cert = [certificate_string[i:i+64] for i in range(0, len(certificate_string), 64)]
      l = [x + "\n"for x in split_string_cert]
      split_string_cert = l
      split_string_cert = "".join(split_string_cert)
      certificate_string = "-----BEGIN CERTIFICATE-----\n" + \
                                  split_string_cert + \
                                "-----END CERTIFICATE-----"
      x509_cert = M2Crypto.X509.load_cert_string(certificate_string, M2Crypto.X509.FORMAT_PEM)
      return certificate_string, x509_cert
    except:
      pass
    return None, None
     
  def xml_validation(self):
    """
    Validate the correct formation of the invoice in xml format "parsing"
    """
    try:
 
      xml_invoice_parser = XMLValidator(self.xml_etree, self.version)
      result = xml_invoice_parser.is_valid()
      if not result["success"]:
        
        self.incident_list.append('XML mal formado')
        self.is_valid = False
        self.xml_error = result["message"]
      self.addenda = result['addenda']
      try:
        if self.addenda is not None:
          self.addenda_string = etree.tostring(self.addenda, encoding='UTF-8')
      except:
        pass
      print (result)
    except Exception as e:
      pprint.pprint(e)
   
      self.incident_list.append('XML mal formado')
      self.is_valid = False
    

  def amount_validation(self):
    """
    Validate the correct amounts in the xml (subtotal, total, taxes)
    """
    try:      
      amount_validator = AmountValidator(self.xml_etree)
      result = amount_validator.is_valid()
      if not result["success"]:
       
        self.incident_list.append(result['message'])
        self.is_valid = False
      print (result)
    except Exception as e:
      pprint.pprint(e)
      self.incident_list.append('XML mal formado')
      self.is_valid = False
  

  def signed_by_sat_authority(self):
    """Validate that the issuer CSD has been signed by a Certificate Authority of the SAT
    """ 
    try:
   
      signed_sat = SignedSATAuthority(self.xml_etree, self.certificate)
      result = signed_sat.is_valid()  
      print (result)
      if not result["success"]:
        
        self.incident_list.append('Certificado No expedido por el SAT')
        self.is_valid = False
    except Exception as e:
      pprint.pprint(e)
      
      self.incident_list.append('Certificado No expedido por el SAT')
      self.is_valid = False
    

  def fiel_validation(self):
    """Validate that The issuer certificate is not of type FIEL
    """ 
    try:   
      fiel_validator = FielValidator(self.xml_etree, self.certificate)
      result = fiel_validator.is_valid()
      print (result)
      if not result["success"]:
       
        self.incident_list.append('El certificado no es de tipo CSD')
        self.is_valid = False
    except Exception as e:
      pprint.pprint(e)
      self.incident_list.append('El certificado no es de tipo CSD')
      self.is_valid = False

    
  def lco_validator(self):
    """Validate that RFC issuer is not in the regime of taxpayers
    """
    try:
      lco_validator = LCOValidator(self.xml_etree, self.certificate)
      result = lco_validator.is_valid()
      print (result)
      if not result["success"]:
        self.incident_list.append('RFC del emisor no se encuentra en el régimen de contribuyentes')
        self.is_valid = False
    except Exception as e:
      pprint.pprint(e)
      self.incident_list.append('RFC del emisor no se encuentra en el régimen de contribuyentes')
      self.is_valid = False
 
      
  def seal_validator(self):
    """Validate the seal of the CFDI
    """
    try:
  
      seal_validator = SealValidator(self.cfd_seal, self.certificate, self.xml_string, self.version)
      result = seal_validator.is_valid()
      self.original_string = seal_validator.original_string
      if result["success"]:
        self.original_string = seal_validator.original_string
        self.cfd_seal = seal_validator.sign       
      else:
       
        self.incident_list.append('CFDI33102 - El resultado de la digestión debe ser igual al resultado de la desencripción del sello.')
        self.is_valid = False
    except Exception as e:
      pprint.pprint(e)
      
      self.incident_list.append('CFDI33102 - El resultado de la digestión debe ser igual al resultado de la desencripción del sello.')
      self.is_valid = False
 
 
  def seal_validator_sat(self):
    """Validate the seal of the CFDI
    """
    try:
      seal_validator_sat = SealValidator(self.sello_sat, self.certificate_sat, version=self.version, original_string=self.sat_original_string, sello_sat=True)
      result = seal_validator_sat.is_valid()
      self.original_string_sat = seal_validator_sat.original_string
      if result["success"]:
        self.original_string_sat = seal_validator_sat.original_string
        self.sello_sat = seal_validator_sat.sign
        self.validate_seal=True

        print ("Exito"    )
        self.is_valid = False
    except Exception as e:
      pprint.pprint(e)
      pass

  def get_certificado_sat(self):

    try:
      self.certificate_path = os.path.join(settings.CERTIFICATE_STORAGE, '%s.cer' % self.nocert_tfd)
      if not os.path.isfile(self.certificate_path):
        
        import urllib.request
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            self.url = settings.SAT_GET_CERTIFICATES % (self.nocert_tfd[:6], self.nocert_tfd[6:12], self.nocert_tfd[12:14], self.nocert_tfd[14:16], self.nocert_tfd[16:18], self.nocert_tfd)
            self.response = urllib.request.urlopen(self.url)
        except Exception as e:
          print ("Errot al obtener el certificado SAT => %s" % str(e))
        else:
          certificate = open(self.certificate_path, "w+")
          self.certificate_string = self.response.read()
          certificate.write(self.certificate_string)
          certificate.close()
      certificate = open(self.certificate_path, "r")
      self.certificate_string = certificate.read()
      certificate.close()
      self.certificateb64 = base64.b64encode(self.certificate_string)
      return self.certificateb64
    except Exception as e:
     print ("Error al obtener el certificado SAT => %s" % str(e))
     return None


class SignedSATAuthority(object):
  
  def __init__(self, xml_etree, x509_cert):
    self.valid = True
    self.error = ''
    try:
      #self.xml_root = xml_etree.getroot()
      self.xml_root = xml_etree
      self.x509_cert = x509_cert

      self.issuer_dn = self.x509_cert.get_issuer().as_text(flags=(M2Crypto.m2.XN_FLAG_RFC2253 | M2Crypto.m2.ASN1_STRFLGS_UTF8_CONVERT )  )
      self.issuer_dn = self.issuer_dn.decode("utf8","ignore")
      sat_admin = u"Servicio de Administraci\C3\B3n Tributaria" 
      sat_rfc = u"SAT97070701NN3"
      
      self.issuer_is_valid = False
      if ( sat_admin in self.issuer_dn or sat_rfc in  self.issuer_dn ):
        self.issuer_is_valid = True

      self.ca_is_valid = False
      certs_path = os.path.join(os.path.dirname(__file__), "certs", "production")
      if False and settings.LOCALDEV:
        certs_path = os.path.join(os.path.dirname(__file__), "certs")

      for root_cert in os.listdir(certs_path):
        cert_flag = False
        if os.path.isfile(os.path.join(certs_path,root_cert)):
          try:
            ca_root = M2Crypto.X509.load_cert("%s/%s" % (certs_path, root_cert), M2Crypto.X509.FORMAT_DER)
            cert_flag = True
          except M2Crypto.X509.X509Error:
            ca_root = M2Crypto.X509.load_cert("%s/%s" % (certs_path, root_cert), M2Crypto.X509.FORMAT_PEM)
            cert_flag = True
          except:
            continue
          finally:
            if cert_flag and bool(self.x509_cert.verify(ca_root.get_pubkey())):
              self.ca_is_valid = True
              break
    except Exception as e:
      self.valid = False
      self.error = str(e)
     
  def is_valid(self):    
    if self.valid and self.ca_is_valid and self.issuer_is_valid:
      result = {
        "success" : True,
        "message" : "The issuer CSD has been signed by a Certificate Authority of the SAT"
      }
    else:
      result = {
        "success" : False,
        "message" : "The issuer CSD has not been signed by a Certificate Authority of the SAT"
      }
    print (result)
    return result
  

class FielValidator():
  """This class is responsible for validating whether a certificate is a 
     Fiel or a certificate
  """
  
  def __init__(self,xml_etree, x509_cert):
    self.valid = True
    self.error = ''
    try:
      self.xml_root = xml_etree
      self.x509_cert = x509_cert
      subject = self.x509_cert.get_subject().__str__()
      if "OU" in subject:
        self.is_fiel = False
      else:
        self.is_fiel = True
    except Exception as e:
      self.valid = False
      self.error = str(e) 

  def is_valid(self):
    if self.valid  and not self.is_fiel:
      result = {
        "success" : True,
        "message" : "The issuer certificate is not of type FIEL"
      }
    else:
      result = {
        "success" : False,
        "message" : "The issuer certificate is of type FIEL"
      }
    pprint.pprint(result)
    return result

class LCOValidator(object):
  
  def __init__(self, xml_etree, x509_cert):
    self.valid = True
    self.error = ''
    self.lco_is_valid = False
    try:
      #self.xml_root = xml_etree.getroot() 
      self.xml_root = xml_etree
      self.x509_cert = x509_cert
      self.node = self.xml_root.find(XML_INVOICE_NAMESPACE % "Emisor")
      self.rfc =  self.node.get("rfc")
      self.serial_number = hex(self.x509_cert.get_serial_number())[3:-1:2]
      self.rfc_ascii = self.__to_ascii(self.rfc)
      try:
        lco_list = lco.objects.get(rfc=self.rfc_ascii, certificate_number=self.serial_number)
        self.lco_is_valid = True
      except Exception as e:
        self.error = str(e)
        try:
          lco_list = lco.objects.get(rfc=self.rfc, certificate_number=self.serial_number)
          self.lco_is_valid = True
        except Exception as e:
          self.error = str(e)
          self.lco_is_valid = False
    except Exception as e:
      self.valid = False
      self.error = str(e) 

  def __to_ascii(self,string):
    stripped = [c if 0 < ord(c) < 127 else '&' for c in string]
    return ''.join(stripped)      
  
  def is_valid(self):
    if self.valid and self.lco_is_valid:
      result = {
        "success" : True,
        "message" : "RFC issuer is in the regime of taxpayers"
      }
    else:
      result = {
        "success" : False,
        "message" : "RFC issuer is not in the regime of taxpayers"
      }
    print (result)
    return result

class SealValidator(object):
  
  def __init__(self, sello, x509_cert, xml_string='', version='3.2', original_string='', sello_sat=False):
    self.valid = True
    self.error = ''
    self.sign = sello
    self.x509_cert = x509_cert
    self.version = version    
    self.original_string = original_string
    self.sello_sat = sello_sat

    try:
      self.seal_is_valid = False      
      self.decoded_sign = base64.decodestring(self.sign)
      
      if not self.original_string:
        os_obj = OriginalString(xml_string, self.version)
        self.original_string = os_obj.get_original_string()
      print(self.original_string)
      rsa = self.x509_cert.get_pubkey().get_rsa()
      pubkey = M2Crypto.EVP.PKey()
      pubkey.assign_rsa(rsa)
      if self.version == '3.2':
        pubkey.reset_context(md='sha1')
      elif self.version == '3.3':
        pubkey.reset_context(md='sha256')
      pubkey.verify_init()
      pubkey.verify_update(self.original_string)
      self.seal_is_valid = bool(pubkey.verify_final(self.decoded_sign)) 
    except Exception as e:
      self.valid = False
      self.error = str(e)  
   
  
  def is_valid(self):
    if not self.sello_sat:
      result = {
        "success" : self.valid and self.seal_is_valid,
        "message" : "The seal is valid for this CFDI" if self.valid and self.seal_is_valid else "The seal is not valid for this CFDI",
        "original_string" : self.original_string,
        "sign" : self.sign
      }
    else:
      result = {
        "success" : self.valid and self.seal_is_valid,
        "message" : "The sat seal is valid for this CFDI" if self.valid and self.seal_is_valid else "The sat seal is not valid for this CFDI",
        "original_string" : self.original_string,
        "sign" : self.sign
      }
    print (result)
    return result