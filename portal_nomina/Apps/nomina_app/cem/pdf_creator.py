#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from suds.client import Client
from lxml import etree
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, SimpleDocTemplate, Frame, Paragraph, Image, Spacer, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, cm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from .pdf_choice import *

import sys
import math
from decimal import Decimal
from lxml import etree as ET
from moneda import numero_a_letras
from pdb import set_trace
import locale
try:
  locale.setlocale(locale.LC_ALL, "es_MX.utf8")
except:
  locale.setlocale(locale.LC_ALL, "es_ES.utf8")


PATH_QR = '/tmp/'

darkred = colors.Color(red=(0.401), green=(0.172), blue=(0.160))

style = getSampleStyleSheet()
basic_center = ParagraphStyle('Caption', fontSize=7, alignment=TA_CENTER, leading=8, spaceAfter=0, spaceBefore=0)
basic_left = ParagraphStyle('Caption', fontSize=7, alignment=TA_LEFT, leading=8, spaceAfter=0, spaceBefore=0)
total_style = ParagraphStyle('Caption', fontSize=9.5, alignment=TA_RIGHT, leading=10.5, spaceAfter=0, spaceBefore=0)
_8_right = ParagraphStyle('Caption', fontSize=8, alignment=TA_RIGHT, leading=9, spaceAfter=0, spaceBefore=0)
_8_left = ParagraphStyle('Caption', fontSize=8, alignment=TA_LEFT, leading=9, spaceAfter=0, spaceBefore=0)
basic_right = ParagraphStyle('Caption', fontSize=7, alignment=TA_RIGHT, leading=8, spaceAfter=0, spaceBefore=0)
title_style = ParagraphStyle('Caption', fontSize=9, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_LEFT)
folio_style = ParagraphStyle('Caption', fontSize=10, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_RIGHT, textColor='red')
style_white_10 = ParagraphStyle('Caption', fontSize=10, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_CENTER, textColor='white')
style_white = ParagraphStyle('Caption', fontSize=8, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_CENTER, textColor="white")
taxpayer_name = ParagraphStyle('Caption', fontSize=10, leading=12, spaceAfter=0, spaceBefore=0, alignment=TA_LEFT, textColor=darkred)
titles_tfd = ParagraphStyle('Caption', fontSize=10, leading=10, spaceAfter=0, spaceBefore=0, alignment=TA_LEFT)
s = Paragraph('', basic_center)


