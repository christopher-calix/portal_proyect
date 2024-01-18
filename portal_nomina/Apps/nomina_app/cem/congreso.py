#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = ['Alfredo Herrejón', 'Alexis Martínez', 'Juan Pérez', 'Abimelec Chávez', 'Alfredo Carrillo']
__copyright__ = 'Copyright (C) 2017 S.A. de C.V., Proyecto: IUSA'
__credits__ = ['Alfredo Herrejón', 'Alexis Martínez', 'Juan Pérez', 'Abimelec Chávez', 'Alfredo Carrillo']
__licence__ = 'Privativo'
__version__ = '1.4'
__maintainer__ = ['Alfredo Herrejón', 'Alexis Martínez', 'Juan Pérez', 'Abimelec Chávez']
__email__ = ['desarrollo@test.com']
__status__ = 'Development'

from django.conf import settings
import os
import sys
from lxml import etree as ET
from lxml.etree import QName
from lxml.etree import Element
from lxml.etree import SubElement
import copy
from M2Crypto.X509 import FORMAT_PEM
from M2Crypto.RSA import load_key_string
import time
from datetime import datetime
from dateutil.tz import tzoffset
import StringIO
from lxml import etree
# import libxml2
# import libxslt
import hashlib
import base64
#import CFDI_32
import CFDI_33
import json
import codecs
import shutil, os
from utils import FinkokWS, FinkokWSRetentions
from csd import CSD_DICT
import logging
from pdf_creator import CreatePDF
import re
#import pypyodbc
#from donat11 import Donatarias
from copy import deepcopy
#import sub_retenciones
#import sub_dividendos

from nomina12 import (
  EmisorType as NomEmisorType,
  EntidadSNCFType,
  ReceptorType as NomReceptorType,
  SubContratacionType,
  DeduccionesType as NomDeduccionesType,
  DeduccionType as NomDeduccionType,
  PercepcionesType as NomPercepcionesType,
  PercepcionType as NomPercepcionType,
  JubilacionPensionRetiroType,
  SeparacionIndemnizacionType,
  HorasExtraType,
  SubsidioAlEmpleoType,
  CompensacionSaldosAFavorType,
  OtroPagoType,
  OtrosPagosType,
  IncapacidadType,
  IncapacidadesType,
  Nomina,
)

#from db_nomina import IUSADB
import subprocess 
from subprocess import check_output
from pdb import set_trace
from app.core.models import PayRoll
from app.core.utils import get_values

reload(sys)
sys.setdefaultencoding('utf-8')

CABECERA_KEYS = ['Folio', 'Nombre_Emisor', 'RFC_Emisor', 'Dom_Emisor_calle', 'Dom_Emisor_noExterior', 'Dom_Emisor_noInterior', 'Dom_Emisor_colonia', 'Dom_Emisor_localidad', 'Dom_Emisor_referencia', 'Dom_Emisor_municipio', 'Dom_Emisor_estado', 'Dom_Emisor_pais', 'Dom_Emisor_codigoPostal', 'Tel_Emisor', 'Dom_Sucursal_calle', 'Dom_Sucursal_noExterior', 'Dom_Sucursal_noInterior', 'Dom_Sucursal_colonia', 'Dom_Sucursal_localidad', 'Dom_Sucursal_referencia', 'Dom_Sucursal_municipio', 'Dom_Sucursal_estado', 'Dom_Sucursal_pais', 'Dom_Sucursal_codigoPostal', 'Tel_Sucursal', 'Version', 'Serie_Comprobante', 'Numero_Aprobacion', 'FormaPago', 'Fecha', 'Hora', 'Dom_LugarExpide_calle', 'Dom_LugarExpide_noExterior', 'Dom_LugarExpide_noInterior', 'Dom_LugarExpide_colonia', 'Dom_LugarExpide_localidad', 'Dom_LugarExpide_referencia', 'Dom_LugarExpide_municipio', 'Dom_LugarExpide_estado', 'Dom_LugarExpide_pais', 'Dom_LugarExpide_codigoPostal', 'Nombre_Receptor', 'RFC_Receptor', 'Dom_Receptor_calle', 'Dom_Receptor_noExterior', 'Dom_Receptor_noInterior', 'Dom_Receptor_colonia', 'Dom_Receptor_localidad', 'Dom_Receptor_referencia', 'Dom_Receptor_municipio', 'Dom_Receptor_estado', 'Dom_Receptor_pais', 'Dom_Receptor_codigoPostal', 'Monto_SubTotal', 'Monto_IVA', 'Monto_Total', 'Estado', 'TipoCFD', 'Notas', 'Notas02', 'Notas03', 'TradingPartner_Prov', 'Calif_TradingPartner_Prov', 'EAN_Proveedor', 'Numero_Factura', 'Numero_OrdenCompra', 'Fecha_OrdenCompra', 'Numero_Proveedor', 'EAN_Tienda', 'Numero_Tienda', 'Nombre_Tienda', 'Dom_Tienda_calle', 'Dom_Tienda_noExterior', 'Dom_Tienda_noInterior', 'Dom_Tienda_colonia', 'Dom_Tienda_localidad', 'Dom_Tienda_referencia', 'Dom_Tienda_municipio', 'Dom_Tienda_estado', 'Dom_Tienda_pais', 'Dom_Tienda_codigoPostal', 'RFC_Tienda', 'Cod_Moneda', 'Dias_Pago', 'Porc_Desc_ProntoPago', 'Monto_Desc_ProntoPago', 'Cod_Descuento', 'Porc_Descuento', 'Monto_Descuento', 'Cantidad_LineasFactura', 'Fecha_Vencimiento', 'Cod_Zona', 'Numero_Receptor', 'Cod_Vendedor', 'Nombre_Vendedor', 'Via_Embarque', 'Condiciones_Pago', 'Numero_Pedido', 'Fecha_Pedido', 'Letras_Monto_Total', 'Cantidad_unidades', 'Cantidad_empaques', 'EAN_Receptor', 'EAN_LugarExpide', 'IEPS_Id', 'Estatus', 'Numero_Emisor', 'Monto_Merma', 'Monto_SubTotal_ApIVA', 'Transportista', 'Numero_Solicitud', 'Desc_Moneda', 'Misc01', 'Misc02', 'Misc03', 'Misc04', 'Misc05', 'Misc06', 'Misc07', 'Misc08', 'Misc09', 'Misc10', 'Misc11', 'Misc12', 'Misc13', 'Misc14', 'Misc15', 'Misc16', 'Misc17', 'Misc18', 'Misc19', 'Misc20', 'Misc21', 'Misc22', 'Misc23', 'Misc24', 'Misc25', 'Misc26', 'Misc27', 'Misc28', 'Misc29', 'Misc30', 'Misc31', 'Misc32', 'Misc33', 'Misc34', 'Misc35', 'Misc36', 'Misc37', 'Misc38', 'Misc39', 'Misc40', 'Misc41', 'Misc42', 'Misc43', 'Misc44', 'Misc45', 'Misc46', 'Misc47', 'Misc48', 'Misc49', 'Misc50', 'Porc_IVA', 'Monto_IEPS', 'Document_Status', 'Delivery_Date', 'RegimenFiscal', 'Num_CtaPago', 'Num_contrarecibo', 'Fecha_Num_contrarecibo', 'Contacto_Compras', 'Customs_gln', 'Alternate_identification_gln', 'Nombre_Aduana', 'Nombre_Aduana_Ciudad', 'Func_Divisa', 'Tasa_Divisa', 'Ref_Tiempo_Pago', 'Ref_Termino_Tiempo_Pago', 'LugarExpedicion', 'SerieFolioFiscalOrig', 'Inf_Cargo_Descuento', 'FechaFolioFiscalOrig', 'Porcentaje_no_aplicado', 'MontoFolioFiscalOrig', 'Monto_Total_Descuentos', 'Monto_Total_Pagar', 'Ano_Aprobacion', 'Motivo_Descuento', 'Metodo_Pago', 'Efecto_Comprobante', 'Monto_TotalImp_Retenidos', 'Monto_TotalImp_Trasladados']
DETALLE_KEYS = ['Linea_Descripcion', 'Linea_Cantidad', 'Linea_Unidad', 'Linea_PrecioUnitario', 'Linea_Importe', 'ClaveProdServ', 'Linea_Aduana_FechaDoc', 'Linea_Aduana_Nombre', 'Linea_CuentaPredial_Numero', 'Linea_FraccionArancelaria', 'Linea_Notas', 'Linea_Cod_UPC', 'Linea_Piezas_Empaque', 'Linea_Cod_DUN', 'Linea_Cod_Barras', 'Linea_Cod_Articulo', 'Linea_Cod_Desc', 'Linea_Porc_Desc', 'Linea_Monto_Desc', 'Linea_PrecioUnitario_SinDesc', 'Linea_Cant_Empaques_Fac', 'Linea_Cant_Empaques_Emb', 'Linea_Porc_IVA', 'Linea_Monto_IVA', 'Linea_Porc_IEPS', 'Linea_Monto_IEPS', 'Linea_PrecioUnitario_ConImp', 'Linea_Importe_ConImp', 'Linea_Frontera', 'Linea_PaisOrigen', 'Linea_EAN_Aduana', 'Linea_Misc01', 'Linea_Misc02', 'Linea_Misc03', 'Linea_Misc04', 'Linea_Misc05', 'Linea_Misc06', 'Linea_Misc07', 'Linea_Misc08', 'Linea_Misc09', 'Linea_Misc10', 'Linea_Misc11', 'Linea_Misc12', 'Linea_Misc13', 'Linea_Misc14', 'Linea_Misc15', 'Linea_Misc16', 'Linea_Misc17', 'Linea_Misc18', 'Linea_Misc19', 'Linea_Misc20', 'Linea_Misc21', 'Linea_Misc22', 'Linea_Misc23', 'Linea_Misc24', 'Linea_Misc25', 'Linea_Misc26', 'Linea_Misc27', 'Linea_Misc28', 'Linea_Misc29', 'Linea_Misc30', 'Linea_Misc31', 'Linea_Misc32', 'Linea_Misc33', 'Linea_Misc34', 'Linea_Misc35', 'Linea_Misc36', 'Linea_Misc37', 'Linea_Misc38', 'Linea_Misc39', 'Linea_Misc40', 'Linea_Misc41', 'Linea_Misc42', 'Linea_Misc43', 'Linea_Misc44', 'Linea_Misc45', 'Linea_Misc46', 'Linea_Misc47', 'Linea_Misc48', 'Linea_Misc49', 'Linea_Misc50', 'Linea_MedicionSecundaria', 'Linea_TipoIdent_Adicional', 'Linea_DescripIdioma', 'Linea_Cant_Adicional', 'Linea_Cant_Adicional_Tipo', 'Linea_Tipo_Referencia', 'Linea_Calif_NumIdentidad', 'Linea_TipoEmpaquetado', 'Linea_Metodo_Pago', 'Linea_Numero_Lote', 'Linea_Fecha_ProdLote', 'Linea_Ind_CargoDescuento', 'Linea_Inf_CargoDescuento', 'Linea_Secuencia_Calculo', 'Linea_Tipo_ServiciosEsp', 'Linea_Ident_Impuesto', 'Linea_Cod_EAN', 'Linea_NoIdentificacion']
IMPUESTOS_C_KEYS = ['Impuesto_TipoImpuesto', 'Impuesto_Descripcion', 'Impuesto_Base', 'Impuesto_Monto_Importe', 'Impuesto_Tasa', 'Impuesto_TipoFactor']
IMPUESTOS_KEYS = ['Impuesto_TipoImpuesto', 'Impuesto_Descripcion', 'Impuesto_Monto_Importe', 'Impuesto_Tasa', 'Impuesto_TipoFactor']
AUXILIAR_KEYS = ['DetalleAux_Tipo', 'DetalleAux_DescTipo', 'DetalleAux_Misc01', 'DetalleAux_Misc02', 'DetalleAux_Misc03', 'DetalleAux_Misc04', 'DetalleAux_Misc05', 'DetalleAux_Misc06', 'DetalleAux_Misc07', 'DetalleAux_Misc08', 'DetalleAux_Misc09', 'DetalleAux_Misc10', 'DetalleAux_Misc11', 'DetalleAux_Misc12', 'DetalleAux_Misc13', 'DetalleAux_Misc14', 'DetalleAux_Misc15', 'DetalleAux_Misc16']

