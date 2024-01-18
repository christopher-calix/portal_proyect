####        create pdf          ###

dom_dicc = {
  'FOR8203044R2':{
    'domicilio':'<b>RFC: FOR8203044R2<br/>Domicilio Fiscal:<br/>Calle 6 No. 2510 Zona Industrial C.P. 44940<br/>GUADALAJARA, JALISCO, MEXICO<br/>Tels: (52) 33-3268-0500 GENERAL<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0508 VENTAS<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0505<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0507 TRAFICO<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0501 FAX</b>'
  }
}

TIPO_COMPROBANTE = {
  'I': u'I - Ingreso',
  'E': u'E - Egreso',
  'T': u'T - Traslado',
  'N': u'N - Nómina  ',
  'P': u'P - Pago'
}

METODO_PAGO = {
  'PUE': u'PUE - Pago en una sola exhibición',
  'PIP': u'PIP - Pago inicial y parcialidades',
  'PPD': u'PPD - Pago en parcialidades o diferido'
}

IMP_DES = {
  '001': '001-ISR',
  '002': '002-IVA',
  '003': '003-IEPS'
}

REG_FIS = {
  '601': u'601 - General de Ley Personas Morales',
  '603': u'603 - Personas Morales con Fines no Lucrativos',
  '605': u'605 - Sueldos y Salarios e Ingresos Asimilados a Salarios',
  '606': u'606 - Arrendamiento',
  '608': u'608 - Demás ingresos',
  '609': u'609 - Consolidación',
  '610': u'610 - Residentes en el Extranjero sin Establecimiento Permanente en México',
  '611': u'611 - Ingresos por Dividendos (socios y accionistas)',
  '612': u'612 - Personas Físicas con Actividades Empresariales y Profesionales',
  '614': u'614 - Ingresos por intereses',
  '616': u'616 - Sin obligaciones fiscales',
  '620': u'620 - Sociedades Cooperativas de Producción que optan por diferir sus ingresos',
  '621': u'621 - Incorporación Fiscal',
  '622': u'622 - Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras',
  '623': u'623 - Opcional para Grupos de Sociedades',
  '624': u'624 - Coordinados',
  '628': u'628 - Hidrocarburos',
  '607': u'607 - Régimen de Enajenación o Adquisición de Bienes',
  '629': u'629 - De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales',
  '630': u'630 - Enajenación de acciones en bolsa de valores',
  '615': u'615 - Régimen de los ingresos por obtención de premios'
}

FOR_PA = {
  '01': u'01 - Efectivo',
  '02': u'02 - Cheque nominativo',
  '03': u'03 - Transferencia electrónica de fondos',
  '04': u'04 - Tarjeta de crédito',
  '05': u'05 - Monedero electrónico',
  '06': u'06 - Dinero electrónico',
  '08': u'08 - Vales de despensa',
  '12': u'12 - Dación en pago',
  '13': u'13 - Pago por subrogación',
  '14': u'14 - Pago por consignación',
  '15': u'15 - Condonación',
  '17': u'17 - Compensación',
  '23': u'23 - Novación',
  '24': u'24 - Confusión',
  '25': u'25 - Remisión de deuda',
  '26': u'26 - Prescripción o caducidad',
  '27': u'27 - A satisfacción del acreedor',
  '28': u'28 - Tarjeta de débito',
  '29': u'29 - Tarjeta de servicios',
  '30': u'30 - Aplicación de anticipos',
  '99': u'99 - Por definir'
}

USO_CFDI = {
  'G01': u'G01 - Adquisición de mercancias',
  'G02': u'G02 - Devoluciones, descuentos o bonificaciones',
  'G03': u'G03 - Gastos en general',
  'I01': u'I01 - Construcciones',
  'I02': u'I02 - Mobilario y equipo de oficina por inversiones',
  'I03': u'I03 - Equipo de transporte',
  'I04': u'I04 - Equipo de computo y accesorios',
  'I05': u'I05 - Dados, troqueles, moldes, matrices y herramental',
  'I06': u'I06 - Comunicaciones telefónicas',
  'I07': u'I07 - Comunicaciones satelitales',
  'I08': u'I08 - Otra maquinaria y equipo',
  'D01': u'D01 - Honorarios médicos, dentales y gastos hospitalarios.',
  'D02': u'D02 - Gastos médicos por incapacidad o discapacidad',
  'D03': u'D03 - Gastos funerales.',
  'D04': u'D04 - Donativos.',
  'D05': u'D05 - Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).',
  'D06': u'D06 - Aportaciones voluntarias al SAR.',
  'D07': u'D07 - Primas por seguros de gastos médicos.',
  'D08': u'D08 - Gastos de transportación escolar obligatoria.',
  'D09': u'D09 - Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.',
  'D10': u'D10 - Pagos por servicios educativos (colegiaturas)',
  'P01': u'P01 - Por definir'
}