class CreatePDF(object):
  
  #def __init__(self, xml_string, txt_name):
  def __init__(self, xml_path, txt_name):
    xml_file = open(xml_path, 'r')
    xml_string = xml_file.read()
    xml_file.close()
    self.message = ''
    self.success = False
    self.filename = txt_name
    
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
        n_comp = xml_etree.xpath('//cfdi:Comprobante', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/3'})[0]
        self.folio = n_comp.get('Folio') if n_comp.get('Folio') else ""
        self.serie = n_comp.get('Serie') if n_comp.get('Serie') else ""
        self.date = n_comp.get('Fecha')
        self.currency = n_comp.get('Moneda')
        self.serial_cfdi = n_comp.get('NoCertificado')
        self.expedition_place = n_comp.get('LugarExpedicion') 
        try:
          self.pay_method = METODO_PAGO[n_comp.get('MetodoPago')]
        except:
          self.pay_method = n_comp.get('MetodoPago') if n_comp.get('MetodoPago') else ''
        
        try:
          self.way_payment = FOR_PA[n_comp.get('FormaPago')]
        except:
          self.way_payment = n_comp.get('FormaPago') if n_comp.get('FormaPago') else ''
        
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
        print "Exception get node Comprobante => %s" % str(e)
        raise Exception(e)
      
      # Emisor
      try:
        n_emisor = xml_etree.find('cfdi:Emisor', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/3'})   
        self.name = n_emisor.get('Nombre')
        self.taxpayer_id = n_emisor.get('Rfc')
        try:
          self.regimen = REG_FIS[n_emisor.get('RegimenFiscal')]
        except:
          self.regimen = n_emisor.get('RegimenFiscal')
      except Exception as e:
        print "Exception get node Emisor => %s" % str(e)
        raise Exception(e)

      # Receptor
      try: 
        n_receptor = xml_etree.find('cfdi:Receptor', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/3'})
        self.rtaxpayer_id =  n_receptor.get('Rfc')
        self.rname = n_receptor.get('Nombre')
        self.uso_cfdi = n_receptor.get('UsoCFDI')
      except Exception as e:
        print "Exception get node Receptor => %s" % str(e)
        raise Exception(e)
      
      # Conceptos
      try:
        self.conceptos = xml_etree.xpath('cfdi:Conceptos/cfdi:Concepto', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/3'})
      except:
        self.conceptos = None
        print "Exception get node Conceptos => %s" % str(e)   
        raise Exception(e)

      # total impuestos trasladados
      try:
        self.total_tra = xml_etree.xpath('//cfdi:Comprobante/cfdi:Impuestos/@TotalImpuestosTrasladados', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/3'})[0]
      except:
        self.total_tra = '0.00'
      
      # total impuestos retenidos
      try:
        self.total_ret = xml_etree.xpath('//cfdi:Comprobante/cfdi:Impuestos/@TotalImpuestosRetenidos', namespaces={'cfdi':'http://www.sat.gob.mx/cfd/3'})[0]
      except:
        self.total_ret = '0.00'

      try:
        n_nomina = xml_etree.xpath('//tmp:Nomina', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
        self.tot_ded = n_nomina.get('TotalDeducciones')
        self.tot_per = n_nomina.get('TotalPercepciones')
        self.tot_otpa = n_nomina.get('TotalOtrosPagos')
        self.fe_exped = n_nomina.get('FechaFinalPago')
        self.paid_days = n_nomina.get('NumDiasPagados')
        paid_from = n_nomina.get('FechaInicialPago')
        paid_from_2 = datetime.strptime(paid_from, '%Y-%m-%d').strftime('%d/%b/%Y').upper()
        
        paid_to = n_nomina.get('FechaFinalPago')
        paid_to_2 = datetime.strptime(paid_to, '%Y-%m-%d').strftime('%d/%b/%Y').upper()
        
        self.period = "%s al %s" % (paid_from_2, paid_to_2)

        # Emisor Nomina
        self.employer_regist = xml_etree.xpath('//tmp:Emisor/@RegistroPatronal', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]

        # Receptor Nomina
        n_receptor = xml_etree.xpath('//tmp:Receptor', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
        self.emp_num = n_receptor.get('NumEmpleado')
        self.curp = n_receptor.get('Curp')
        self.imss = n_receptor.get('NumSeguridadSocial')
        self.depart = n_receptor.get('Departamento')
        self.posit = n_receptor.get('Puesto')
        self.s_diario = n_receptor.get('SalarioDiarioIntegrado')
        self.ss_no = n_receptor.get('NumSeguridadSocial')
        try:
          self.emp_regimen = REG_EMP[n_receptor.get('TipoRegimen')]
        except:
          self.emp_regimen = n_receptor.get('TipoRegimen')

        # Deducciones
        if len(xml_etree.xpath('//tmp:Deducciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          self.deducciones = xml_etree.xpath('//tmp:Deducciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
          self.tot_isr = self.deducciones.get('TotalImpuestosRetenidos') if self.deducciones.get('TotalImpuestosRetenidos') else '0.00'
          self.tot_ded = self.deducciones.get('TotalOtrasDeducciones') if self.deducciones.get('TotalOtrasDeducciones') else '0.00'
        else:
          self.deducciones = []
        
        # Percepciones
        if len(xml_etree.xpath('//tmp:Percepciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          self.percepciones = xml_etree.xpath('//tmp:Percepciones', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
        else:
          self.percepciones = []
        
        # OtrosPagos
        if len(xml_etree.xpath('//tmp:OtrosPagos', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})) > 0:
          try:
            self.n_otros_pagos = xml_etree.xpath('//tmp:OtrosPagos', namespaces={'tmp':'http://www.sat.gob.mx/nomina12'})[0]
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
      except Exception, e:
        print "Exception Datos de Nómina => %s" % str(e)
        self.message = "Exception Datos de Nómina => %s" % str(e)
        return
      
      # TFD
      try: 
        n_tfd = xml_etree.xpath('//cfdi:TimbreFiscalDigital', namespaces={'cfdi':'http://www.sat.gob.mx/TimbreFiscalDigital'})[0]
        self.uuid = n_tfd.get('UUID')
        self.seal_cfd = n_tfd.get('SelloCFD')
        self.seal_sat = n_tfd.get('SelloSAT')
        self.serial_sat = n_tfd.get('NoCertificadoSAT')
        self.date_cert = n_tfd.get('FechaTimbrado')
        self.original_string_tfd = '||1.1|%s|%s|%s|%s||' % (self.uuid, self.date_cert, self.seal_sat, self.serial_sat)
      except Exception as e:
        print "Exception get node TFD => %s" % str(e)
        raise Exception(e)
      
      self.taxpayer_address = "Av. Francisco I. Madero No. 97 Col. Centro Morelia, Michoacán, C.P. 58000 <br/> <br/> <b>RFC:</b> %s <br/> <b>Régimen Fiscal:</b> %s <br/> <b>Registro Patronal:</b> %s" % (self.taxpayer_id, self.regimen, self.employer_regist) #Registro Patronal: %s</b> self.registro_patronal
      #self.emisor_address = "Cerrada Rancho de la Cruz 98<br/>Jamaica<br/>México<br/>Ciudad de México<br/>Venustiano Carranza<br/>C.P. 15800<br/><b>RFC:</b> %s" % self.taxpayer_id
      #self.receptor_address = "%s %s %s<br/>%s %s %s<br/>%s %s<br/>%s, %s" % (re_calle, re_no_ext, re_no_int, re_col, re_ref, re_cp, re_mun, re_loc, re_estado, re_pais)
      self.signature_legend = u"""Recibo del "%s" por concepto del pago total de mi salario y demás prestaciones del periodo indicado, sin que a la fecha se me adeude cantidad alguna por ningún concepto.""" % self.name
      self.success = self.tables_builder()
    except Exception as e:
      print "Exeption Constructor | %s" % str(e)

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
      print "Error al crear el CodigoQR => %s" % str(e)
      self.message = "Error al crear el CodigoQR => %s" % str(e)
  
  def settings(self, canvas, doc):
    try: 
      canvas.saveState()
      canvas.setFont('Helvetica-Bold', 7.5)

      # Set PDF Properties
      canvas.setTitle('Factura Electrónica')
      canvas.setSubject('Recibo de Nómina de ()')
      canvas.setAuthor('CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V')
      canvas.setKeywords(['CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V', 'CFDI 3.3', 'Nómina 1.2', 'SAT'])
      canvas.setCreator('CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V')
      
      # Draw table with canvas
      self.header(canvas)
      
      canvas.restoreState()
    except Exception as e:
      print "Exception header() =>  %s" % str(e)
      self.message = "Exception header() =>  %s" % str(e)

  def tables_builder(self):
    try:
      response  = {
        'success': False,
        'message': ''
      }
      
      story=[]
      table_concepts = self.concepts()
      story.append(table_concepts)
      story.append(Spacer(0,9))
      table_totales = self.totales()
      story.append(table_totales)
      story.append(Spacer(0,5))
      table_signature = self.employe_signature()
      story.append(table_signature)
      story.append(Spacer(0,15))
      table_tfd_data = self.tfd_data()
      story.append(table_tfd_data)
      story.append(Spacer(0,15))
      table_tfd = self.tfd_seals()
      story.append(table_tfd)
      
      frame = Frame(inch, 60, 465, 545)
      header = PageTemplate(id='header', frames=frame, onPage=self.settings)
      self.doc = BaseDocTemplate('PDF/%s' % self.filename.replace('.txt', '.pdf'), pageTemplates=[header], pagesize=letter)
      self.doc.build(story, canvasmaker=NumberedCanvas)
      success = True

      response['success'] = True
      response['message'] = self.message

      
    except Exception as e:
      print "Exception tables_builder() | %s" % str(e)
    return response

  def header(self, canvas):
    try:
      #canvas.setFont('Helvetica-Bold', 13)
      #canvas.setFillColor(HexColor('#4d0000'))
      #canvas.drawString(2.9*inch, 10.7*inch, '%s' % self.name)

      canvas.setFont('Helvetica-Bold', 8)
      canvas.setFillColor(HexColor('#555759'))
      canvas.drawString(0.5*inch, 0.4*inch, 'Creado por:')
      
      # Link on "CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V"
      coords = (1.15*inch, 0.6*inch, 2.2*inch, 0.3*inch) # [x1, y1, x2, y2] Define an link area (rectangle)
      canvas.linkURL('http://www.pruebas.com', coords)
      canvas.setFillColor(HexColor('#113a5d'))
      canvas.drawString(1.2*inch, 0.4*inch, 'CENTRO DE VALIDACIÓN DIGITAL CVDSA”, S.A. DE C.V')
      
      # Link on logo
      #coords_2 = (7.3*inch, 1.6*inch, 8.05*inch, 0.5*inch)

      #logo = ImageReader('pac.png')
      #width = 45
      #height = 70
      #canvas.drawImage(logo, 530, 42, width=width, height=height, mask='auto')

      # Emisor ================================================================================
      emisor_data = [
              [Paragraph('<b>%s</b>' % self.name, taxpayer_name), Paragraph("<b>Recibo de Nómina</b>", style_white_10)],
              [Paragraph(self.taxpayer_address, title_style), s],
          ]

      table_emisor = Table(emisor_data, colWidths=[15.05*cm, 4*cm], style=[
              #('GRID', (0,0), (-1,-1), 1, colors.gray),
              ('VALIGN', (0,0), (-1,-1), "MIDDLE"),
              ('BACKGROUND', (-1,0), (-1,0), darkred),
              ('TOPPADDING', (0,0), (-1,-1), 2.5), 
              ('BOTTOMPADDING', (0,0), (-1,-1), 2.5), 
              ('BOTTOMPADDING', (-1,0), (-1,0), 5), 
      ])

      table_emisor.wrapOn(canvas, 1.2*cm, 24.5*cm)
      table_emisor.drawOn(canvas, 1.2*cm, 24.5*cm)
      # Emisor ================================================================================
      
      # Receptor ================================================================================
      receiver_data = [
              [Paragraph('<b>RECEPTOR</b>', style_white), s],
              [Paragraph('<b>No. Empleado: </b>%s' % self.emp_num, _8_left), Paragraph('<b>Depto.: </b>%s' % self.depart, _8_left)],
              [Paragraph('<b>Nombre: </b>%s' % self.rname, _8_left), Paragraph('<b>Puesto.: </b>%s' % self.posit, _8_left)],
              [Paragraph('<b>CURP: </b>%s' % self.curp, _8_left), Paragraph('<b>Periodo del: </b>%s' % self.period, _8_left)],
              [Paragraph('<b>RFC: </b>%s' % self.rtaxpayer_id, _8_left), Paragraph('<b>Días pagados: </b>%s' % self.paid_days, _8_left)],
              [Paragraph('<b>No. Seguridad Social: </b>%s' % self.ss_no, _8_left), Paragraph('<b>Régimen del trabajador: </b>%s' % self.emp_regimen, _8_left)],
      ]

      table_receiver = Table(receiver_data, colWidths=[9.55*cm, 9.5*cm], style=[
              #('GRID', (0,0),(-1,-1), 1, colors.gray),
              ('BACKGROUND', (0,0),(-1,0), darkred),
              ('TOPPADDING', (0,0),(-1,-1), 0.5),
              ('BOTTOMPADDING', (0,0),(-1,-1), 0.5),
              ('SPAN', (0,0),(-1,0)),
              ('VALIGN', (0,1),(-1,-1), 'TOP'),
        ])

      table_receiver.wrapOn(canvas, 1.2*cm, 21.8*cm)
      table_receiver.drawOn(canvas, 1.2*cm, 21.8*cm)
      # Receptor ================================================================================
      
    except Exception as e:
      print "Exception header() => %s" % str(e)

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
          per_desc = ET.tostring(percepcion)
          if not 'SeparacionIndemnizacion' in per_desc:
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

            per_ded_data.append([Paragraph(percepcion.get('Clave'), basic_center), Paragraph(percepcion.get('Concepto'), basic_left), Paragraph(self.truncate(Decimal('%.2f' % (float(percepcion.get('ImporteExento')) + float(percepcion.get('ImporteGravado')))), 2), basic_right), s, Paragraph(clave_ded, basic_center), Paragraph(concepto_ded, basic_left), Paragraph(importe_ded, basic_right)]),
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
        #('BOX', (0,0),(-1,-1), 1, darkred),
        ('BACKGROUND', (0,0),(2,0), darkred),
        ('BACKGROUND', (4,0),(-1,0), darkred),
        ('SPAN', (0,0),(2,0)), # PERCEPCIONES
        ('SPAN', (4,0),(-1,0)), # DEDUCCIONES
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('VALIGN', (0,2),(-1,-1), 'TOP'),
        ('RIGHTPADDING', (0,0),(-1,-1), 2.5),
        ('LEFTPADDING', (0,0),(-1,-1), 2.5),
        ('TOPPADDING', (0,0),(-1,-1), 0.5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 0.5),
        ('BOTTOMPADDING', (0,1),(-1,1), 2),
        ('LINEBELOW',(0,1),(2,1), 1, darkred), # Draw a line below headers PERCEPCIONES
        ('LINEBELOW',(4,1),(-1,1), 1, darkred), # Draw a line below headers DEDUCCIONES
        ('LINEBELOW',(0,-1),(2,-1), 1, darkred), # Draw a line after last row PERCEPCIONES
        ('LINEBELOW',(4,-1),(-1,-1), 1, darkred), # Draw a line after last row DEDUCCIONES
        ('LINEBELOW',(0,"splitlast"),(2,"splitlast"), 1, darkred),
        ('LINEBELOW',(4,"splitlast"),(-1,"splitlast"), 1, darkred),
        ('BOTTOMPADDING',(0,-1),(-1,-1), 2),
        #('LINEBELOW',(0,"splitlast"),(-1,"splitlast"), 1, colors.gray),
      ])

    except Exception as e:
      print "Exception concepts() | %s" % str(e)
    return table_per_ded

  def totales(self):
    try:

      total_data =[
            [s, Paragraph('<b>Total Percepciones</b>', _8_right), Paragraph('%s' % self.truncate(Decimal(self.sub_total), 2), _8_right)],
            [s, Paragraph('<b>Total deducciones sin ISR</b>', _8_right), Paragraph('- %s' % self.truncate(Decimal(self.tot_ded), 2), _8_right)],
            [Paragraph('<b>Total con letra:</b>', _8_left), Paragraph('<b>ISR Retenido</b>', _8_right), Paragraph('- %s' % self.truncate(Decimal(self.tot_isr), 2), _8_right)],
            [Paragraph('%s %s/100 M.N.' % (self.amount_in_writting, self.total.split('.')[-1] if len(self.total.split('.'))>1 else '00'), _8_left), Paragraph('<b>Total</b>', total_style), Paragraph('$ %s' % self.truncate(Decimal(self.total), 2), total_style)],
        ]

      table_totales = Table(total_data, colWidths=[12.05*cm, 4*cm, 3*cm ], style=[
        #('GRID', (0,0), (-1, -1), 1, colors.gray),
        ('LINEBELOW', (1,2),(-1,2), 1, darkred),
        #('SPAN', (1,2),(1,-1)),
        #('SPAN', (2,2),(2,-1)),
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('VALIGN', (1,2),(-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0),(0,0), 1.3),
        ('TOPPADDING', (0,1),(-1,-1), 1.5),
        ('LEFTPADDING', (0,-2),(0,-1), 0),
        ('RIGHTPADDING', (-2,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,1),(-1,-1), 2.5),
      ])
    
    except Exception as e:
      print "Exception totales() | %s" % str(e)
    return table_totales

  def employe_signature(self):
    try:
      signature_data = [
              [Paragraph(self.signature_legend, basic_left), Paragraph('FIRMA:', basic_right), s],
      ]

      table_signature = Table(signature_data, colWidths=[11.5*cm, 1*cm, 6.55*cm], style=[
              #('GRID', (0,0),(-1,-1), 1, colors.gray),
              ('LINEBELOW', (-1,0),(-1,0), 1, darkred),
              ('RIGHTPADDING', (0,0),(-1,-1), 0.3),
              ('LEFTPADDING', (0,0),(-1,-1), 0.3),
              ('BOTTOMPADDING', (0,0),(-1,-1), 0),
              ('VALIGN', (0,0),(-1,-1), 'BOTTOM'),
        ])
    except Exception as e:
      print "Exception employe_signature() => %s" % str(e)
    return table_signature

  def tfd_data(self):
    try:
      tfd_data = [
            [Paragraph('<b>COMPROBANTE FISCAL DIGITAL POR INTERNET</b>', style_white), s, s],
            [Paragraph('<b>Folio fiscal: </b>%s' % self.uuid, _8_left), s, Paragraph('<b>Lugar de emisión: </b>%s' % self.expedition_place, _8_left)],
            [Paragraph('<b>Fecha y hora de certificación: </b>%s' % self.date_cert, _8_left), s, Paragraph('<b>Fecha y hora de emisión: </b>%s' % self.date, _8_left)],
            [Paragraph('<b>No. de serie del CSD del SAT: </b>%s' % self.serial_sat, _8_left), s, Paragraph('<b>No. de serie del CSD del emisor: </b>%s' % self.serial_cfdi, _8_left)],
            [Paragraph('<b>Forma de pago: </b>%s' % self.way_payment, _8_left), s, Paragraph('<b>Método de pago: </b>%s' % self.pay_method, _8_left)],
      ]

      table_tfd = Table(tfd_data, colWidths=[9.5*cm, 0.05*cm, 9.5*cm], style=[
            #('GRID', (0,0),(-1,-1), 1, colors.gray),
            ('SPAN', (0,0),(-1,0)),
            ('BACKGROUND', (0,0),(-1,0), darkred),
            ('TOPPADDING', (0,0),(-1,-1), 1),
            ('BOTTOMPADDING', (0,0),(-1,-1), 1),
        ])
    except Exception as e:
      print "Exception tfd_data() | %s" % str(e)
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
        #[s, s],
        #[s, Paragraph('<b>%s - %s</b>' % (self.name, self.ta), style_white)],
      ]

      table_tfd =Table(data_tfd, colWidths=[4*cm, 15.05*cm], style=[
        #('GRID',(0,0),(-1,-1), 1, darkred),
        #('BOX',(0,0),(-1,-1), 1, darkred),
        ('LINEAFTER',(0,0),(0,-1), 1, darkred),
        ('SPAN',(0,0),(0,-1)), # QR CODE
        #('BOTTOMPADDING',(1,1),(1,1), 3.5),
        #('BACKGROUND',(1,0),(1,0), darkred),
        #('BACKGROUND',(1,2),(1,2), darkred),
        #('BACKGROUND',(1,4),(1,4), darkred),
        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1), 'CENTER'),
        #('TOPPADDING',(0,0),(-1,-1), 2.5),
        ('TOPPADDING', (1,0),(-1,0), 2.5),
        ('BOTTOMPADDING', (1,-1),(-1,-1), 2.5),
        
        ('TOPPADDING', (1,1),(1,1), 0), # Cadena
        ('BOTTOMPADDING', (1,1),(1,1), 3), # Cadena

        ('TOPPADDING', (1,3),(1,3), 0), # Sello Emisor
        ('BOTTOMPADDING', (1,3),(1,3), 3), # Sello Emisor

        ('TOPPADDING', (1,5),(1,5), 0), # Sello SAT
        ('BOTTOMPADDING', (1,5),(1,5), 3), # Sello SAT
        
      ])

    except Exception as e:
      print "Exception tfd_seals() | %s" % str(e)
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
      print "Exception truncate() | %s" % str(e)
    
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
    self.drawString(2.6*inch, 0.6*inch, 'Este documento es una representación impresa de un CFDI')
    
    self.setFont('Helvetica-Bold', 8)
    self.setFillColor(HexColor('#555759'))
    self.drawString(7.2*inch, 0.4*inch, "Página %d de %d" % (self._pageNumber, page_count))
    