NOMINA_KEYS = ['NM', 'encabezado', 'Version', 'TipoNomina', 'FechaPago', 'FechaInicialPago', 'FechaFinalPago', 'NumDiasPagados', 'TotalPercepciones', 'TotalDeducciones',  'TotalOtrosPagos', '11', '12', '13', '14', '15', '16', '17']
EMISOR_KEYS = ['NM', 'Emisor', 'Curp', 'RegistroPatronal', 'RfcPatronOrigen', 'OrigenRecurso', 'MontoRecursoPropio', '8','9','10','11','12','13','14','15','16','17']
RECEPTOR1_KEYS = ['NM', 'Receptor1', 'Curp', 'NumSeguridadSocial', 'FechaInicioRelLaboral', 'Antiguedad', 'TipoContrato', 'Sindicalizado', 'TipoJornada', 'TipoRegimen', 'NumEmpleado', 'Departamento', 'Puesto', 'RiesgoPuesto', 'PeriodicidadPago', 'Banco', 'CuentaBancaria' ]
RECEPTOR2_KEYS = ['NM', 'Receptor2', 'SalarioBaseCotApor', 'SalarioDiarioIntegrado', 'ClaveEntFed', '6','7','8','9','10','11','12','13','14','15','16','17']
SUBCONTRATACION_KEYS = ['NM', 'SubContratacion', 'claveRecep', 'RfcLabora', 'PorcentajeTiempo', '6','7','8','9','10','11','12','13','14','15','16','17']
PERCEPCIONES_KEY = ['NM', 'Percepciones', 'TotalSueldos', 'TotalSeparacionIndemnizacion', 'TotalJubilacionPensionRetiro', 'TotalGravado', 'TotalExento','8','9','10','11','12','13','14','15','16','17']
JUBILACION_KEYS = ['NM', 'JubilacionPensionRetiro', 'TotalUnaExhibicion', 'TotalParcialidad', 'MontoDiario', 'IngresoAcumulable', 'IngresoNoAcumulable','8','9','10','11','12','13','14','15','16','17']
SEPARACION_KEYS = ['NM', 'SeparacionIndemnizacion', 'TotalPagado', 'NumAnosServicio', 'UltimoSueldoMensOrd', 'IngresoAcumulable', 'IngresoNoAcumulable','8','9','10','11','12','13','14','15','16','17']
PERCEPCION_KEYS = ['NM', 'Percepcion', 'TipoPercepcion', 'Clave', 'Concepto', 'ImporteGravado', 'ImporteExento', 'ValorMercado', 'PrecioAlOtorgarse', '10','11','12','13','14','15','16','17']
HORAS_EXTRA_KEYS = ['NM', 'HorasExtra', 'ClavePercepcion', 'Dias', 'TipoHoras', 'HorasExtraAttr', 'ImportePagado','8','9','10','11','12','13','14','15','16','17']
DEDUCCIONES_KEYS = ['NM', 'Deducciones', 'TotalOtrasDeducciones', 'TotalImpuestosRetenidos', '5', '6','7','8','9','10','11','12','13','14','15','16','17']
DEDUCCION_KEYS = ['NM', 'Deduccion', 'TipoDeduccion', 'Clave', 'Concepto', 'Importe', '7','8','9','10','11','12','13','14','15','16','17']
OTROS_PAGOS_KEYS = ['NM', 'OtrosPagos' , 'SubsidioCausado', 'SaldoAFavor', 'Año', 'RemanenteSalFav', '7','8','9','10','11','12','13','14','15','16','17']
OTRO_PAGO_KEYS = ['NM', 'OtroPago', 'TipoOtroPago', 'Clave', 'Concepto', 'Importe', '7','8','9','10','11','12','13','14','15','16','17']
INCAPACIDAD_KEYS = ['NM', 'Incapacidad', 'DiasIncapacidad', 'TipoIncapacidad', 'ImporteMonetario', '6','7','8','9','10','11','12','13','14','15','16','17']

RETENCIONES_KEYS = ['Folio', 'Version', 'Folio_Cliente', 'FechaExp', 'CveRetenc', 'DescRetenc', 'RFCEmisor', 'NomDenRazSocE', 'CURPE', 'Nacionalidad', 'RFCRecep', 'NumRegIdTrib', 'NomDenRazSocR', 'CURPR', 'MesIni', 'MesFin', 'Ejerc', 'montoTotOperacion', 'montoTotGrav', 'montoTotExent', 'montoTotRet', 'Tipo_Documento', 'Notas', 'Notas02', 'Notas03', 'Misc01', 'Misc02', 'Misc03', 'Misc04', 'Misc05', 'Misc06', 'Misc07', 'Misc08', 'Misc09', 'Misc10', 'Misc11', 'Misc12', 'Misc13', 'Misc14', 'Misc15', 'Misc16', 'Misc17', 'Misc18', 'Misc19', 'Misc20', 'Misc21', 'Misc22', 'Misc23', 'Misc24', 'Misc25', 'Misc26', 'Misc27', 'Misc28', 'Misc29', 'Misc30', 'Misc31', 'Misc32', 'Misc33', 'Misc34', 'Misc35', 'Misc36', 'Misc37', 'Misc38', 'Misc39', 'Misc40', 'Misc41', 'Misc42', 'Misc43', 'Misc44', 'Misc45', 'Misc46', 'Misc47', 'Misc48', 'Misc49']
IMPUESTOS_RET_KEYS = ['TipoPagoRet','Impuesto','montoRet','BaseRet']
DIVIDENDOS_RET_KEYS = ['DV', 'header_div', 'CveTipDivOUtil', 'MontISRAcredRetMexico', 'MontISRAcredRetExtranjero', 'MontRetExtDivExt', 'TipoSocDistrDiv', 'MontISRAcredNal', 'MontDivAcumNal', 'MontDivAcumExt', 'Misc09', 'Misc10', 'Misc11', 'Misc12', 'Misc13', 'Misc14', 'Misc15']

RETENCIONES_KEYS_DB = ['Folio', 'Version', 'Folio_Cliente', 'Fecha_Expedicion', 'Clave_Retencion', 'Descripcion_Retencion', 'RFC_Emisor', 'NomDenRazSoc_Emisor', 'CURP_Emisor', 'Nacionalidad', 'RFC_Receptor', 'NumRegIdTrib', 'NomDenRazsoc_Receptor', 'CURP_Receptor', 'Periodo_Mes_Inicial', 'Periodo_Mes_Final', 'Periodo_Ejecicio_Fiscal', 'Monto_Total_Operacion', 'Monto_total_Gravado', 'Monto_Total_Exento', 'Monto_Total_Retenciones', 'Tipo_Documento', 'Notas', 'Notas02', 'Notas03', 'Misc01', 'Misc02', 'Misc03', 'Misc04', 'Misc05', 'Misc06', 'Misc07', 'Misc08', 'Misc09', 'Misc10', 'Misc11', 'Misc12', 'Misc13', 'Misc14', 'Misc15', 'Misc16', 'Misc17', 'Misc18', 'Misc19', 'Misc20', 'Misc21', 'Misc22', 'Misc23', 'Misc24', 'Misc25', 'Misc26', 'Misc27', 'Misc28', 'Misc29', 'Misc30', 'Misc31', 'Misc32', 'Misc33', 'Misc34', 'Misc35', 'Misc36', 'Misc37', 'Misc38', 'Misc39', 'Misc40', 'Misc41', 'Misc42', 'Misc43', 'Misc44', 'Misc45', 'Misc46', 'Misc47', 'Misc48', 'Misc49']
IMPUESTOS_RET_KEYS_DB = ['Impuesto_TipoPago','Impuesto_TipoImpuesto','Impuesto_Monto_retencion','Impuesto_Base_retencion']
DIVIDENDOS_RET_KEYS_DB = ['ComplementoDividendos', 'CompDivid', 'TipoDivid', 'MontISRAcredRetMexico', 'MontISRAcredRetExtranjero', 'MontRetExtDivExt', 'TipoSocDistrDiv', 'MontISRAcredNal', 'MontDivAcumNal', 'MontDivAcumExt', 'Misc09', 'Misc10', 'Misc11', 'Misc12', 'Misc13', 'Misc14', 'Misc15']

PAGO_KEYS = ['PA', 'FechaPago', 'FormaDePagoP', 'MonedaP', 'TipoCambioP', 'Monto', 'NumOperacion', 'RfcEmisorCtaOrd', 'NomBancoOrdExt', 'CtaOrdenante', 'RfcEmisorCtaBen', 'CtaBeneficiario', 'TipoCadPago', 'CertPago', 'CadPago', 'SelloPago']
DCTORE_KEYS = ['DR', 'IdDocumento', 'Serie', 'Folio', 'MonedaDR', 'TipoCambioDR', 'MetodoDePagoDR', 'NumParcialidad', 'ImpSaldoAnt', 'ImpPagado', 'ImpSaldoInsoluto']

CFDI_REL_KEYS = ['DR', 'TipoRelacion', 'UUID']
CANCEL_KEYS = ['document_id', 'taxpayer_id', 'uuid', 'notes', 'type']
REPROCESS_KEYS = ['document_id', 'name', 'type']

CANCEL_ESTATUS = {
  '201': '201 - UUID cancelado exitosamente.',
  '202': '202 - UUID previamente cancelado.',
  '203': '203 - No corresponde el RFC del Emisor y de quien solicita la cancelación.',
  '205': '205 - UUID no existe.',
  '708': '708 - No se pudo conectar al SAT, intentar más tarde.'
}

