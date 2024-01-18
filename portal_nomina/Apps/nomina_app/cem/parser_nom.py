# -*- coding: utf-8 -*-
from django.conf import settings
import CFDI_33
import csv
import StringIO
from lxml import etree
from datetime import datetime
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
  AccionesOTitulosType,
  HorasExtraType,
  SubsidioAlEmpleoType,
  CompensacionSaldosAFavorType,
  OtroPagoType,
  OtrosPagosType,
  IncapacidadType,
  IncapacidadesType,
  Nomina,
)
import copy
import CFDI_40


class PARSER_NOM(object):
    """
        CLASE ENCARGADA DE CREAR EL XML DE NOMINA
    """

    def __init__(self, txt_path=None, taxpayer_id=None):

        self.txt_path = txt_path
        self.taxpayer_id = taxpayer_id
        self.namespace = 'nomina12:'
        self.is_valid = False
        self.error = None

        self.json = None
        self.cfdi = None
        self.serie = None
        self.folio = None
        self.receptor = None
        self.switch_version = False

        self.CFDI_HEADERS = {
            'Comprobante': [
                'Version', 'Serie', 'Folio', 'Fecha', 'FormaPago',
                'NoCertificado', 'SubTotal', 'Descuento', 'Moneda',
                'TipoCambio', 'Total', 'TipoDeComprobante', 'MetodoPago',
                'LugarExpedicion', 'Confirmacion',
            ],
            'CfdiRelacionados': ['numCfdiRelacionados', 'TipoRelacion'],
            'CfdiRelacionado': ['UUID'],
            'Emisor': ['Rfc', 'Nombre', 'RegimenFiscal'],
            'Receptor': [
                'Rfc', 'Nombre', 'ResidenciaFiscal', 'NumRegIdTrib', 'UsoCFDI'
            ],
            'Concepto': [
                'ClaveProdServ', 'Cantidad', 'ClaveUnidad',
                'Descripcion', 'ValorUnitario', 'Importe', 'Descuento'
            ],
            'ComplementoNomina': ['numNominas'],
            'Nomina': [
                'Version', 'TipoNomina', 'FechaPago', 'FechaInicialPago',
                'FechaFinalPago', 'NumDiasPagados', 'TotalPercepciones',
                'TotalDeducciones', 'TotalOtrosPagos'
            ],
            'NomEmisor': ['Curp', 'RegistroPatronal', 'RfcPatronOrigen'],
            'EntidadSNCF': ['OrigenRecurso', 'MontoRecursoPropio'],
            'NomReceptor': [
                'numSubContrataciones', 'Curp', 'NumSeguridadSocial',
                'FechaInicioRelLaboral', 'Antiguedad', 'TipoContrato',
                'Sindicalizado', 'TipoJornada', 'TipoRegimen', 'NumEmpleado',
                'Departamento', 'Puesto', 'RiesgoPuesto', 'PeriodicidadPago',
                'Banco', 'CuentaBancaria', 'SalarioBaseCotApor',
                'SalarioDiarioIntegrado', 'ClaveEntFed'
            ],
            'SubContratacion': ['RfcLabora', 'PorcentajeTiempo'],
            'Percepciones': [
                'numPercepciones', 'TotalSueldos', 'TotalSeparacionIndemnizacion',
                'TotalJubilacionPensionRetiro', 'TotalGravado', 'TotalExento'
            ],
            'Percepcion': [
                'numHorasExtra', 'TipoPercepcion', 'Clave', 'Concepto',
                'ImporteGravado', 'ImporteExento'
            ],
            'AccionesOTitulos': ['ValorMercado', 'PrecioAlOtorgarse'],
            'HorasExtra': ['Dias', 'TipoHoras', 'HorasExtra', 'ImportePagado'],
            'JubilacionPensionRetiro': [
                'TotalUnaExhibicion', 'TotalParcialidad', 'MontoDiario',
                'IngresoAcumulable', 'IngresoNoAcumulable'
            ],
            'SeparacionIndemnizacion': [
                'TotalPagado', 'NumAnosServicio', 'UltimoSueldoMensOrd',
                'IngresoAcumulable', 'IngresoNoAcumulable'
            ],
            'Deducciones': [
                'numDeducciones', 'TotalOtrasDeducciones',
                'TotalImpuestosRetenidos'
            ],
            'Deduccion': ['TipoDeduccion', 'Clave', 'Concepto', 'Importe'],
            'OtrosPagos': ['numOtroPago'],
            'OtroPago': ['TipoOtroPago', 'Clave', 'Concepto', 'Importe'],
            'SubsidioAlEmpleo': ['SubsidioCausado'],
            'CompensacionSaldosAFavor': ['SaldoAFavor', 'Ano', 'RemanenteSalFav'],
            'Incapacidades': ['numIncapacidad'],
            'Incapacidad': [
                'DiasIncapacidad', 'TipoIncapacidad', 'ImporteMonetario'
            ],
            'Observaciones': ['Observacion'],
            'Extras': ['num', 'PAE_EMAIL', 'email', 'PAE_MENSAJE', 'message', 'LUGAR_PAGO_ESTADO', 'state', 'LUGAR_PAGO_MUNICIPIO', 'municipality'],
        }

        self.CFDI_DICT = {
            'Comprobante': {},
            'CfdiRelacionados': {
                'numCfdiRelacionados': None,
                'TipoRelacion': None,
                'CfdiRelacionado': [],
            },
            'Emisor': {},
            'Receptor': {},
            'Concepto': {},
            'Nominas': [],
            'Observaciones': {},
            'Extras': {}
        }

        self.PAYROLL_DICT = {
            'Nomina': {
                'Version': '1.2',
                'TipoNomina': None,
                'FechaPago': None,
                'FechaInicialPago': None,
                'FechaFinalPago': None,
                'NumDiasPagados': None,
                'TotalPercepciones': None,
                'TotalDeducciones': None,
                'TotalOtrosPagos': None,
            },
            'Emisor': {
                'Curp': None,
                'RegistroPatronal': None,
                'RfcPatronOrigen': None,
                'EntidadSNCF': {}
            },
            'Receptor': {
                'numSubContrataciones': None,
                'Curp': None,
                'NumSeguridadSocial': None,
                'FechaInicioRelLaboral': None,
                'Antiguedad': None,
                'TipoContrato': None,
                'Sindicalizado': None,
                'TipoJornada': None,
                'TipoRegimen': None,
                'NumEmpleado': None,
                'Departamento': None,
                'Puesto': None,
                'RiesgoPuesto': None,
                'PeriodicidadPago': None,
                'Banco': None,
                'CuentaBancaria': None,
                'SalarioBaseCotApor': None,
                'SalarioDiarioIntegrado': None,
                'ClaveEntFed': None,
                'SubContratacion': []
            },
            'Percepciones': {
                'numPercepciones': None,
                'TotalSueldos': None,
                'TotalSeparacionIndemnizacion': None,
                'TotalJubilacionPensionRetiro': None,
                'TotalGravado': None,
                'TotalExento': None,
                'Percepcion': [],
                'JubilacionPensionRetiro': {
                    'TotalUnaExhibicion': None,
                    'TotalParcialidad': None,
                    'MontoDiario': None,
                    'IngresoAcumulable': None,
                    'IngresoNoAcumulable': None,
                },
                'SeparacionIndemnizacion': {
                    'TotalPagado': None,
                    'NumAnosServicio': None,
                    'UltimoSueldoMensOrd': None,
                    'IngresoAcumulable': None,
                    'IngresoNoAcumulable': None,
                },
            },
            'Deducciones': {
                'numDeducciones': None,
                'TotalOtrasDeducciones': None,
                'TotalImpuestosRetenidos': None,
                'Deduccion': []
            },
            'OtrosPagos': {
                'numOtroPago': None,
                'OtroPago': [],
            },
            'Incapacidades': {
                'numIncapacidad': None,
                'Incapacidad': [],
            }
        }

        self.generate_json()
        if self.is_valid:
            self.generate_xml()

    def generate_json(self):
        self.is_valid = False
        self.error = 'Error al crear JSON'
        try:
            parser_nom = False

            with open(self.txt_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='|')
                for row in csv_reader:

                    row = [i if i else None for i in row]

                    header = row.pop(0).replace(':', '').replace('\t', '')
                    if header == 'ComplementoNomina':
                        parser_nom = True
                        pos_payroll = -1
                        pos_perception = -1
                        pos_other_payment = -1

                    # DATOS DE CFDI
                    if header == "Comprobante":
                        self.CFDI_DICT['Comprobante'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        if self.CFDI_DICT['Comprobante']['Version'] == '4.0':
                            self.switch_version = True
                            self.CFDI_DICT['Comprobante']['Version'] = '3.3'

                    elif header == "CfdiRelacionados":
                        self.CFDI_DICT['CfdiRelacionados'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "CfdiRelacionado":
                        self.CFDI_DICT['CfdiRelacionados']['CfdiRelacionado'].append(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Emisor" and not parser_nom:
                        self.CFDI_DICT['Emisor'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        # if self.CFDI_DICT['Emisor']['Rfc'] != self.taxpayer_id:
                        #     self.error = 'Rfc emisor es distinto al Rfc del negocio'
                        #     raise Exception(self.error)

                    elif header == "Receptor" and not parser_nom:
                        if self.switch_version:
                            row[4] = 'P01'
                            row[2] = None
                            row[3] = None
                        self.CFDI_DICT['Receptor'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == 'Concepto':
                        self.CFDI_DICT['Concepto'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    # DATOS DE LA NOMINA
                    elif header == 'Nomina':
                        self.CFDI_DICT['Nominas'].append(self.PAYROLL_DICT.copy())
                        pos_payroll += 1
                        self.CFDI_DICT['Nominas'][pos_payroll]['Nomina'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        # if self.CFDI_DICT['Nominas'][pos_payroll]['Nomina']['TotalOtrosPagos'] == "0.00":
                        #     self.CFDI_DICT['Nominas'][pos_payroll]['Nomina']['TotalOtrosPagos'] = None

                    elif header == "Emisor" and parser_nom:
                        self.CFDI_DICT['Nominas'][pos_payroll]['Emisor'].update(dict(zip(self.CFDI_HEADERS['NomEmisor'], row)))

                    elif header == "EntidadSNCF":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Emisor']['EntidadSNCF'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Receptor" and parser_nom:
                        if self.switch_version:
                            if row[-2] == 'CMX':
                                row[-2] = 'DIF'
                        self.CFDI_DICT['Nominas'][pos_payroll]['Receptor'].update(dict(zip(self.CFDI_HEADERS['NomReceptor'], row)))

                    elif header == "SubContratacion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['SubContratacion'].append(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Percepciones":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones'].update((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "Percepcion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'].append(dict(zip(self.CFDI_HEADERS[header], row)))
                        pos_perception += 1
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['AccionesOTitulos'] = {}
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['HorasExtra'] = []

                    elif header == "AccionesOTitulos":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['AccionesOTitulos'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "HorasExtra":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['HorasExtra'].append(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "JubilacionPensionRetiro":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['JubilacionPensionRetiro'].update((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "SeparacionIndemnizacion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['SeparacionIndemnizacion'].update((dict(zip(self.CFDI_HEADERS[header], row))))
                        SI = self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['SeparacionIndemnizacion']
                        if SI['TotalPagado'] and float(SI['TotalPagado']) > 0:
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['NumSeguridadSocial'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['FechaInicioRelLaboral'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['Antiguedad'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['RiesgoPuesto'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['SalarioDiarioIntegrado'] = None

                    elif header == "Deducciones":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Deducciones'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Deduccion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Deducciones']['Deduccion'].append((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "OtrosPagos":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        if int(self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['numOtroPago']) == 0:
                            self.CFDI_DICT['Nominas'][pos_payroll]['Nomina']['TotalOtrosPagos'] = None

                    elif header == "OtroPago":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'].append((dict(zip(self.CFDI_HEADERS[header], row))))
                        pos_other_payment += 1
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['SubsidioAlEmpleo'] = {}
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['CompensacionSaldosAFavor'] = {}

                    elif header == "SubsidioAlEmpleo":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['SubsidioAlEmpleo'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "CompensacionSaldosAFavor":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['CompensacionSaldosAFavor'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Incapacidades":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Incapacidades'].update((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "Incapacidad":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Incapacidades']['Incapacidad'].append((dict(zip(self.CFDI_HEADERS[header], row))))

                    # DATOS DE OBSERVACIONES
                    elif header == 'Observaciones':
                        self.CFDI_DICT['Observaciones'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == 'Extras':
                        self.CFDI_DICT['Extras'].update(dict(zip(self.CFDI_HEADERS[header], row)))

            self.json = copy.deepcopy(self.CFDI_DICT)
            self.serie = self.json['Comprobante']['Serie']
            self.folio = self.json['Comprobante']['Folio']
            self.receptor = self.json['Receptor']['Rfc']

            self.is_valid = True

        except Exception as e:
            print('Exception in PARSER_NOM[generate_json] => {}'.format(str(e)))

    def generate_xml(self):
        try:
            self.is_valid = False
            ns_ = 'xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nomina12="http://www.sat.gob.mx/nomina12" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd"'
            self.CFDI_DICT['Comprobante']['ns_'] = ns_

            # COMPROBANTE
            try:
                comprobante = self.CFDI_DICT.pop('Comprobante')
                self.cfdi_obj = CFDI_33.Comprobante(**comprobante)
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Comprobante | {}".format(str(e)))

            # CFDI RELACIONADOS
            try:
                cfdi_relacionados = self.CFDI_DICT.pop('CfdiRelacionados')
                cfdis_relacionado = cfdi_relacionados['CfdiRelacionado']

                if cfdis_relacionado:
                    cfdi_relacionados = CFDI_33.CfdiRelacionadosType(
                        TipoRelacion=cfdi_relacionados['TipoRelacion'])

                    for cfdi_relacionado in cfdis_relacionado:
                        cfdi_relacionados.add_CfdiRelacionado(
                            CFDI_33.CfdiRelacionadoType(
                                UUID=cfdi_relacionado['UUID'])
                        )

                    self.cfdi_obj.set_CfdiRelacionados(cfdi_relacionados)
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() CfdiRelacionados | {}".format(
                        str(e)))

            # EMISOR
            try:
                emisor = self.CFDI_DICT.pop('Emisor')
                self.cfdi_obj.set_Emisor(CFDI_33.EmisorType(**emisor))
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Emisor | {}".format(str(e)))

            # RECEPTOR
            try:
                receptor = self.CFDI_DICT.pop('Receptor')
                self.cfdi_obj.set_Receptor(CFDI_33.ReceptorType(**receptor))
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Receptor | {}".format(str(e)))

            # CONCEPTOS
            try:
                concepto = self.CFDI_DICT.pop('Concepto')
                conceptos = CFDI_33.ConceptosType()
                conceptos.add_Concepto(CFDI_33.ConceptoType(**concepto))
                self.cfdi_obj.set_Conceptos(conceptos)
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Conceptos | {}".format(str(e)))

            # COMPLEMENTO DE NOMINA
            nominas = self.CFDI_DICT.pop('Nominas')
            complemento_obj = CFDI_33.ComplementoType()

            for nomina_dic in nominas:

                # NOMINA
                try:
                    nomina = nomina_dic.pop('Nomina')
                    self.nomina = Nomina(**nomina)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Nomina | {}".format(str(e)))

                # EMISOR
                try:
                    emisor = nomina_dic.pop('Emisor')
                    entidad = emisor.pop('EntidadSNCF')
                    emisor_type = NomEmisorType(**emisor)

                    if entidad['OrigenRecurso'] is not None:
                        emisor_type.set_EntidadSNCF(EntidadSNCFType(
                            **entidad))

                    self.nomina.set_Emisor(emisor_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() NominaEmisor | {}".format(
                            str(e)))

                # RECEPTOR
                try:
                    receptor = nomina_dic.pop('Receptor')
                    numSubContrataciones = int(receptor.pop('numSubContrataciones'))
                    sub_contratacion_list = receptor.pop('SubContratacion')
                    receptor_type = NomReceptorType(**receptor)
                    if numSubContrataciones > 0:
                        for sub_contratacion in sub_contratacion_list:
                            receptor_type.add_SubContratacion(
                                SubContratacionType(**sub_contratacion))

                    self.nomina.set_Receptor(receptor_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() NominaReceptor | {}".format(
                            str(e)))

                # PERCEPCIONES
                try:
                    percepciones = nomina_dic.pop('Percepciones')
                    num_percepciones = int(percepciones.pop('numPercepciones'))
                    if num_percepciones > 0:
                        list_percepciones = percepciones.pop('Percepcion')
                        jubilacion_pension_retiro = percepciones.pop(
                            'JubilacionPensionRetiro')
                        separacion_indemnizacion = percepciones.pop(
                            'SeparacionIndemnizacion')
                        percepciones_type = NomPercepcionesType(**percepciones)

                        # JubilacionPensionRetiro
                        if jubilacion_pension_retiro['IngresoAcumulable']:
                            percepciones_type.set_JubilacionPensionRetiro(
                                JubilacionPensionRetiroType(
                                    **jubilacion_pension_retiro))
                        # Percepcion
                        for percepcion in list_percepciones:
                            percepcion.pop('numHorasExtra')
                            acciones_o_titulos = percepcion.pop('AccionesOTitulos')
                            horas_extra = percepcion.pop('HorasExtra')
                            percepcion_type = NomPercepcionType(**percepcion)

                            # AccionesOTitulos
                            if acciones_o_titulos['ValorMercado'] and \
                                    acciones_o_titulos['PrecioAlOtorgarse']:
                                percepcion_type.set_AccionesOTitulos(
                                    AccionesOTitulosType(**acciones_o_titulos))

                            # HorasExtra
                            for hora_extra in horas_extra:
                                percepcion_type.add_HorasExtra(
                                    HorasExtraType(**hora_extra))

                            percepciones_type.add_Percepcion(percepcion_type)

                        # SeparacionIndemnizacion
                        if separacion_indemnizacion['TotalPagado']:
                            percepciones_type.set_SeparacionIndemnizacion(
                                SeparacionIndemnizacionType(
                                    **separacion_indemnizacion))

                        self.nomina.set_Percepciones(percepciones_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Percepciones | {}".format(
                            str(e)))

                # DEDUCCIONES
                try:
                    deducciones = nomina_dic.pop('Deducciones')
                    num_deducciones = int(deducciones.pop('numDeducciones'))
                    if num_deducciones > 0:
                        deducciones_list = deducciones.pop('Deduccion')
                        deducciones_type = NomDeduccionesType(**deducciones)
                        for deduccion in deducciones_list:
                            if isinstance(deduccion, dict):
                                deducciones_type.add_Deduccion(
                                    NomDeduccionType(**deduccion))
                        self.nomina.set_Deducciones(deducciones_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Deducciones | {}".format(
                            str(e)))

                # OTROSPAGOS
                try:
                    otros_pagos = nomina_dic.pop('OtrosPagos')
                    num_otro_pago = int(otros_pagos.pop('numOtroPago'))
                    if num_otro_pago > 0:
                        otros_pagos_list = otros_pagos.pop('OtroPago')
                        otros_pagos_type = OtrosPagosType()
                        for otro_pago in otros_pagos_list:
                            if isinstance(otro_pago, dict):
                                subsidio_al_empleo = otro_pago.pop(
                                    'SubsidioAlEmpleo')
                                Compensacion_Saldos_a_favor = otro_pago.pop(
                                    'CompensacionSaldosAFavor')

                                otro_pago_type = OtroPagoType(**otro_pago)

                                if subsidio_al_empleo['SubsidioCausado'] \
                                        is not None:
                                    otro_pago_type.set_SubsidioAlEmpleo(
                                        SubsidioAlEmpleoType(
                                            **subsidio_al_empleo))

                                if Compensacion_Saldos_a_favor['Ano'] is not None and Compensacion_Saldos_a_favor['SaldoAFavor'] is not None:
                                    otro_pago_type.set_CompensacionSaldosAFavor(CompensacionSaldosAFavorType(**Compensacion_Saldos_a_favor))

                                otros_pagos_type.add_OtroPago(otro_pago_type)
                        self.nomina.set_OtrosPagos(otros_pagos_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() OtrosPagos | {}".format(
                            str(e)))

                # Incapacidades
                try:
                    incapacidades = nomina_dic.pop('Incapacidades')
                    num_incapacidad = int(incapacidades.pop('numIncapacidad'))
                    if num_incapacidad > 0:
                        incapacidades_list = incapacidades.pop('Incapacidad')
                        incapacidades_type = IncapacidadesType(**incapacidades)
                        for incapacidad in incapacidades_list:
                            if isinstance(incapacidad, dict):
                                incapacidades_type.add_Incapacidad(
                                    IncapacidadType(**incapacidad))
                        self.nomina.set_Incapacidades(incapacidades_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Incapacidades | {}".format(
                            str(e)))

                complemento_obj.add_anytypeobjs_(self.nomina)

            self.cfdi_obj.set_Complemento(complemento_obj)

            output = StringIO.StringIO()
            self.cfdi_obj.export(
                output,
                0,
                pretty_print=True,
                namespace_complement_=self.namespace
            )
            xml_str = output.getvalue()
            parser = etree.XMLParser(ns_clean=True)
            cfdi_etree = etree.fromstring(xml_str, parser=parser)
            self.cfdi = etree.tostring(
                cfdi_etree, encoding='utf-8', xml_declaration=True)

            self.is_valid = True

        except Exception as e:
            print('Exception in PARSER_NOM[to_xml] => {}'.format(str(e)))
            self.error = 'Error al crear XML'

    '''def stamp_xml(self):
        try:
            response, client = FinkokWS.stamp(self.cfdi)

            # CUANDO EL XML SE TIMBRA
            if hasattr(response, 'CodEstatus') and \
                    'timbrado' in response.CodEstatus:
                pass

            # CUANDO EL XML YA TIENE UN TIMBRE PREVIO
            elif hasattr(response, 'CodEstatus') and \
                    'Comprobante timbrado previamente' in response.CodEstatus:
                pass

            # CUANDO EL XML TIENE ERRORES EN EL TIMBRADO
            elif hasattr(response, 'Incidencias') and response.Incidencias:
                pass

            # ERROR NO CONTROLADO
            else:
                raise Exception('Exception in stamp process')
        except Exception as e:
            print('Exception in PARSER_NOM[to_xml] => {}'.format(str(e)))
            self.payroll_obj.status = 'E'
            self.payroll_obj.notes = 'Error al timbrar XML'
            self.payroll_obj.save()
    '''


class PARSER_NOM_V4_PAE(object):
    """
        CLASE ENCARGADA DE CREAR EL XML DE NOMINA
        CFDI 4.0 Y NOMINA 1.2
    """

    def __init__(self, txt_path=None, business_obj=None):

        self.txt_path = txt_path
        self.business_obj = business_obj
        self.taxpayer_id = business_obj.taxpayer_id
        self.namespace = 'nomina12:'
        self.is_valid = False
        self.error = None

        self.json = None
        self.cfdi = None
        self.serie = None
        self.folio = None
        self.receptor = None

        self.CFDI_HEADERS = {
            'Comprobante': [
                'Version', 'Serie', 'Folio', 'Fecha', 'FormaPago',
                'NoCertificado', 'SubTotal', 'Descuento', 'Moneda',
                'TipoCambio', 'Total', 'TipoDeComprobante', 'MetodoPago',
                'LugarExpedicion', 'Confirmacion', 'Exportacion'
            ],
            'CfdiRelacionados': ['numCfdiRelacionados', 'TipoRelacion'],
            'CfdiRelacionado': ['UUID'],
            'Emisor': ['Rfc', 'Nombre', 'RegimenFiscal'],
            'Receptor': [
                'Rfc', 'Nombre', 'DomicilioFiscalReceptor', 'RegimenFiscalReceptor', 'UsoCFDI'
            ],
            'Concepto': [
                'ClaveProdServ', 'Cantidad', 'ClaveUnidad',
                'Descripcion', 'ValorUnitario', 'Importe', 'Descuento', 'ObjetoImp'
            ],
            'ComplementoNomina': ['numNominas'],
            'Nomina': [
                'Version', 'TipoNomina', 'FechaPago', 'FechaInicialPago',
                'FechaFinalPago', 'NumDiasPagados', 'TotalPercepciones',
                'TotalDeducciones', 'TotalOtrosPagos'
            ],
            'NomEmisor': ['Curp', 'RegistroPatronal', 'RfcPatronOrigen'],
            'EntidadSNCF': ['OrigenRecurso', 'MontoRecursoPropio'],
            'NomReceptor': [
                'numSubContrataciones', 'Curp', 'NumSeguridadSocial',
                'FechaInicioRelLaboral', 'Antiguedad', 'TipoContrato',
                'Sindicalizado', 'TipoJornada', 'TipoRegimen', 'NumEmpleado',
                'Departamento', 'Puesto', 'RiesgoPuesto', 'PeriodicidadPago',
                'Banco', 'CuentaBancaria', 'SalarioBaseCotApor',
                'SalarioDiarioIntegrado', 'ClaveEntFed'
            ],
            'SubContratacion': ['RfcLabora', 'PorcentajeTiempo'],
            'Percepciones': [
                'numPercepciones', 'TotalSueldos', 'TotalSeparacionIndemnizacion',
                'TotalJubilacionPensionRetiro', 'TotalGravado', 'TotalExento'
            ],
            'Percepcion': [
                'numHorasExtra', 'TipoPercepcion', 'Clave', 'Concepto',
                'ImporteGravado', 'ImporteExento'
            ],
            'AccionesOTitulos': ['ValorMercado', 'PrecioAlOtorgarse'],
            'HorasExtra': ['Dias', 'TipoHoras', 'HorasExtra', 'ImportePagado'],
            'JubilacionPensionRetiro': [
                'TotalUnaExhibicion', 'TotalParcialidad', 'MontoDiario',
                'IngresoAcumulable', 'IngresoNoAcumulable'
            ],
            'SeparacionIndemnizacion': [
                'TotalPagado', 'NumAnosServicio', 'UltimoSueldoMensOrd',
                'IngresoAcumulable', 'IngresoNoAcumulable'
            ],
            'Deducciones': [
                'numDeducciones', 'TotalOtrasDeducciones',
                'TotalImpuestosRetenidos'
            ],
            'Deduccion': ['TipoDeduccion', 'Clave', 'Concepto', 'Importe'],
            'OtrosPagos': ['numOtroPago'],
            'OtroPago': ['TipoOtroPago', 'Clave', 'Concepto', 'Importe'],
            'SubsidioAlEmpleo': ['SubsidioCausado'],
            'CompensacionSaldosAFavor': ['SaldoAFavor', 'Ano', 'RemanenteSalFav'],
            'Incapacidades': ['numIncapacidad'],
            'Incapacidad': [
                'DiasIncapacidad', 'TipoIncapacidad', 'ImporteMonetario'
            ],
            'Observaciones': ['Observacion'],
            'Extras': ['num', 'PAE_EMAIL', 'email', 'PAE_MENSAJE', 'message', 'LUGAR_PAGO_ESTADO', 'state', 'LUGAR_PAGO_MUNICIPIO', 'municipality'],
        }

        self.CFDI_DICT = {
            'Comprobante': {},
            'CfdiRelacionados': {
                'numCfdiRelacionados': None,
                'TipoRelacion': None,
                'CfdiRelacionado': [],
            },
            'Emisor': {},
            'Receptor': {},
            'Concepto': {},
            'Nominas': [],
            'Observaciones': {},
            'Extras': {}
        }

        self.PAYROLL_DICT = {
            'Nomina': {
                'Version': '1.2',
                'TipoNomina': None,
                'FechaPago': None,
                'FechaInicialPago': None,
                'FechaFinalPago': None,
                'NumDiasPagados': None,
                'TotalPercepciones': None,
                'TotalDeducciones': None,
                'TotalOtrosPagos': None,
            },
            'Emisor': {
                'Curp': None,
                'RegistroPatronal': None,
                'RfcPatronOrigen': None,
                'EntidadSNCF': {}
            },
            'Receptor': {
                'numSubContrataciones': None,
                'Curp': None,
                'NumSeguridadSocial': None,
                'FechaInicioRelLaboral': None,
                'Antiguedad': None,
                'TipoContrato': None,
                'Sindicalizado': None,
                'TipoJornada': None,
                'TipoRegimen': None,
                'NumEmpleado': None,
                'Departamento': None,
                'Puesto': None,
                'RiesgoPuesto': None,
                'PeriodicidadPago': None,
                'Banco': None,
                'CuentaBancaria': None,
                'SalarioBaseCotApor': None,
                'SalarioDiarioIntegrado': None,
                'ClaveEntFed': None,
                'SubContratacion': []
            },
            'Percepciones': {
                'numPercepciones': None,
                'TotalSueldos': None,
                'TotalSeparacionIndemnizacion': None,
                'TotalJubilacionPensionRetiro': None,
                'TotalGravado': None,
                'TotalExento': None,
                'Percepcion': [],
                'JubilacionPensionRetiro': {
                    'TotalUnaExhibicion': None,
                    'TotalParcialidad': None,
                    'MontoDiario': None,
                    'IngresoAcumulable': None,
                    'IngresoNoAcumulable': None,
                },
                'SeparacionIndemnizacion': {
                    'TotalPagado': None,
                    'NumAnosServicio': None,
                    'UltimoSueldoMensOrd': None,
                    'IngresoAcumulable': None,
                    'IngresoNoAcumulable': None,
                },
            },
            'Deducciones': {
                'numDeducciones': None,
                'TotalOtrasDeducciones': None,
                'TotalImpuestosRetenidos': None,
                'Deduccion': []
            },
            'OtrosPagos': {
                'numOtroPago': None,
                'OtroPago': [],
            },
            'Incapacidades': {
                'numIncapacidad': None,
                'Incapacidad': [],
            }
        }

        self.generate_json()
        if self.is_valid:
            self.generate_xml()

    def generate_json(self):
        self.is_valid = False
        self.error = 'Error al crear JSON'
        try:
            parser_nom = False

            with open(self.txt_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='|')
                for row in csv_reader:

                    row = [i if i else None for i in row]

                    header = row.pop(0).replace(':', '').replace('\t', '')
                    if header == 'ComplementoNomina':
                        parser_nom = True
                        pos_payroll = -1
                        pos_perception = -1
                        pos_other_payment = -1

                    # DATOS DE CFDI
                    if header == "Comprobante":
                        self.CFDI_DICT['Comprobante'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        self.CFDI_DICT['Comprobante'].pop('FormaPago')
                        self.CFDI_DICT['Comprobante'].pop('TipoCambio')

                    elif header == "CfdiRelacionados":
                        self.CFDI_DICT['CfdiRelacionados'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "CfdiRelacionado":
                        self.CFDI_DICT['CfdiRelacionados']['CfdiRelacionado'].append(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Emisor" and not parser_nom:
                        self.CFDI_DICT['Emisor'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        self.CFDI_DICT['Emisor']['Nombre'] = self.business_obj.sat_name

                    elif header == "Receptor" and not parser_nom:
                        self.CFDI_DICT['Receptor'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == 'Concepto':
                        self.CFDI_DICT['Concepto'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    # DATOS DE LA NOMINA
                    elif header == 'Nomina':
                        self.CFDI_DICT['Nominas'].append(self.PAYROLL_DICT.copy())
                        pos_payroll += 1
                        self.CFDI_DICT['Nominas'][pos_payroll]['Nomina'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        # if self.CFDI_DICT['Nominas'][pos_payroll]['Nomina']['TotalOtrosPagos'] == "0.00":
                        #     self.CFDI_DICT['Nominas'][pos_payroll]['Nomina']['TotalOtrosPagos'] = None

                    elif header == "Emisor" and parser_nom:
                        self.CFDI_DICT['Nominas'][pos_payroll]['Emisor'].update(dict(zip(self.CFDI_HEADERS['NomEmisor'], row)))

                    elif header == "EntidadSNCF":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Emisor']['EntidadSNCF'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Receptor" and parser_nom:
                        self.CFDI_DICT['Nominas'][pos_payroll]['Receptor'].update(dict(zip(self.CFDI_HEADERS['NomReceptor'], row)))
                        if self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['ClaveEntFed'] == 'DIF':
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['ClaveEntFed'] = 'CMX'


                    elif header == "SubContratacion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['SubContratacion'].append(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Percepciones":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones'].update((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "Percepcion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'].append(dict(zip(self.CFDI_HEADERS[header], row)))
                        pos_perception += 1
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['AccionesOTitulos'] = {}
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['HorasExtra'] = []

                    elif header == "AccionesOTitulos":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['AccionesOTitulos'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "HorasExtra":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['Percepcion'][pos_perception]['HorasExtra'].append(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "JubilacionPensionRetiro":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['JubilacionPensionRetiro'].update((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "SeparacionIndemnizacion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['SeparacionIndemnizacion'].update((dict(zip(self.CFDI_HEADERS[header], row))))
                        SI = self.CFDI_DICT['Nominas'][pos_payroll]['Percepciones']['SeparacionIndemnizacion']
                        if SI['TotalPagado'] and float(SI['TotalPagado']) > 0:
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['NumSeguridadSocial'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['FechaInicioRelLaboral'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['Antiguedad'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['RiesgoPuesto'] = None
                            self.CFDI_DICT['Nominas'][pos_payroll]['Receptor']['SalarioDiarioIntegrado'] = None

                    elif header == "Deducciones":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Deducciones'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Deduccion":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Deducciones']['Deduccion'].append((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "OtrosPagos":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos'].update(dict(zip(self.CFDI_HEADERS[header], row)))
                        if int(self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['numOtroPago']) == 0:
                            self.CFDI_DICT['Nominas'][pos_payroll]['Nomina']['TotalOtrosPagos'] = None

                    elif header == "OtroPago":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'].append((dict(zip(self.CFDI_HEADERS[header], row))))
                        pos_other_payment += 1
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['SubsidioAlEmpleo'] = {}
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['CompensacionSaldosAFavor'] = {}

                    elif header == "SubsidioAlEmpleo":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['SubsidioAlEmpleo'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "CompensacionSaldosAFavor":
                        self.CFDI_DICT['Nominas'][pos_payroll]['OtrosPagos']['OtroPago'][pos_other_payment]['CompensacionSaldosAFavor'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == "Incapacidades":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Incapacidades'].update((dict(zip(self.CFDI_HEADERS[header], row))))

                    elif header == "Incapacidad":
                        self.CFDI_DICT['Nominas'][pos_payroll]['Incapacidades']['Incapacidad'].append((dict(zip(self.CFDI_HEADERS[header], row))))

                    # DATOS DE OBSERVACIONES
                    elif header == 'Observaciones':
                        self.CFDI_DICT['Observaciones'].update(dict(zip(self.CFDI_HEADERS[header], row)))

                    elif header == 'Extras':
                        self.CFDI_DICT['Extras'].update(dict(zip(self.CFDI_HEADERS[header], row)))

            self.json = copy.deepcopy(self.CFDI_DICT)
            self.serie = self.json['Comprobante']['Serie']
            self.folio = self.json['Comprobante']['Folio']
            self.receptor = self.json['Receptor']['Rfc']

            self.is_valid = True

        except Exception as e:
            print('Exception in PARSER_NOM_V4_PAE[generate_json] => {}'.format(str(e)))

    def generate_xml(self):
        try:
            self.is_valid = False
            ns_ = 'xmlns:cfdi="http://www.sat.gob.mx/cfd/4" xmlns:nomina12="http://www.sat.gob.mx/nomina12" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd"'
            self.CFDI_DICT['Comprobante']['ns_'] = ns_

            # COMPROBANTE
            try:
                comprobante = self.CFDI_DICT.pop('Comprobante')
                self.cfdi_obj = CFDI_40.Comprobante(**comprobante)
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Comprobante | {}".format(str(e)))

            # CFDI RELACIONADOS
            try:
                cfdi_relacionados = self.CFDI_DICT.pop('CfdiRelacionados')
                cfdis_relacionado = cfdi_relacionados['CfdiRelacionado']
                if cfdis_relacionado:
                    cfdi_relacionados = CFDI_40.CfdiRelacionadosType(
                        TipoRelacion=cfdi_relacionados['TipoRelacion'])

                    for cfdi_relacionado in cfdis_relacionado:
                        cfdi_relacionados.add_CfdiRelacionado(
                            CFDI_40.CfdiRelacionadoType(
                                UUID=cfdi_relacionado['UUID'])
                        )

                    self.cfdi_obj.add_CfdiRelacionados(cfdi_relacionados)
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() CfdiRelacionados | {}".format(
                        str(e)))

            # EMISOR
            try:
                emisor = self.CFDI_DICT.pop('Emisor')
                self.cfdi_obj.set_Emisor(CFDI_40.EmisorType(**emisor))
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Emisor | {}".format(str(e)))

            # RECEPTOR
            try:
                receptor = self.CFDI_DICT.pop('Receptor')
                self.cfdi_obj.set_Receptor(CFDI_40.ReceptorType(**receptor))
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Receptor | {}".format(str(e)))

            # CONCEPTOS
            try:
                concepto = self.CFDI_DICT.pop('Concepto')
                conceptos = CFDI_40.ConceptosType()
                conceptos.add_Concepto(CFDI_40.ConceptoType(**concepto))
                self.cfdi_obj.set_Conceptos(conceptos)
            except Exception as e:
                raise Exception(
                    "Exception generate_xml() Conceptos | {}".format(str(e)))

            # COMPLEMENTO DE NOMINA
            nominas = self.CFDI_DICT.pop('Nominas')
            complemento_obj = CFDI_40.ComplementoType()

            for nomina_dic in nominas:

                # NOMINA
                try:
                    nomina = nomina_dic.pop('Nomina')
                    self.nomina = Nomina(**nomina)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Nomina | {}".format(str(e)))

                # EMISOR
                try:
                    emisor = nomina_dic.pop('Emisor')
                    entidad = emisor.pop('EntidadSNCF')
                    emisor_type = NomEmisorType(**emisor)

                    if entidad['OrigenRecurso'] is not None:
                        emisor_type.set_EntidadSNCF(EntidadSNCFType(
                            **entidad))

                    self.nomina.set_Emisor(emisor_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() NominaEmisor | {}".format(
                            str(e)))

                # RECEPTOR
                try:
                    receptor = nomina_dic.pop('Receptor')
                    numSubContrataciones = int(receptor.pop('numSubContrataciones'))
                    sub_contratacion_list = receptor.pop('SubContratacion')
                    receptor_type = NomReceptorType(**receptor)
                    if numSubContrataciones > 0:
                        for sub_contratacion in sub_contratacion_list:
                            receptor_type.add_SubContratacion(
                                SubContratacionType(**sub_contratacion))

                    self.nomina.set_Receptor(receptor_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() NominaReceptor | {}".format(
                            str(e)))

                # PERCEPCIONES
                try:
                    percepciones = nomina_dic.pop('Percepciones')
                    num_percepciones = int(percepciones.pop('numPercepciones'))
                    if num_percepciones > 0:
                        list_percepciones = percepciones.pop('Percepcion')
                        jubilacion_pension_retiro = percepciones.pop(
                            'JubilacionPensionRetiro')
                        separacion_indemnizacion = percepciones.pop(
                            'SeparacionIndemnizacion')
                        percepciones_type = NomPercepcionesType(**percepciones)

                        # JubilacionPensionRetiro
                        if jubilacion_pension_retiro['IngresoAcumulable']:
                            percepciones_type.set_JubilacionPensionRetiro(
                                JubilacionPensionRetiroType(
                                    **jubilacion_pension_retiro))
                        # Percepcion
                        for percepcion in list_percepciones:
                            percepcion.pop('numHorasExtra')
                            acciones_o_titulos = percepcion.pop('AccionesOTitulos')
                            horas_extra = percepcion.pop('HorasExtra')
                            percepcion_type = NomPercepcionType(**percepcion)

                            # AccionesOTitulos
                            if acciones_o_titulos['ValorMercado'] and \
                                    acciones_o_titulos['PrecioAlOtorgarse']:
                                percepcion_type.set_AccionesOTitulos(
                                    AccionesOTitulosType(**acciones_o_titulos))

                            # HorasExtra
                            for hora_extra in horas_extra:
                                percepcion_type.add_HorasExtra(
                                    HorasExtraType(**hora_extra))

                            percepciones_type.add_Percepcion(percepcion_type)

                        # SeparacionIndemnizacion
                        if separacion_indemnizacion['TotalPagado']:
                            percepciones_type.set_SeparacionIndemnizacion(
                                SeparacionIndemnizacionType(
                                    **separacion_indemnizacion))

                        self.nomina.set_Percepciones(percepciones_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Percepciones | {}".format(
                            str(e)))

                # DEDUCCIONES
                try:
                    deducciones = nomina_dic.pop('Deducciones')
                    num_deducciones = int(deducciones.pop('numDeducciones'))
                    if num_deducciones > 0:
                        deducciones_list = deducciones.pop('Deduccion')
                        deducciones_type = NomDeduccionesType(**deducciones)
                        for deduccion in deducciones_list:
                            if isinstance(deduccion, dict):
                                deducciones_type.add_Deduccion(
                                    NomDeduccionType(**deduccion))
                        self.nomina.set_Deducciones(deducciones_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Deducciones | {}".format(
                            str(e)))

                # OTROSPAGOS
                try:
                    otros_pagos = nomina_dic.pop('OtrosPagos')
                    num_otro_pago = int(otros_pagos.pop('numOtroPago'))
                    if num_otro_pago > 0:
                        otros_pagos_list = otros_pagos.pop('OtroPago')
                        otros_pagos_type = OtrosPagosType()
                        for otro_pago in otros_pagos_list:
                            if isinstance(otro_pago, dict):
                                subsidio_al_empleo = otro_pago.pop(
                                    'SubsidioAlEmpleo')
                                Compensacion_Saldos_a_favor = otro_pago.pop(
                                    'CompensacionSaldosAFavor')

                                otro_pago_type = OtroPagoType(**otro_pago)

                                if subsidio_al_empleo['SubsidioCausado'] \
                                        is not None:
                                    otro_pago_type.set_SubsidioAlEmpleo(
                                        SubsidioAlEmpleoType(
                                            **subsidio_al_empleo))

                                if Compensacion_Saldos_a_favor['Ano'] is not None and Compensacion_Saldos_a_favor['SaldoAFavor'] is not None:
                                    otro_pago_type.set_CompensacionSaldosAFavor(CompensacionSaldosAFavorType(**Compensacion_Saldos_a_favor))

                                otros_pagos_type.add_OtroPago(otro_pago_type)
                        self.nomina.set_OtrosPagos(otros_pagos_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() OtrosPagos | {}".format(
                            str(e)))

                # Incapacidades
                try:
                    incapacidades = nomina_dic.pop('Incapacidades')
                    num_incapacidad = int(incapacidades.pop('numIncapacidad'))
                    if num_incapacidad > 0:
                        incapacidades_list = incapacidades.pop('Incapacidad')
                        incapacidades_type = IncapacidadesType(**incapacidades)
                        for incapacidad in incapacidades_list:
                            if isinstance(incapacidad, dict):
                                incapacidades_type.add_Incapacidad(
                                    IncapacidadType(**incapacidad))
                        self.nomina.set_Incapacidades(incapacidades_type)
                except Exception as e:
                    raise Exception(
                        "Exception generate_xml() Incapacidades | {}".format(
                            str(e)))

                complemento_obj.add_anytypeobjs_(self.nomina)

            self.cfdi_obj.set_Complemento(complemento_obj)

            output = StringIO.StringIO()
            self.cfdi_obj.export(
                output,
                0,
                pretty_print=True,
                namespacedef_=ns_
            )
            xml_str = output.getvalue()
            parser = etree.XMLParser(ns_clean=True)
            cfdi_etree = etree.fromstring(xml_str, parser=parser)
            self.cfdi = etree.tostring(
                cfdi_etree, encoding='utf-8', xml_declaration=True)

            self.is_valid = True

        except Exception as e:
            print('Exception in PARSER_NOM_V4_PAE[to_xml] => {}'.format(str(e)))
            self.error = 'Error al crear XML'