TIPO_CONTRATO = {
  '01': u'01 - Contrato de trabajo por tiempo indeterminado',
  '02': u'02 - Contrato de trabajo para obra determinada',
  '03': u'03 - Contrato de trabajo por tiempo determinado',
  '04': u'04 - Contrato de trabajo por temporada',
  '05': u'05 - Contrato de trabajo sujeto a prueba',
  '06': u'06 - Contrato de trabajo con capacitación inicial',
  '07': u'07 - Modalidad de contratación por pago de hora laborada',
  '08': u'08 - Modalidad de trabajo por comisión laboral',
  '09': u'09 - Modalidades de contratación donde no existe relación de trabajo',
  '10': u'10 - Jubilación, pensión, retiro.',
  '99': u'99 - Otro contrato'
}

TIPO_REGIMEN = {
  '02': u'02 - Sueldos',
  '03': u'03 - Jubilados',
  '04': u'04 - Pensionados',
  '05': u'05 - Asimilados Miembros Sociedades Cooperativas Produccion',
  '06': u'06 - Asimilados Integrantes Sociedades Asociaciones Civiles',
  '07': u'07 - Asimilados Miembros consejos',
  '08': u'08 - Asimilados comisionistas',
  '09': u'09 - Asimilados Honorarios',
  '10': u'10 - Asimilados acciones',
  '11': u'11 - Asimilados otros',
  '12': u'12 - Jubilados o Pensionados',
  '99': u'99 - Otro Regímen'
}

CATALOGO_ESTADO = {
  'AGU': u'AGU - Aguascalientes',
  'BCN': u'BCN - Baja California',
  'BCS': u'BCS - Baja California Sur',
  'CAM': u'CAM - Campeche',
  'CHP': u'CHP - Chiapas',
  'CHH': u'CHH - Chihuahua',
  'COA': u'COA - Coahuila',
  'COL': u'COL - Colima',
  'DIF': u'DIF - Ciudad de México',
  'DUR': u'DUR - Durango',
  'GUA': u'GUA - Guanajuato',
  'GRO': u'GRO - Guerrero',
  'HID': u'HID - Hidalgo',
  'JAL': u'JAL - Jalisco',
  'MEX': u'MEX - Estado de México',
  'MIC': u'MIC - Michoacán',
  'MOR': u'MOR - Morelos',
  'NAY': u'NAY - Nayarit',
  'NLE': u'NLE - Nuevo León',
  'OAX': u'OAX - Oaxaca',
  'PUE': u'PUE - Puebla',
  'QUE': u'QUE - Querétaro',
  'ROO': u'ROO - Quintana Roo',
  'SLP': u'SLP - San Luis Potosí',
  'SIN': u'SIN - Sinaloa',
  'SON': u'SON - Sonora',
  'TAB': u'TAB - Tabasco',
  'TAM': u'TAM - Tamaulipas',
  'TLA': u'TLA - Tlaxcala',
  'VER': u'VER - Veracruz',
  'YUC': u'YUC - Yucatán',
  'ZAC': u'ZAC - Zacatecas'
}

TIPO_JORNADA = {
  '01': u'01 - Diurna', 
  '02': u'02 - Nocturna', 
  '03': u'03 - Mixta', 
  '04': u'04 - Por hora', 
  '05': u'05 - Reducida', 
  '06': u'06 - Continuada', 
  '07': u'07 - Partida', 
  '08': u'08 - Por turnos', 
  '99': u'99 - Otra Jornada' 
}

CATALOGO_RIESGO = {
  '1': '1 - Clase I',
  '2': '2 - Clase II',
  '3': '3 - Clase III',
  '4': '4 - Clase IV',
  '5': '5 - Clase V',
  '99': '99 - No aplica'
}

FORMATO_FECHAS = {
  1: 'ENE',
  2: 'FEB',
  3: 'MAR',
  4: 'ABR',
  5: 'MAY',
  6: 'JUN',
  7: 'JUL',
  8: 'AGO',
  9: 'SEP',
  10: 'OCT',
  11: 'NOV',
  12: 'DIC',
}

CATALOGO_TIPOHORAS = {
  "01": "Dobles",
  "02": "Triples",
  "03": "Simples"
}