SAVE_JSON_TXT = True
SAVE_JSON_XML = True


linux = False
windows = False
try:
  oSys = sys.platform
  if oSys == 'linux2':
    linux = True
    TMP_PATH = "/tmp/"
  elif oSys in ('win32', 'win64'):
    windows = True
    TMP_PATH = "%s\\" % os.environ['tmp']
except Exception as e:
  logging.error('Plataforma error => %s' % str(e))

NAMESPACE = 'http://www.sat.gob.mx/cfd/3'
NSMAP = {'cfdi': NAMESPACE}

NOMINA = True

class CONGRESO(object):

  def __init__(self, payroll=None):
    try:
      #set_trace()
      self.payroll = payroll
      self.txt_path = self.payroll._txt.path
      #self.txt_name = os.path.basename(txt_path)
      self.txt_name = self.payroll.filename
      self.version_cfdi = '3.3'
      self.datos_json = {}
      self.taxpayer_id = None
      self.serial_number = None
      self.nomina_complement = True
      self.document_id = None
      self.invoice_type = 'N'
      #self.invoice_status = 'N'
      self.serial = None
      self.folio = None
      self.traslados = False
      self.retenciones = False
      self.retention_invoice = False
      self.log_f = None
      self.parser_success = True
      self.cfdi = None
      self.bad_file = False
      self.ret_json_db = {'retenciones': {}, 'dividendos': {}, 'impuestos': []}
      self.nomina_double = False
      self.reprocess_pdf = False
      self.percepciones_014 = []
      #self.cfdi_error_path = ERROR_PATH


      retentions_json = {
        'Version': '1.0',
        'FolioInt': '',
        'FechaExp': '',
        'CveRetenc': '',
        'DescRetenc': '',
        'Emisor': {
          'RFCEmisor': '',
          'NomDenRazSocE': '',
          'CURPE': '',
        },
        'Receptor': {
        'Nacionalidad': '',
        'Nacional':{
            'RFCRecep': '',
            'NomDenRazSocR': '',
            'CURPR': '',
        },
        'Extranjero': {'NumRegIdTrib': ''}
        },
        'Periodo':{
          'MesIni': '',
          'MesFin': '',
          'Ejerc': '',
        },
        'Totales': {
          'ImpRetenidos': [],
          'montoTotOperacion': '',
          'montoTotGrav': '',
          'montoTotExent': '',
          'montoTotRet': '',
        },
        'Complemento': { 
          'Dividendos': {
            'DividOUtil': [],
            'Remanente': [],
          },
        }
      }
      self.retentions_json_raw = deepcopy(retentions_json)
      self.process_invoice()

    except Exception, e:
      print 'Exception __init__() => %s' % str(e)
      self.log_f.error('Exception __init__() => %s' % str(e))

  def process_invoice(self):
    try:
      #set_trace()
      self.logs()
      result_parser = self.parse_invoice()
      if result_parser and not self.bad_file:
        result_json = self.create_json()
        if result_json or self.retention_invoice:
          result_generate = self.generate_xml()
          if result_generate:
            result_stamp = self.stamp()
            if result_stamp:
              pass
              #pdf_result = self.create_pdf()
              #if pdf_result['success']:     
              #  self.move_error_txt(only_json=True)
              #else:
              #  pdf_result = self.create_pdf()
              #  if pdf_result['success']:
              #    self.move_error_txt(only_json=True)
              #  else:
              #    self.move_error_txt()
            else:
              self.log_f.info("El CFDI no se timbró, no iniciará el proceso de creación de PDF")
              #self.move_error_txt()
          else:
            pass
            #self.move_error_txt()
        else:
          pass
          #self.move_error_txt()
      else:
        if not self.reprocess_pdf or self.bad_file:
          self.move_error_txt()
        
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
        self.move_error_txt()
      self.log_f.error('Exception process_invoice() => %s' % str(e))
      print "Exception process_invoice() => %s" % str(e)

  def logs(self, client=None):
    if not client:
      try:
        logging.disable(logging.NOTSET)
        logging.shutdown()
        #reload(logging)
        now =  datetime.now()
        self.logs_time = str(now.strftime('%Y_%m_%d'))
        path_logs = os.path.join(TMP_PATH, 'LOGS', self.logs_time)
        
        if not os.path.exists(path_logs):
          os.makedirs(path_logs)
        
        level=logging.INFO
        self.log_filename = self.txt_name.replace('.txt', '.log').replace('.print', '.log').replace('.can', '.log')
        
        if linux:
          self.log_path = '%s/%s' % (path_logs, self.log_filename)
        elif windows:
          self.log_path = '%s\\%s' % (path_logs, self.log_filename)
        l = logging.getLogger(self.log_path)
        formatter = logging.Formatter('%(levelname)-7.7s %(message)s')
        fileHandler = logging.FileHandler(self.log_path, mode='a')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)
        self.log_f = logging.getLogger(self.log_path)
      except Exception, e:
        print 'Exception logs() => %s' % str(e)
        pass
    else:
      try:
        now =  datetime.now()
        self.logs_time = str(now.strftime('%Y_%m_%d'))
        #path_logs = os.path.join(BASE_PATH, 'LOGS', self.logs_time)
        path_logs = os.path.join(TMP_PATH, 'LOGS', self.logs_time)
        if not os.path.exists(path_logs):
          os.makedirs(path_logs)
        logs_file_path_request = os.path.join(path_logs, '%s_SOAP_REQUEST.xml' % self.txt_name.replace('.txt', ''))
        logs_file_path_response = os.path.join(path_logs, '%s_SOAP_RESPONSE.xml' % self.txt_name.replace('.txt', ''))
        with open(logs_file_path_request, 'w+') as req_file:
          req_file.write('%s' % client.last_sent())
          #req_file.close()
        with open(logs_file_path_response, 'w+') as res_file:
          res_file.write('%s' % client.last_received())
          #res_file.close()
      except Exception, e:
        print 'Exception logs() => %s' % str(e)
        self.log_f.error('Exception logs() => %s' % str(e))

  def recursive_dict(self, r_dict, data):
    for key, value in r_dict.iteritems():
      if isinstance(value, dict):
        r_dict[key] = self.recursive_dict(value, data)
      if key in data.keys():
        r_dict[key] = data[key]
    return r_dict

  def parse_invoice(self):
    success = False
    message = ''
    try:
      txt_path = codecs.open(self.txt_path, 'r', 'utf-8')
      root_json = {'cabecera': '', 'detalle': {}, 'impuestos': '', 'auxiliar': ''}

      nomina_json = {
        'emisor': [], 
        'receptor': {'subcontratacion': []}, 
        'subcontratacion': [], 
        'percepciones': {'percepcion': [], 'jubilacion': [], 'separacion': [], 'horas_extra': {}}, 
        'deducciones': {'deduccion': []},
        'otrospagos':{'otropago': []},
        'incapacidad': [],
        'incapacidad_2': [],
      }
      
      detalle_list = []
      cont = 0

      for line in txt_path.readlines():
        line = line.strip().decode('utf-8')
        line = line.replace('[Hora]','').replace('[Fecha]','').replace('¬','').replace('~','').replace('*','').replace('\xc3\x82','')
        pipes = line.count('|')
        txt_data = line.split('|')
        if pipes == 192: # Cabecera
          txt_data = line.strip().split('|')
          cabecera_dict = dict(zip(CABECERA_KEYS, txt_data))
          root_json['cabecera'] = cabecera_dict
          if (root_json['cabecera']['RFC_Emisor'] in ('CBR060824732', 'CBR080430UZ4', 'CBR140313KA6')) and (root_json['cabecera']['RFC_Receptor'] not in ('XAXX010101000', 'XEXX010101000')) and ('nomina' not in root_json['cabecera']['Notas']):
            self.iedu = True
          if 'RD' in cabecera_dict['Numero_Factura']:
            self.donatarias_complement = True
        elif pipes == 98: # Detalle
          #set_trace()
          cont += 1
          detalle_dict = dict(zip(DETALLE_KEYS, txt_data))
          detalle_dict['Impuestos'] = {'Traslados': [], 'Retenciones': []}
          root_json['detalle'][str(cont)] = detalle_dict
        elif pipes == 17 and 'dividendos' in txt_data:
          self.invoice_type = 'D'
          div_ = dict(zip(DIVIDENDOS_RET_KEYS_DB , txt_data))
          self.ret_json_db['dividendos'] = div_
          txt_data[0] = txt_data[0].replace(u'\xc2\xac', '')
          dividendos = dict(zip(DIVIDENDOS_RET_KEYS, txt_data))
          self.retentions_json_raw['Complemento']['Dividendos']['DividOUtil'].append(dividendos)
          self.retention_json1['all'] = self.retentions_json_raw
          self.retention_json1['cabecera_div_pdf'] = raw_dict
        elif pipes == 17: # Auxiliar
          if 'NM|' in line:
            self.nomina_complement = True
            self.invoice_type = 'N'
            if 'encabezado|' in line:
              nomina_json.update(dict(zip(NOMINA_KEYS, txt_data)))
            elif 'emisor|' in line.lower():
              nomina_json['emisor'].append(dict(zip(EMISOR_KEYS, txt_data)))
            elif 'receptor1|' in line.lower():
              nomina_json['receptor'].update(dict(zip(RECEPTOR1_KEYS, txt_data)))
            elif 'receptor2|' in line.lower():
              nomina_json['receptor'].update(dict(zip(RECEPTOR2_KEYS, txt_data)))
            elif 'subcontratacion|' in line.lower():
              nomina_json['receptor']['subcontratacion'].append(dict(zip(SUBCONTRATACION_KEYS, txt_data)))
            elif 'percepciones|' in line.lower():
              nomina_json['percepciones'].update(dict(zip(PERCEPCIONES_KEY, txt_data)))
            elif 'percepcion|' in line.lower():
              nomina_json['percepciones']['percepcion'].append(dict(zip(PERCEPCION_KEYS, txt_data)))
            elif 'jubilacion|' in line.lower():
              nomina_json['percepciones']['jubilacion'].append(dict(zip(JUBILACION_KEYS, txt_data)))
            elif 'separacionindemnizacion|' in line.lower():
              nomina_json['percepciones']['separacion'].append(dict(zip(SEPARACION_KEYS, txt_data)))
            elif 'horasextra|' in line.lower():
              horas_extra = dict(zip(HORAS_EXTRA_KEYS, txt_data))
              if horas_extra['ClavePercepcion'] not in nomina_json['percepciones']['horas_extra']:
                nomina_json['percepciones']['horas_extra'].update({horas_extra['ClavePercepcion']: [horas_extra]})
              else:
                nomina_json['percepciones']['horas_extra'][horas_extra['ClavePercepcion']].append(horas_extra)
            elif 'deducciones|' in line.lower():
              nomina_json['deducciones'].update(dict(zip(DEDUCCIONES_KEYS, txt_data)))
            elif 'deduccion|' in line.lower():
              nomina_json['deducciones']['deduccion'].append(dict(zip(DEDUCCION_KEYS, txt_data)))
            elif 'otrospagos|' in line.lower():
              nomina_json['otrospagos'].update(dict(zip(OTROS_PAGOS_KEYS, txt_data)))
            elif 'otropago|' in line.lower():
              nomina_json['otrospagos']['otropago'].append(dict(zip(OTRO_PAGO_KEYS, txt_data)))
            elif 'incapacidad|' in line.lower():
              nomina_json['incapacidad'].append(dict(zip(INCAPACIDAD_KEYS, txt_data)))
            elif 'incapacidad_2|' in line.lower():
              nomina_json['incapacidad_2'].append(dict(zip(INCAPACIDAD_KEYS, txt_data)))
        elif pipes == 74:
          self.invoice_type = 'R'
          ret = dict(zip(RETENCIONES_KEYS_DB, txt_data))
          self.ret_json_db['retenciones'] = ret
          self.retention_invoice = True
          txt_data[0] = txt_data[0].replace(u'\xef\xbb\xbf', '').replace('~', '')
          raw_dict = dict(zip(RETENCIONES_KEYS, txt_data))
          self.retentions_json_raw = self.recursive_dict(self.retentions_json_raw, raw_dict)
        elif pipes == 3 and self.retention_invoice:
          imp = dict(zip(IMPUESTOS_RET_KEYS_DB, txt_data))
          self.ret_json_db['impuestos'].append(imp)
          txt_data[0] = txt_data[0].replace(u'\xc2\xac', '')
          imp_retenidos = dict(zip(IMPUESTOS_RET_KEYS, txt_data))
          self.retentions_json_raw['Totales']['ImpRetenidos'].append(imp_retenidos)
        elif pipes == 2 and self.reprocess_pdf: # Reprocess PDF
          reprocess_dic = dict(zip(REPROCESS_KEYS, txt_data))
          self.reprocess_lst.append(reprocess_dic)
        #elif pipes == 4 and self.cancelation:
        #  cancel_dic = dict(zip(CANCEL_KEYS, txt_data))
        #  self.cancel_lst.append(cancel_dic)
      #txt_path.close()
      if self.reprocess_pdf:
        now =  datetime.now()
        self.log_f.info("====== Fecha: %s | Reproceso de PDF ======" % now.strftime('%Y/%m/%d %H:%M:%S'))
        self.f_reprocess_pdf()
      #elif self.cancelation:
      #  now =  datetime.now()
      #  self.log_f.info("====== Fecha: %s | Cancelación de CFDI ======" % now.strftime('%Y/%m/%d %H:%M:%S'))
      #  self.cancel()
      
      self.datos_json = root_json
      self.nomina_json = nomina_json
      
      # @TODO MOVER A PROCESADOS
      #if not self.reprocess_pdf:
      #  try:
      #    if os.path.exists(os.path.join(TXT_SUCCESS, self.txt_name)):
      #      os.remove(os.path.join(TXT_SUCCESS, self.txt_name))
      #    if os.path.isfile(self.txt_path):
      #      os.rename(self.txt_path, os.path.join(TXT_SUCCESS, self.txt_name))
      #  except Exception as e:
      #    self.log_f.error('mv entrada => %s' % str(e))
      #    pass
      #  if SAVE_JSON_TXT:
      #    if os.path.exists(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json1'))):
      #      os.remove(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json1')))
      #    with open(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json1')), 'w+') as json_file:
      #      json.dump(root_json, json_file, sort_keys=True, indent=4, ensure_ascii=True)
      #      #json_file.close()
      #    # JSON1 para RETENCIONES
      #    if self.retention_invoice:
      #      with open(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json1')), 'w+') as json_file:
      #        json.dump(self.retention_json1, json_file, sort_keys=True, indent=4, ensure_ascii=True)
      #        #json_file.close()

      #  #Set issuer RFC as log header
      #  now =  datetime.now()
      #  if not self.retention_invoice:
      #    self.log_f.info("#Fecha de proceso: {} #RFC Emisor: {} #RFC Receptor: {}".format(now.strftime('%Y-%m-%d %H:%M:%S'), root_json['cabecera']['RFC_Emisor'], root_json['cabecera']['RFC_Receptor']))
      #  else:
      #    try:
      #     self.log_f.info("#Fecha de proceso: {} #RFC Emisor: {} #RFC Receptor: {}".format(now.strftime('%Y-%m-%d %H:%M:%S'), self.retentions_json_raw['Emisor']['RFCEmisor'], self.retentions_json_raw['Receptor']['Nacional']['RFCRecep']))
      #    except:
      #      self.log_f.info("#Fecha de proceso: {} #RFC Emisor: {} #RFC Receptor: {}".format(now.strftime('%Y-%m-%d %H:%M:%S'), self.retentions_json_raw['Emisor']['RFCEmisor'], self.retentions_json_raw['Receptor']['Extranjero']['NumRegIdTrib']))
      #  #set_trace()
      success = True
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      success = False
      print 'Exception parse_invoice() Message => {} | Error => {}'.format(message, str(e))
      self.log_f.error('Exception parse_invoice() Message => {} | Error => {}'.format(message, str(e)))
      self.parser_success = False
    return success

  def create_json(self):
    success = False
    try:
      self.cfdi_json = {}
      if not self.retention_invoice:
        cfdi_json = self.create_json_33()
        success = True
        self.cfdi_json = cfdi_json

        # @TODO GUARDAR archivo.json en PROCESADOS
        #if SAVE_JSON_XML:
        #  if os.path.exists(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json2'))):
        #    os.remove(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json2')))
        #  with open(os.path.join(TXT_SUCCESS, self.txt_name.replace('.txt', '.json2')), 'w') as json_file:
        #    json.dump(cfdi_json, json_file, sort_keys=True, indent=4, ensure_ascii=False)
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.parser_success = False
      self.log_f.error("Exception create_json() | {}".format(str(e)))
    return success

  def generate_xml(self):
    success = False
    try:
      if not self.retention_invoice:
        xml = self.generate_xml_33()
      else:
        xml = self.generate_retention_10()
      if xml:
        success = self.get_original_string()
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.parser_success = False
      print "Exception generate_xml() | {}".format(str(e))
      self.log_f.error("Exception generate_xml() | {}".format(str(e)))

    return success
  
  def generate_retention_10(self):
    r_xml = False
    try:
      self.date = datetime.now().replace(microsecond=0).isoformat()
      self.retentions_json_raw = self.remove_empty_from_dict(self.retentions_json_raw)
      emisor_ret = self.retentions_json_raw.pop('Emisor') if 'Emisor' in self.retentions_json_raw else None
      receptor_ret = self.retentions_json_raw.pop('Receptor') if 'Receptor' in self.retentions_json_raw else None
      nacional_ret = receptor_ret.pop('Nacional') if 'Nacional' in receptor_ret else None
      extranjero_ret = receptor_ret.pop('Extranjero') if 'Extranjero' in receptor_ret else None
      periodo = self.retentions_json_raw.pop('Periodo') if 'Periodo' in self.retentions_json_raw else None
      totales = self.retentions_json_raw.pop('Totales') if 'Totales' in self.retentions_json_raw else None
      imp_ret = totales.pop('ImpRetenidos') if 'ImpRetenidos' in totales else None
      complemento = self.retentions_json_raw.pop('Complemento') if 'Complemento' in self.retentions_json_raw else None
      # add Totales to Retenciones
      if totales:
        if imp_ret:
          imp_ret_list = []
          for ir in imp_ret:
            imp_ret_list.append(sub_retenciones.ImpRetenidosTypeSub(**ir))
          totales['ImpRetenidos'] = imp_ret_list
        self.retentions_json_raw['Totales'] = sub_retenciones.TotalesTypeSub(**totales)
        # add Periodo to Retenciones
      if periodo:
        self.retentions_json_raw['Periodo'] = sub_retenciones.PeriodoTypeSub(**periodo)
      # add Receptor to Retenciones
      if receptor_ret:
        if nacional_ret:
          self.receiver_id = nacional_ret['RFCRecep']
          receptor_ret['Nacional'] = sub_retenciones.NacionalTypeSub(**nacional_ret)
        if extranjero_ret:
          self.receiver_id = extranjero_ret['NumRegIdTrib']
          receptor_ret['Extranjero'] = sub_retenciones.ExtranjeroTypeSub(**extranjero_ret)
        self.retentions_json_raw['Receptor'] = sub_retenciones.ReceptorTypeSub(**receptor_ret)
      # add Emisor to Retenciones
      if emisor_ret:
        emisor_ret['RFCEmisor'] = 'EKU9003173C9'
        self.taxpayer_id = 'EKU9003173C9'
        self.serial_number = CSD_DICT[self.taxpayer_id].keys()[0]
        self.retentions_json_raw['Emisor'] = sub_retenciones.EmisorTypeSub(**emisor_ret)
      self.retentions_json_raw['NumCert'] = CSD_DICT[self.taxpayer_id].keys()[0]
      cfdi_obj = sub_retenciones.RetencionesSub(**self.retentions_json_raw)
      if complemento:
        dividendos = complemento.pop('Dividendos') if 'Dividendos' in complemento else None
        if dividendos:
          dividendos['Version'] = '1.0'
          self.namespace = 'dividendos:'
          remanente = dividendos.pop('Remanente') if 'Remanente' in dividendos else None
          divo = dividendos.pop('DividOUtil') if 'DividOUtil' in dividendos else None
          if remanente:
            dividendos['Remanente'] = sub_dividendos.RemanenteTypeSub(**remanente)
          if divo:
            for dou in divo:
              print dou.pop('header_div') if 'header_div' in dou else None
              print dou.pop('DV') if 'DV' in dou else None
              print dou.pop('MontRetExtDivExt') if 'MontRetExtDivExt' in dou and dou['MontRetExtDivExt'] and float(dou['MontRetExtDivExt']) == 0.0 else None
              print dou.pop('MontISRAcredNal') if 'MontISRAcredNal' in dou and dou['MontISRAcredNal'] and float(dou['MontISRAcredNal']) == 0.0 else None
              print dou.pop('MontDivAcumNal') if 'MontDivAcumNal' in dou and dou['MontDivAcumNal'] and float(dou['MontDivAcumNal']) == 0.0 else None
              print dou.pop('MontDivAcumExt') if 'MontDivAcumExt' in dou and dou['MontDivAcumExt'] and float(dou['MontDivAcumExt']) == 0.0 else None
              dividendos['DividOUtil'] = sub_dividendos.DividOUtilTypeSub(**dou)
          retention_complement_obj = sub_dividendos.DividendosSub(**dividendos)
        complemento_obj = sub_retenciones.ComplementoTypeSub()
        complemento_obj.add_anytypeobjs_(retention_complement_obj)
        cfdi_obj.set_Complemento(complemento_obj)
      output = StringIO.StringIO()
      cfdi_obj.export(output, 0, pretty_print=False, namespace_complement_=self.namespace)
      self.cfdi = output.getvalue()
      parser = ET.XMLParser(ns_clean=True)
      self.cfdi_etree = ET.fromstring(self.cfdi, parser=parser)
      self.log_f.info("Creación de XML: OK")
      r_xml = True
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.log_f.error("Creación de XML: Error")
      print 'Exception generate_retention_10() | {}'.format(str(e))
      self.log_f.error('Exception generate_retention_10() | {}'.format(str(e)))

    return r_xml

  def generate_xml_33(self):
    r_xml = False
    try:
      cfdi_json = self.cfdi_json
      complemento_obj = None
      # CFDI 3.3
      ns_ = 'xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nomina12="http://www.sat.gob.mx/nomina12" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd"'
      cfdi_json['Comprobante']['ns_'] = ns_
      #set_trace()
      comprobante = cfdi_json.pop('Comprobante')
      emisor = cfdi_json.pop('Emisor')
      receptor = cfdi_json.pop('Receptor')
      conceptos = cfdi_json.pop('Conceptos')
      _impuestos = cfdi_json.pop('Impuestos') if 'Impuestos' in cfdi_json else None
      # Comprobante
      try:
       self.serial = comprobante['Serie']
      except:
        pass
      
      try:
        self.folio = comprobante['Folio']
      except:
        pass
      
      try:
        self.cfdi_obj = CFDI_33.Comprobante(**comprobante)
      except Exception as e:
        print "Exception generate_xml_33() Comprobante | {}".format(str(e))
        self.log_f.error("Exception generate_xml_33() Comprobante | {}".format(str(e)))
      # CFDI RELACIONADO
      if self.cfdi_rel:
        #set_trace()
        try:
          x = self.cfdi_rel_lst[0]
          TipoRelacion = x['TipoRelacion']
          cfdi_rels_obj = CFDI_33.CfdiRelacionadosType(TipoRelacion=TipoRelacion)
          for cr in self.cfdi_rel_lst:
            UUID = cr['UUID']
            cfdi_rel_obj = CFDI_33.CfdiRelacionadoType(UUID=UUID)
            cfdi_rels_obj.add_CfdiRelacionado(cfdi_rel_obj)
          self.cfdi_obj.set_CfdiRelacionados(cfdi_rels_obj)
        except Exception as e:
          print "Exception generate_xml_33() CfdiRelacionados => %s" % str(e)
          self.log_f.error("Exception generate_xml_33() CfdiRelacionados => %s" % str(e))
      # Emisor
      try:
        try:
          emisor_dom = emisor.pop('Emisor_dom')
        except:
          pass
        emisor_obj = CFDI_33.EmisorType(**emisor)
        self.cfdi_obj.set_Emisor(emisor_obj)
      except Exception as e:
        print 'Exception generate_xml_33() Emisor => %s' % str(e)
        self.log_f.error('Exception generate_xml_33() Emisor => %s' % str(e))
      # Receptor
      try:
        try:
          receptor_dom = receptor.pop('Receptor_dom')
        except:
          pass
        receptor_obj = CFDI_33.ReceptorType(**receptor)
        self.cfdi_obj.set_Receptor(receptor_obj)
      except Exception as e:
        print 'Exception generate_xml_33() Receptor => %s' % str(e)
        self.log_f.error('Exception generate_xml_33() Receptor => %s' % str(e))
      # Conceptos
      #set_trace()
      try:
        imp_g = False
        traslados_g = False
        retenciones_g = False
        conceptos_obj = CFDI_33.ConceptosType()
        for c in conceptos:
          imp = False
          traslados = False
          retenciones = False
          try:
            impuestos = c.pop('Impuestos')
          except:
            pass
          if self.nomina_complement:
            try:
              #descuento = None
              descuento = self.nomina_json['TotalDeducciones']
              if descuento != "":
                c['Descuento'] = descuento
            except:
              pass
            unidad = c.pop('Unidad')
          concepto_obj = CFDI_33.ConceptoType(**c)
          
          if not self.nomina_complement:
            impuestos_obj = CFDI_33.ImpuestosType()
            try:
              if len(impuestos['Traslados']):
                traslados_obj = CFDI_33.TrasladosType()
                for it in impuestos['Traslados']:
                  if it['TipoFactor'] != 'Exento':
                    if it['Importe'] != '0.00':
                      traslados = True
                      traslados_g = True
                      traslado_obj = CFDI_33.TrasladoType(**it)
                      traslados_obj.add_Traslado(traslado_obj)
                  else:
                    traslados = True
                    traslados_g = True
                    traslado_obj = CFDI_33.TrasladoType(**it)
                    traslados_obj.add_Traslado(traslado_obj)
                if traslados:
                  imp = True
                  imp_g = True
                  impuestos_obj.set_Traslados(traslados_obj)
            except:
              pass
            try:
              if len(impuestos['Retenciones']):
                retenciones_obj = CFDI_33.RetencionesType()
                for ir in impuestos['Retenciones']:
                  if ir['Importe'] != '0.00':
                    retenciones = True
                    retenciones_g = True
                    retencion_obj = CFDI_33.RetencionType(**ir)
                    retenciones_obj.add_Retencion(retencion_obj)
                if retenciones:
                  imp = True
                  imp_g = True
                  impuestos_obj.set_Retenciones(retenciones_obj)
            except:
              pass
          else:
            pass
          if imp:
            concepto_obj.set_Impuestos(impuestos_obj)
          conceptos_obj.add_Concepto(concepto_obj)
        self.cfdi_obj.set_Conceptos(conceptos_obj)
      except Exception as e:
        print 'Exception generate_xml_33() Conceptos => %s' % str(e)
        self.log_f.error('Exception generate_xml_33() Conceptos => %s' % str(e))
      # Impuestos
      #set_trace()
      try:
        _impuestos_obj = None
        if imp_g:
          attr = {}
          tra = {}
          ret = {}
          if traslados_g:
            attr['TotalImpuestosTrasladados'] = _impuestos['totalImpuestosTrasladados']
            traslados_obj = CFDI_33.TrasladosType5()
            for i in _impuestos['Traslados']:
              tra['Impuesto'] = i['impuesto']
              tra['TipoFactor'] = i['TipoFactor']
              tra['TasaOCuota'] = i['tasa']
              tra['Importe'] = i['importe']
              traslado_obj = CFDI_33.TrasladoType6(**tra)
              tra = {}
              traslados_obj.add_Traslado(traslado_obj)
          if retenciones_g:
            attr['TotalImpuestosRetenidos'] = _impuestos['totalImpuestosRetenidos']
            retenciones_obj = CFDI_33.RetencionesType3()
            for i in _impuestos['Retenciones']:
              ret['Impuesto'] = i['impuesto']
              ret['Importe'] = i['importe']
              retencion_obj = CFDI_33.RetencionType4(**ret)
              ret = {}
              retenciones_obj.add_Retencion(retencion_obj)
          _impuestos_obj = CFDI_33.ImpuestosType2(**attr)
          if traslados_g:
            _impuestos_obj.set_Traslados(traslados_obj)
          if retenciones_g:
            _impuestos_obj.set_Retenciones(retenciones_obj)
        else:
          pass
        if not self.nomina_complement:
          #_impuestos_obj = CFDI_33.ImpuestosType2()
          if _impuestos_obj is not None:
            self.cfdi_obj.set_Impuestos(_impuestos_obj)
      except Exception as e:
        self.log_f.error("Exception generate_xml_33() Impuestos => %s" % str(e))
        print 'Exception generate_xml_33() Impuestos => %s' % str(e)
      
      # Nomina1.2
      if self.nomina_complement:
        try:
          self.namespace = 'nomina12:'
          self.nomina_json = self.remove_empty_from_dict(self.nomina_json)
          #print self.nomina_json.pop('NM') if 'NM' in self.nomina_json else None
          self.nomina_json.pop('NM') if 'NM' in self.nomina_json else None
          #print self.nomina_json.pop('encabezado') if 'encabezado' in self.nomina_json else None
          self.nomina_json.pop('encabezado') if 'encabezado' in self.nomina_json else None
          if 'emisor' in self.nomina_json:
            emisor = self.nomina_json.pop('emisor')
            for em in emisor:
              #print em.pop('NM') if 'NM' in em else None
              em.pop('NM') if 'NM' in em else None
              #print em.pop('Emisor') if 'Emisor' in em else None
              print em.pop('Emisor') if 'Emisor' in em else None
              entidad_sncf = {'EntidadSNCF': {}}
              entidad_sncf_obj = None
              if 'OrigenRecurso' in em:
                entidad_sncf['EntidadSNCF'].update({'OrigenRecurso': em.pop('OrigenRecurso')})
              if 'MontoRecursoPropio' in em:
                entidad_sncf['EntidadSNCF'].update({'MontoRecursoPropio': em.pop('MontoRecursoPropio')})
              if entidad_sncf['EntidadSNCF']:
                entidad_sncf_obj = EntidadSNCFType(**entidad_sncf['EntidadSNCF'])
                em.update({'EntidadSNCF': entidad_sncf_obj})
              nom_emisor_obj = NomEmisorType(**em)
              self.nomina_json.update({'Emisor': nom_emisor_obj})
          if 'receptor' in self.nomina_json:
            receptor = self.nomina_json.pop('receptor')
            #receptor['SalarioDiarioIntegrado'] = self.datos_json['cabecera']['Misc05']
            if receptor.get('TipoRegimen') != '09':
              receptor['SalarioDiarioIntegrado'] = receptor['SalarioDiarioIntegrado']
            #print receptor.pop('NM') if 'NM' in receptor else None
            receptor.pop('NM') if 'NM' in receptor else None
            #print receptor.pop('Receptor1') if 'Receptor1' in receptor else None  
            receptor.pop('Receptor1') if 'Receptor1' in receptor else None  
            #print receptor.pop('Receptor2') if 'Receptor2' in receptor else None  
            receptor.pop('Receptor2') if 'Receptor2' in receptor else None  
            if 'subcontratacion' in receptor:
              subcontratacion = receptor.pop('subcontratacion')
              #print receptor.pop('NM') if 'NM' in receptor else None
              receptor.pop('NM') if 'NM' in receptor else None
              #print receptor.pop('subcontratacion') if 'subcontratacion' in receptor else None
              receptor.pop('subcontratacion') if 'subcontratacion' in receptor else None
              subcontratacion_list = []
              for sub in subcontratacion:
                #print sub.pop('NM') if 'NM' in sub else None
                sub.pop('NM') if 'NM' in sub else None
                #print sub.pop('SubContratacion') if 'SubContratacion' in sub else None
                sub.pop('SubContratacion') if 'SubContratacion' in sub else None
                #print sub.pop('claveRecep') if 'claveRecep' in sub else None
                sub.pop('claveRecep') if 'claveRecep' in sub else None
                subcontratacion_list.append(SubContratacionType(**sub))
              receptor.update({'SubContratacion': subcontratacion_list})
            nom_receptor_obj = NomReceptorType(**receptor)
            self.nomina_json.update({'Receptor': nom_receptor_obj})

          if 'deducciones' in self.nomina_json:
            deducciones = self.nomina_json.pop('deducciones')
            #print deducciones.pop('NM') if 'NM' in deducciones else None
            deducciones.pop('NM') if 'NM' in deducciones else None
            #print deducciones.pop('Deducciones') if 'Deducciones' in deducciones else None  
            deducciones.pop('Deducciones') if 'Deducciones' in deducciones else None  
            if 'deduccion' in deducciones:
              deduccion = deducciones.pop('deduccion')
              deduccion_list = []
              for de in deduccion:
                #print de.pop('NM') if 'NM' in de else None
                de.pop('NM') if 'NM' in de else None
                #print de.pop('Deduccion') if 'Deduccion' in de else None  
                de.pop('Deduccion') if 'Deduccion' in de else None  
                deduccion_list.append(NomDeduccionType(**de))
              deducciones.update({'Deduccion': deduccion_list})
            deducciones_obj = NomDeduccionesType(**deducciones)
            self.nomina_json.update({'Deducciones': deducciones_obj})

          if 'percepciones' in self.nomina_json:
            percepciones = self.nomina_json.pop('percepciones')
            #print percepciones.pop('NM') if 'NM' in percepciones else None
            percepciones.pop('NM') if 'NM' in percepciones else None
            #print percepciones.pop('Percepciones') if 'Percepciones' in percepciones else None  
            percepciones.pop('Percepciones') if 'Percepciones' in percepciones else None  
            if 'jubilacion' in percepciones:
              jubilacion = percepciones.pop('jubilacion')
              jubilacion_list = []
              for ju in jubilacion:
                #print ju.pop('NM') if 'NM' in ju else None
                ju.pop('NM') if 'NM' in ju else None
                #print ju.pop('JubilacionPensionRetiro') if 'JubilacionPensionRetiro' in ju else None
                ju.pop('JubilacionPensionRetiro') if 'JubilacionPensionRetiro' in ju else None
                jubilacion_list.append(JubilacionPensionRetiroType(**ju))
              percepciones.update({'JubilacionPensionRetiro': jubilacion_list})
            if 'separacion' in percepciones:
              separacion = percepciones.pop('separacion')
              separacion_obj = None
              for se in separacion:
                #print se.pop('NM')
                se.pop('NM')
                #print se.pop('SeparacionIndemnizacion')
                se.pop('SeparacionIndemnizacion')
                separacion_obj = SeparacionIndemnizacionType(**se)
                percepciones.update({'SeparacionIndemnizacion': separacion_obj})
            if 'percepcion' in percepciones:
              percepcion = percepciones.pop('percepcion')
              percepcion_list = []
              for pe in percepcion:
                #print pe.pop('NM') if 'NM' in pe else None
                pe.pop('NM') if 'NM' in pe else None
                #print pe.pop('Percepcion') if 'Percepcion' in pe else None
                pe.pop('Percepcion') if 'Percepcion' in pe else None
                if 'horas_extra' in percepciones and pe['Clave'] in percepciones['horas_extra']:
                  #horas_extra = percepciones.pop('horas_extra')
                  horas_e = percepciones['horas_extra'].pop(pe['Clave'])
                  horas_extra_list = []
                  for he in horas_e:
                    #print he.pop('NM') if 'NM' in he else None
                    he.pop('NM') if 'NM' in he else None
                    #print he.pop('HorasExtra') if 'HorasExtra' in he else None
                    he.pop('HorasExtra') if 'HorasExtra' in he else None
                    #print he.pop('ClavePercepcion') if 'ClavePercepcion' in he else None
                    he.pop('ClavePercepcion') if 'ClavePercepcion' in he else None
                    if 'HorasExtraAttr' in he:
                      horas_extra_attr = he.pop('HorasExtraAttr')
                      he.update({'HorasExtra': horas_extra_attr})
                    horas_extra_list.append(HorasExtraType(**he))
                  pe.update({'HorasExtra': horas_extra_list})
                #set_trace()
                if pe['TipoPercepcion'] != '014':
                  percepcion_list.append(NomPercepcionType(**pe))
                else:
                  self.percepciones_014.append(pe)
              percepciones.update({'Percepcion': percepcion_list})
            #set_trace()
            if 'horas_extra' in percepciones:
              he_trash = percepciones.pop('horas_extra')
            percepciones_obj = NomPercepcionesType(**percepciones)
            self.nomina_json.update(**{'Percepciones': percepciones_obj})

          #set_trace()
          if 'otrospagos' in self.nomina_json:
            otros_pagos = self.nomina_json.pop('otrospagos')
            #print otros_pagos.pop('NM') if 'NM' in otros_pagos else None
            otros_pagos.pop('NM') if 'NM' in otros_pagos else None
            #print otros_pagos.pop('OtrosPagos') if 'OtrosPagos' in otros_pagos else None
            otros_pagos.pop('OtrosPagos') if 'OtrosPagos' in otros_pagos else None            
            if 'otropago' in otros_pagos:
              otro_pago = otros_pagos.pop('otropago')
              otro_pago_list = []
              for op in otro_pago:
                #print op.pop('NM') if 'NM' in op else None
                op.pop('NM') if 'NM' in op else None
                #print op.pop('OtroPago') if 'OtroPago' in op else None
                op.pop('OtroPago') if 'OtroPago' in op else None
                if 'SubsidioCausado' in otros_pagos:
                  subsidio_causado = otros_pagos.pop('SubsidioCausado')
                  op.update({'SubsidioAlEmpleo': SubsidioAlEmpleoType(**{'SubsidioCausado': subsidio_causado})})
                ano = otros_pagos.pop('Año') if 'Año' in otros_pagos else None
                saldo_favor = otros_pagos.pop('SaldoAFavor') if 'SaldoAFavor' in otros_pagos else None
                remanente = otros_pagos.pop('RemanenteSalFav') if 'RemanenteSalFav' in otros_pagos else None
                if ano or saldo_favor or remanente:
                  op.update({'CompensacionSaldosAFavor': CompensacionSaldosAFavorType(**{'Ano': ano, 'SaldoAFavor': saldo_favor, 'RemanenteSalFav': remanente})})
                otro_pago_list.append(OtroPagoType(**op))
              self.nomina_json.update({'OtrosPagos': OtrosPagosType(**{'OtroPago': otro_pago_list})})

          if 'incapacidad' in self.nomina_json:
            incapacidad = self.nomina_json.pop('incapacidad')
            incapacidad_list = []
            for inc in incapacidad:
              #print inc.pop('NM') if 'NM' in inc else None
              inc.pop('NM') if 'NM' in inc else None
              #print inc.pop('Incapacidad') if 'Incapacidad' in inc else None
              inc.pop('Incapacidad') if 'Incapacidad' in inc else None
              incapacidad_list.append(IncapacidadType(**inc))
            self.nomina_json.update({'Incapacidades': IncapacidadesType(**{'Incapacidad': incapacidad_list})})
          if 'incapacidad_2' in self.nomina_json:
            self.nomina_double = True
            nomina_json_2 = deepcopy(self.nomina_json)
            
            #print nomina_json_2.pop('incapacidad') if 'incapacidad' in nomina_json_2 else None
            nomina_json_2.pop('incapacidad') if 'incapacidad' in nomina_json_2 else None
            #print nomina_json_2.pop('OtrosPagos') if 'OtrosPagos' in nomina_json_2 else None
            nomina_json_2.pop('OtrosPagos') if 'OtrosPagos' in nomina_json_2 else None
            #print nomina_json_2.pop('Deducciones') if 'Deducciones' in nomina_json_2 else None
            nomina_json_2.pop('Deducciones') if 'Deducciones' in nomina_json_2 else None
            #print nomina_json_2.pop('TotalDeducciones') if 'TotalDeducciones' in nomina_json_2 else None
            nomina_json_2.pop('TotalDeducciones') if 'TotalDeducciones' in nomina_json_2 else None
            #print nomina_json_2.pop('TotalOtrosPagos') if 'TotalOtrosPagos' in nomina_json_2 else None
            nomina_json_2.pop('TotalOtrosPagos') if 'TotalOtrosPagos' in nomina_json_2 else None
            
            percepcion_list = []
            total_percepciones = 0.00
            total_gravado = 0.00
            total_exento = 0.00
            
            for pe in self.percepciones_014:
              total_gravado += float(pe['ImporteGravado'])
              total_exento += float(pe['ImporteExento'])
              percepcion_list.append(NomPercepcionType(**pe))
            
            total_percepciones = (total_gravado + total_exento)

            nomina_json_2['TotalPercepciones'] = total_percepciones
            percepciones['TotalSueldos'] = total_percepciones
            percepciones['TotalGravado'] = total_gravado
            percepciones['TotalExento'] = total_exento
            percepciones.update({'Percepcion': percepcion_list})
            percepciones_obj = NomPercepcionesType(**percepciones)
            nomina_json_2.update(**{'Percepciones': percepciones_obj})

            incapacidad_2 = nomina_json_2.pop('incapacidad_2')

            incapacidad_list_2 = []
            for inc in incapacidad_2:
              #print inc.pop('NM') if 'NM' in inc else None
              inc.pop('NM') if 'NM' in inc else None
              #print inc.pop('Incapacidad') if 'Incapacidad' in inc else None
              inc.pop('Incapacidad') if 'Incapacidad' in inc else None
              incapacidad_list_2.append(IncapacidadType(**inc))
            nomina_json_2.update({'Incapacidades': IncapacidadesType(**{'Incapacidad': incapacidad_list_2})})
          
          #print self.nomina_json.pop('incapacidad_2') if 'incapacidad_2' in self.nomina_json else None
          self.nomina_json.pop('incapacidad_2') if 'incapacidad_2' in self.nomina_json else None
          nomina_obj = Nomina(**self.nomina_json)
          complemento_obj = CFDI_33.ComplementoType()
          complemento_obj.add_anytypeobjs_(nomina_obj)
          if self.nomina_double:
            nomina_obj_2 = Nomina(**nomina_json_2)
            complemento_obj.add_anytypeobjs_(nomina_obj_2)
          self.cfdi_obj.set_Complemento(complemento_obj)
        except Exception as e:
          print "Exception generate_xml_33() Nomina1.2 => %s" % str(e)
          self.log_f.error("Exception generate_xml_33() Nomina1.2 => %s" % str(e))
          raise Exception(e)

      try: # Generate CFDI-XML
        output = StringIO.StringIO()
        self.cfdi_obj.export(output, 0, pretty_print=True, namespace_complement_=self.namespace)
        self.cfdi = output.getvalue()  
        #print self.cfdi
        parser = etree.XMLParser(ns_clean=True)      
        self.cfdi_etree = ET.fromstring(self.cfdi, parser=parser)
        self.log_f.info("Creación de XML: OK")
        r_xml = True
      except Exception, e:
        print "Exception Export => %s" % str(e)
        self.log_f.error("Exception Export => %s" % str(e))
        self.log_f.error("Creación de XML: Error")

    except Exception as e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      print 'Exception generate_xml_33() => %s' % str(e)
      self.log_f.error('Exception generate_xml_33() => %s' % str(e))
    return r_xml

  def create_json_33(self):
    try:
      invoice_json = {}
      datos_json = self.datos_json
      #time = datetime.now()
      #datetime_now = str(time.strftime('%Y-%m-%dT%H:%M:%S'))
      #rfc  = ''
      #if datos_json['cabecera']['RFC_Emisor']:
      #  rfc =  'ACO560518KW7' if not self.nomina_complement else 'TCM970625MB1'
      #else: 
      #  self.log_f.error('EL RFC EMISOR NO ES VALIDO')
      try:
        invoice_json = {
          'Comprobante': {
            'Version': '3.3',
            'Serie': datos_json['cabecera']['Serie_Comprobante'],
            'Folio': datos_json['cabecera']['Folio'],
            'Fecha': datos_json['cabecera']['Fecha'],
            #'Fecha': datetime_now,
            'FormaPago': datos_json['cabecera']['FormaPago'],
            'CondicionesDePago': datos_json['cabecera']['Condiciones_Pago'],
            'SubTotal': datos_json['cabecera']['Monto_SubTotal'],
            'Descuento': datos_json['cabecera']['Monto_Descuento'],
            'Moneda': datos_json['cabecera']['Cod_Moneda'],
            'TipoCambio': datos_json['cabecera']['Tasa_Divisa'],
            'Total': datos_json['cabecera']['Monto_Total'],
            'TipoDeComprobante': datos_json['cabecera']['TipoCFD'],
            'MetodoPago': datos_json['cabecera']['Metodo_Pago'], # catCFDI:c_MetodoPago
            'LugarExpedicion': datos_json['cabecera']['LugarExpedicion'], # catCFDI:c_CodigoPostal
            'Confirmacion': '',
          },
          'CfdiRelacionados': {
            'TipoRelacion': '',
            'CfdiRelacionado': {
              'UUID': ''
            }
          },
          'Emisor': {
            'Rfc': datos_json['cabecera']['RFC_Emisor'],
            #'Rfc': 'ACO560518KW7',
            'Nombre': datos_json['cabecera']['Nombre_Emisor'].replace('.', ''),
            'RegimenFiscal': datos_json['cabecera']['RegimenFiscal'],
            'Emisor_dom': {
              'calle': datos_json['cabecera']['Dom_Emisor_calle'],
              'noExterior': datos_json['cabecera']['Dom_Emisor_noExterior'],
              'noInterior': datos_json['cabecera']['Dom_Emisor_noInterior'],
              'colonia': datos_json['cabecera']['Dom_Emisor_colonia'],
              'localidad': datos_json['cabecera']['Dom_Emisor_localidad'],
              'referencia': datos_json['cabecera']['Dom_Emisor_referencia'],
              'municipio': datos_json['cabecera']['Dom_Emisor_municipio'],
              'estado': datos_json['cabecera']['Dom_Emisor_estado'],
              'pais': datos_json['cabecera']['Dom_Emisor_pais'],
              'codigoPostal': datos_json['cabecera']['Dom_Emisor_codigoPostal'] 
            },
          },
          'Receptor': {
            'Rfc': datos_json['cabecera']['RFC_Receptor'],
            'Nombre': datos_json['cabecera']['Nombre_Receptor'].replace('.', ''),
            #'ResidenciaFiscal': datos_json['cabecera']['Dom_Receptor_pais']  if self.cce_complement else '',
            #'NumRegIdTrib': datos_json['cabecera']['Misc39'] if self.cce_complement else '',
            'UsoCFDI': datos_json['cabecera']['Notas03'], # catCFDI:c_UsoCFDI
            'Receptor_dom': {
              'calle': datos_json['cabecera']['Dom_Receptor_calle'],
              'noExterior': datos_json['cabecera']['Dom_Receptor_noExterior'],
              'noInterior': datos_json['cabecera']['Dom_Receptor_noInterior'],
              'colonia': datos_json['cabecera']['Dom_Receptor_colonia'],
              'localidad': datos_json['cabecera']['Dom_Receptor_localidad'],
              'referencia': datos_json['cabecera']['Dom_Receptor_referencia'],
              'municipio': datos_json['cabecera']['Dom_Receptor_municipio'],
              'estado': datos_json['cabecera']['Dom_Receptor_estado'],
              'pais': datos_json['cabecera']['Dom_Receptor_pais'],
              'codigoPostal': datos_json['cabecera']['Dom_Receptor_codigoPostal']
            }
          },
          #'Conceptos': [{'ClaveProdServ': c['Linea_Misc48'], 'NoIdentificacion': c['Linea_Cod_Articulo'], 'Cantidad': c['Linea_Cantidad'], 'ClaveUnidad': c['Linea_Misc49'], 'Unidad': c['Linea_Unidad'], 'Descripcion': c['Linea_Descripcion'].replace('¬', ''), 'ValorUnitario': c['Linea_PrecioUnitario'], 'Importe': c['Linea_Importe'], 'Descuento': c['Linea_Ind_CargoDescuento']} for c in datos_json['detalle']],
          'Conceptos': [],
          'Impuestos': {
            'TotalImpuestosRetenidos': '',
            'TotalImpuestosTrasladados': '',
            'Traslados': [
              {
                'Impuesto': '',
                'TipoFactor': '',
                'TasaOCuota': '',
                'Importe': ''
              }
            ],
            'Retenciones': [
              {
                'Impuesto': '',
                'Importe': ''
              }
            ]
          }
        }
        self.taxpayer_id = invoice_json['Emisor']['Rfc']
        print self.taxpayer_id
        #result = self.iusa.select_csd(rfc=self.taxpayer_id, serial=True)
        #if result['success']:
          #set_trace()
        #  self.serial_number = str(result['content'][0]).strip()
        #else:
        #  self.log_f.error('No fue posible extraer el número de serie del CSD desde la Base de Datos. Error => %s' % result['error'])
        self.serial_number = CSD_DICT[self.taxpayer_id].keys()[0]
        self.receiver_id = invoice_json['Receptor']['Rfc']
        self.cfdi_serial = invoice_json['Comprobante']['Serie']
        self.cfdi_folio = invoice_json['Comprobante']['Folio']
        self.date = invoice_json['Comprobante']['Fecha']
      except Exception as e:
        print 'Exception create_json_33() Comprobante => %s' % str(e)
        self.log_f.error('Exception create_json_33() Comprobante => %s' % str(e))
        #return invoice_json
      #set_trace()
      try:
        #for d in datos_json['detalle']:
        for k, v in datos_json['detalle'].iteritems():
          concepto = {}
          imp = {}
          concepto['Impuestos'] = {'Traslados': [], 'Retenciones': []}
          concepto['ClaveProdServ'] = v['Linea_Misc47'] if not self.nomina_complement else v['ClaveProdServ']
          concepto['NoIdentificacion'] = v['Linea_Cod_Articulo']
          concepto['Cantidad'] = v['Linea_Cantidad']
          concepto['ClaveUnidad'] = v['Linea_Misc48'] if not self.nomina_complement else v['Linea_Unidad']
          concepto['Unidad'] = v['Linea_Unidad']
          concepto['Descripcion'] = v['Linea_Descripcion'].replace('¬', '').replace('(', '').replace(')', '')
          concepto['ValorUnitario'] = v['Linea_PrecioUnitario']
          concepto['Importe'] = v['Linea_Importe']
          concepto['Descuento'] = v['Linea_Ind_CargoDescuento']
          for i_name in ('Traslados', 'Retenciones'):
            for i in v['Impuestos'][i_name]:
              imp['Impuesto'] = i['Impuesto_Descripcion']
              imp['TipoFactor'] = i['Impuesto_TipoFactor']
              imp['TasaOCuota'] = i['Impuesto_Tasa']
              imp['Importe'] = i['Impuesto_Monto_Importe']
              imp['Base'] = i['Impuesto_Base']
              concepto['Impuestos'][i_name].append(imp)
              imp = {}
          invoice_json['Conceptos'].append(concepto)
      except Exception as e:
        print 'Exception create_json_33() Conceptos => %s' % str(e)
        self.log_f.error('Exception create_json_33() Conceptos => %s' % str(e))

      tr_imp = {}
      re_imp = {}
      #set_trace()
      try:
        if 'impuestos' in datos_json:
          for impuesto in datos_json['impuestos']:
            if 'TR' in impuesto['Impuesto_TipoImpuesto']:
              invoice_json['Impuestos']['totalImpuestosTrasladados'] = datos_json['cabecera']['Monto_TotalImp_Trasladados']
              tr_imp['impuesto'] = impuesto['Impuesto_Descripcion']
              tr_imp['TipoFactor'] = impuesto['Impuesto_TipoFactor']
              tr_imp['tasa'] = impuesto['Impuesto_Tasa']
              tr_imp['importe'] = impuesto['Impuesto_Monto_Importe']
              invoice_json['Impuestos']['Traslados'].append(tr_imp) 
              tr_imp = {}
            elif 'RE' in impuesto['Impuesto_TipoImpuesto']:
              invoice_json['Impuestos']['totalImpuestosRetenidos'] = datos_json['cabecera']['Monto_TotalImp_Retenidos']
              re_imp['impuesto'] = impuesto['Impuesto_Descripcion']
              re_imp['importe'] = impuesto['Impuesto_Monto_Importe']
              invoice_json['Impuestos']['Retenciones'].append(re_imp)
              re_imp = {}
      except Exception as e:
        print 'Exception create_json_33() Impuestos => %s' % str(e)
        self.log_f.error('Exception create_json_33() Impuestos => %s' % str(e))
        #return invoice_json
      self.invoice_json = self.remove_empty_from_dict(invoice_json)

    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      print "Exception create_json_33() => %s" % str(e)
      self.log_f.error("Exception create_json_33() => %s" % str(e))
    return self.invoice_json

  def remove_empty_from_dict(self, d):
    try:
      if type(d) is dict:
        return dict((k, self.remove_empty_from_dict(v)) for k, v in d.iteritems() if v and self.remove_empty_from_dict(v))
      elif type(d) is list:
        return [self.remove_empty_from_dict(v) for v in d if v and self.remove_empty_from_dict(v)]
      else:
        try:
          d = d.encode('utf8')
        except:
          pass
        return d
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.log_f.error("Exception remove_empty_from_dict() => %s" % str(e))
      print "Exception remove_empty_from_dict() => %s" % str(e)

  def get_original_string(self):
    try:
      success = False
      if not self.retention_invoice:
        self.cfdi_etree.set('NoCertificado', self.serial_number)
      self.full_cfdi = ET.tostring(self.cfdi_etree)
      self.full_cfdi = self.full_cfdi.replace('&#172;', '').replace('&#225;', 'á').replace('&#233;', 'é').replace('&#237;', 'í').replace('&#243;', 'ó').replace('&#250;', 'ú').replace('&#193;', 'Á').replace('&#201;', 'É').replace('&#205;', 'Í').replace('&#211;', 'Ó').replace('&#218;', 'Ú')
      self.full_cfdi = self.full_cfdi.replace('&#252;', u'ü').replace('&#241;', 'ñ').replace('&#172;', '').replace('¬', '')
      try:
        self.full_cfdi = self.full_cfdi.encode('utf-8')
        #print self.full_cfdi
      except:
        pass
      doc = libxml2.parseMemory(self.full_cfdi, len(self.full_cfdi))
      if not self.retention_invoice:
        result = settings.XSLT_STYLE_33.applyStylesheet(doc, None)
      else:
        result = settings.XSLT_STYLE_RET.applyStylesheet(doc, None)
      doc.freeDoc()
      self.original_string = str(result)
      self.original_string = self.original_string.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')
      self.original_string = self.original_string.replace('\n','')
      self.original_string = self.original_string.replace('&quot;', '"')
      self.original_string = self.original_string.replace('&lt;', '<')
      self.original_string = self.original_string.replace('&gt;', '>')
      self.original_string = self.original_string.replace('&apos;', '´')
      self.original_string = self.original_string.replace('&amp;', '&')
      self.original_string = self.original_string.strip()
      #print self.original_string
      success = self.gen_seal_local()
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.parser_success = False
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print 'Exception get_original_string() => %s' % str(e)
      self.log_f.error('Exception get_original_string() => %s' % str(e))
      self.log_f.error("%s =>%s =>%s" % (str(exc_type), str(fname), str(exc_tb.tb_lineno)))
      # @TODO MOVER A ERRONEOS
      #if os.path.isfile(self.txt_path):
      #  os.rename(self.txt_path, os.path.join(ERROR_PATH, self.txt_name))

    return success

  def gen_seal_local(self):
    try:
      success = False
      self.sello = None
      csd_key = CSD_DICT[self.taxpayer_id][self.serial_number]['KEY']
      rsa = load_key_string(csd_key)
      assert len(rsa) in (1024, 2048)
      assert rsa.e == '\000\000\000\003\001\000\001'
      
      if self.version_cfdi == '3.3':
        md5_digest = hashlib.sha256(self.original_string).digest()
        rsa_signature = rsa.sign( md5_digest, 'sha256')
      elif self.retention_invoice:
        md5_digest = hashlib.sha1(self.original_string).digest()
        rsa_signature = rsa.sign( md5_digest, 'sha1')
      self.sello = base64.b64encode(rsa_signature)
      success = self.set_certificado_sello()
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.parser_success = False
      print "Exception gen_seal_local() => %s" % str(e)
      self.log_f.error("Exception gen_seal_local() => %s" % str(e))
      # @TODO MOVER A ERRONEOS
      #if os.path.isfile(self.txt_path):
      #  os.rename(self.txt_path, os.path.join(ERROR_PATH, self.txt_name))
    return success

  def set_certificado_sello(self):
    try:
      success = False
      certificado = CSD_DICT[self.taxpayer_id][self.serial_number]['CER']
      
      if not self.retention_invoice:
        #self.cfdi_etree.set('Certificado', CSD_DICT[self.taxpayer_id][self.serial_number]['CER'])
        self.cfdi_etree.set('Certificado', certificado)
        self.cfdi_etree.set('NoCertificado', self.serial_number)
        self.cfdi_etree.set('Sello', self.sello)
      #else:
      #  self.cfdi_etree.set('Cert', certificado)
      #  self.cfdi_etree.set('NumCert', self.serial_number)
      #  self.cfdi_etree.set('Sello', self.sello)
      try:
        self.xml = ET.tostring(self.cfdi_etree, xml_declaration=True, encoding='utf-8')
      except:
        self.xml = ET.tostring(self.cfdi_etree, xml_declaration=True)
      success = True
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.parser_success = False
      print "Exception set_certificado_sello() => %s" % str(e)
      self.log_f.error("Exception set_certificado_sello() => %s" % str(e))

    return success

  def stamp(self):
    try:
      success = False
      #set_trace()
      #print self.xml
      
      #xml_name = '%s.xml' % self.txt_name.replace('.txt', '')
      if self.nomina_complement:
        response, client = FinkokWS.stamp(self.xml)
      elif self.retention_invoice:
        response, client = FinkokWSRetentions.stamp(self.xml)
      
      if response.Incidencias:
        #set_trace()
        #print self.xml

        try:
          cod_status = str(response.Incidencias.Incidencia[0].CodigoError)
        except:
          pass

        #if not os.path.exists(os.path.join(ERROR_PATH, cod_status)):
        #  os.mkdir(os.path.join(ERROR_PATH, cod_status))

        #try:
        #  self.cfdi_error_path = os.path.join(ERROR_PATH, cod_status)
        #except:
        #  pass
        
        #try:
        #  os.rename(os.path.join(TXT_SUCCESS, self.txt_name), os.path.join(self.cfdi_error_path, self.txt_name))
        #except:
        #  os.rename(self.txt_path, os.path.join(self.cfdi_error_path, self.txt_name))

        error_message = str(response.Incidencias.Incidencia[0].MensajeIncidencia)
        extra_info = str(response.Incidencias.Incidencia[0].ExtraInfo) if response.Incidencias.Incidencia[0].ExtraInfo is not None else ''
        error = u'%s - %s - %s' % (cod_status, error_message, extra_info)
        payroll = PayRoll.objects.filter(id=self.payroll.id)
        data_dict = get_values(self.xml)
        payroll.update(**data_dict)
        self.payroll = PayRoll.objects.get(id=self.payroll.id)
        self.payroll.notes = error
        self.payroll.xml = self.xml
        self.payroll.status = 'E'
        self.payroll.save()

        self.log_f.error('Timbrado de XML: Error (%s - %s - %s)' % (cod_status, error_message, extra_info))

        self.logs(client)
        success = False
      elif 'Comprobante timbrado satisfactoriamente' in response.CodEstatus:
        self.cfdi_stamped = response.xml.encode('UTF-8')
        payroll = PayRoll.objects.filter(id=self.payroll.id)
        data_dict = get_values(self.cfdi_stamped)
        payroll.update(**data_dict)
        self.payroll = PayRoll.objects.get(id=self.payroll.id)
        self.payroll.xml = self.cfdi_stamped
        self.payroll.status = 'S'
        self.payroll.save()
        self.log_f.info("Timbrado de XML: OK (%s)" % str(response.UUID))
        
        #with open(os.path.join(XML_PATH, xml_name) , 'w') as cfdi_file:
        #  cfdi_file.write(response.xml.encode('utf8'))
        
        success = True
    except Exception, e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      print "Exception stamp() => %s" % str(e)
      self.log_f.error("Exception stamp() => %s" % str(e))

    return success

  def create_pdf(self):
    try:
      response  = {
          'success': False,
          'message': ''
        }

      #set_trace()
      if not self.reprocess_pdf:
        xml_path = os.path.join(XML_PATH, self.txt_name.replace('.txt', '.xml'))
        pdf_obj = CreatePDF(xml_path, self.txt_name)
      #else:
      #  json_dicc =  json.loads(open(os.path.join(TMP_PATH, self.json_downloaded_name), 'r').read())
      #  pdf_obj = CreatePDF(os.path.join(TMP_PATH, self.filename.replace('.pdf', '.xml')), json_dicc, PDF_FILE_PATH, BASE_PATH, self.nomina_complement, self.retention_invoice)

      if self.nomina_complement:
        response = pdf_obj.tables_builder()
      #elif self.retention_invoice:
      #  response = pdf_obj.create_pdf_retenciones()
      
      if response['success']:
        self.log_f.info("Creación de PDF: OK")
      else:
        self.log_f.error("Creación de PDF: Error: %s" % response['message'])
    except Exception as e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      self.log_f.error("Exception create_pdf() => %s" % str(e))

    return response
  
  def move_error_txt(self, only_json=False):
    import fnmatch

    try:
      log_filename = self.txt_name.replace('txt','log')
      logging.shutdown()


      paths = []
      for root, dirnames, filenames in os.walk(ERROR_PATH):
        for filename in fnmatch.filter(filenames, self.txt_name):
          #paths.append(os.path.join(root, filename))
          paths.append(root)

      #print paths
      #set_trace()


      if not self.bad_file:
        # FALLIDO EN 2 OCASIONES
        #if os.path.exists(os.path.join(ERROR_PATH, self.txt_name)) and not only_json:
        if len(paths) and not only_json:
          shutil.copy2(self.log_path, os.path.join(self.cfdi_error_path, log_filename))
          try:
            os.remove(os.path.join(TXT_SUCCESS, self.txt_name))
          except:
            pass
        # FALLIDO Y TIMBRADO
        #elif os.path.exists(os.path.join(ERROR_PATH, self.txt_name)) and only_json:
        elif len(paths) and only_json:
          for path in paths:
            #os.remove(os.path.join(ERROR_PATH, self.txt_name))
            os.remove(os.path.join(path, self.txt_name))
            try:
              #os.remove(os.path.join(ERROR_PATH, log_filename))
              os.remove(os.path.join(path, log_filename))
            except:
              pass
        # PRIMERA OCASION QUE FALLA
        elif not only_json and os.path.exists(os.path.join(TXT_SUCCESS, self.txt_name)):
          shutil.copy2(os.path.join(TXT_SUCCESS, self.txt_name), os.path.join(TXT_INIT, self.txt_name))
          os.rename(os.path.join(TXT_SUCCESS, self.txt_name), os.path.join(self.cfdi_error_path, self.txt_name))
        try:
          os.remove(os.path.join(TXT_SUCCESS, self.txt_name.replace('txt', 'json1')))
          os.remove(os.path.join(TXT_SUCCESS, self.txt_name.replace('txt', 'json2')))
        except:
          pass
      else:
        if os.path.exists(os.path.join(TXT_SUCCESS, self.txt_name)):
          shutil.copy2(os.path.join(TXT_SUCCESS, self.txt_name), os.path.join(TXT_INIT, self.txt_name))
        #elif os.path.exists(os.path.join(ERROR_PATH, self.txt_name)):
        elif len(paths):
          error_path = paths[0]
          #shutil.copy2(os.path.join(ERROR_PATH, self.txt_name), os.path.join(TXT_INIT, self.txt_name))
          shutil.copy2(os.path.join(error_path, self.txt_name), os.path.join(TXT_INIT, self.txt_name))
        
    except Exception as e:
      if 'Bad file descriptor' in str(e):
        self.bad_file = True
      print "Exception move_error_txt() => %s" % str(e)
