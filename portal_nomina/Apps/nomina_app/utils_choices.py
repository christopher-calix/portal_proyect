####        create pdf          ###

dom_dicc = {
  'FOR8203044R2':{
    'domicilio':'<b>RFC: FOR8203044R2<br/>Domicilio Fiscal:<br/>Calle 6 No. 2510 Zona Industrial C.P. 44940<br/>GUADALAJARA, JALISCO, MEXICO<br/>Tels: (52) 33-3268-0500 GENERAL<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0508 VENTAS<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0505<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0507 TRAFICO<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;33-3268-0501 FAX</b>'
  }
}

TIPO_COMPROBANTE = {
  'I': 'I - Ingreso',
  'E': 'E - Egreso',
  'T': 'T - Traslado',
  'N': 'N - Nómina  ',
  'P': 'P - Pago'
}

METODO_PAGO = {
  'PUE': 'PUE - Pago en una sola exhibición',
  'PIP': 'PIP - Pago inicial y parcialidades',
  'PPD': 'PPD - Pago en parcialidades o diferido'
}

IMP_DES = {
  '001': '001-ISR',
  '002': '002-IVA',
  '003': '003-IEPS'
}

REG_FIS = {
  '601': '601 - General de Ley Personas Morales',
  '603': '603 - Personas Morales con Fines no Lucrativos',
  '605': '605 - Sueldos y Salarios e Ingresos Asimilados a Salarios',
  '606': '606 - Arrendamiento',
  '608': '608 - Demás ingresos',
  '609': '609 - Consolidación',
  '610': '610 - Residentes en el Extranjero sin Establecimiento Permanente en México',
  '611': '611 - Ingresos por Dividendos (socios y accionistas)',
  '612': '612 - Personas Físicas con Actividades Empresariales y Profesionales',
  '614': '614 - Ingresos por intereses',
  '616': '616 - Sin obligaciones fiscales',
  '620': '620 - Sociedades Cooperativas de Producción que optan por diferir sus ingresos',
  '621': '621 - Incorporación Fiscal',
  '622': '622 - Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras',
  '623': '623 - Opcional para Grupos de Sociedades',
  '624': '624 - Coordinados',
  '628': '628 - Hidrocarburos',
  '607': '607 - Régimen de Enajenación o Adquisición de Bienes',
  '629': '629 - De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales',
  '630': '630 - Enajenación de acciones en bolsa de valores',
  '615': '615 - Régimen de los ingresos por obtención de premios'
}

FOR_PA = {
  '01': '01 - Efectivo',
  '02': '02 - Cheque nominativo',
  '03': '03 - Transferencia electrónica de fondos',
  '04': '04 - Tarjeta de crédito',
  '05': '05 - Monedero electrónico',
  '06': '06 - Dinero electrónico',
  '08': '08 - Vales de despensa',
  '12': '12 - Dación en pago',
  '13': '13 - Pago por subrogación',
  '14': '14 - Pago por consignación',
  '15': '15 - Condonación',
  '17': '17 - Compensación',
  '23': '23 - Novación',
  '24': '24 - Confusión',
  '25': '25 - Remisión de deuda',
  '26': '26 - Prescripción o caducidad',
  '27': '27 - A satisfacción del acreedor',
  '28': '28 - Tarjeta de débito',
  '29': '29 - Tarjeta de servicios',
  '30': '30 - Aplicación de anticipos',
  '99': '99 - Por definir'
}

USO_CFDI = {
  'G01': 'G01 - Adquisición de mercancias',
  'G02': 'G02 - Devoluciones, descuentos o bonificaciones',
  'G03': 'G03 - Gastos en general',
  'I01': 'I01 - Construcciones',
  'I02': 'I02 - Mobilario y equipo de oficina por inversiones',
  'I03': 'I03 - Equipo de transporte',
  'I04': 'I04 - Equipo de computo y accesorios',
  'I05': 'I05 - Dados, troqueles, moldes, matrices y herramental',
  'I06': 'I06 - Comunicaciones telefónicas',
  'I07': 'I07 - Comunicaciones satelitales',
  'I08': 'I08 - Otra maquinaria y equipo',
  'D01': 'D01 - Honorarios médicos, dentales y gastos hospitalarios.',
  'D02': 'D02 - Gastos médicos por incapacidad o discapacidad',
  'D03': 'D03 - Gastos funerales.',
  'D04': 'D04 - Donativos.',
  'D05': 'D05 - Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).',
  'D06': 'D06 - Aportaciones voluntarias al SAR.',
  'D07': 'D07 - Primas por seguros de gastos médicos.',
  'D08': 'D08 - Gastos de transportación escolar obligatoria.',
  'D09': 'D09 - Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.',
  'D10': 'D10 - Pagos por servicios educativos (colegiaturas)',
  'P01': 'P01 - Por definir'
}

TIPO_CONTRATO = {
  '01': '01 - Contrato de trabajo por tiempo indeterminado',
  '02': '02 - Contrato de trabajo para obra determinada',
  '03': '03 - Contrato de trabajo por tiempo determinado',
  '04': '04 - Contrato de trabajo por temporada',
  '05': '05 - Contrato de trabajo sujeto a prueba',
  '06': '06 - Contrato de trabajo con capacitación inicial',
  '07': '07 - Modalidad de contratación por pago de hora laborada',
  '08': '08 - Modalidad de trabajo por comisión laboral',
  '09': '09 - Modalidades de contratación donde no existe relación de trabajo',
  '10': '10 - Jubilación, pensión, retiro.',
  '99': '99 - Otro contrato'
}

TIPO_REGIMEN = {
  '02': '02 - Sueldos',
  '03': '03 - Jubilados',
  '04': '04 - Pensionados',
  '05': '05 - Asimilados Miembros Sociedades Cooperativas Produccion',
  '06': '06 - Asimilados Integrantes Sociedades Asociaciones Civiles',
  '07': '07 - Asimilados Miembros consejos',
  '08': '08 - Asimilados comisionistas',
  '09': '09 - Asimilados Honorarios',
  '10': '10 - Asimilados acciones',
  '11': '11 - Asimilados otros',
  '12': '12 - Jubilados o Pensionados',
  '99': '99 - Otro Regímen'
}

CATALOGO_ESTADO = {
  'AGU': 'AGU - Aguascalientes',
  'BCN': 'BCN - Baja California',
  'BCS': 'BCS - Baja California Sur',
  'CAM': 'CAM - Campeche',
  'CHP': 'CHP - Chiapas',
  'CHH': 'CHH - Chihuahua',
  'COA': 'COA - Coahuila',
  'COL': 'COL - Colima',
  'DIF': 'DIF - Ciudad de México',
  'DUR': 'DUR - Durango',
  'GUA': 'GUA - Guanajuato',
  'GRO': 'GRO - Guerrero',
  'HID': 'HID - Hidalgo',
  'JAL': 'JAL - Jalisco',
  'MEX': 'MEX - Estado de México',
  'MIC': 'MIC - Michoacán',
  'MOR': 'MOR - Morelos',
  'NAY': 'NAY - Nayarit',
  'NLE': 'NLE - Nuevo León',
  'OAX': 'OAX - Oaxaca',
  'PUE': 'PUE - Puebla',
  'QUE': 'QUE - Querétaro',
  'ROO': 'ROO - Quintana Roo',
  'SLP': 'SLP - San Luis Potosí',
  'SIN': 'SIN - Sinaloa',
  'SON': 'SON - Sonora',
  'TAB': 'TAB - Tabasco',
  'TAM': 'TAM - Tamaulipas',
  'TLA': 'TLA - Tlaxcala',
  'VER': 'VER - Veracruz',
  'YUC': 'YUC - Yucatán',
  'ZAC': 'ZAC - Zacatecas'
}

TIPO_JORNADA = {
  '01': '01 - Diurna', 
  '02': '02 - Nocturna', 
  '03': '03 - Mixta', 
  '04': '04 - Por hora', 
  '05': '05 - Reducida', 
  '06': '06 - Continuada', 
  '07': '07 - Partida', 
  '08': '08 - Por turnos', 
  '99': '99 - Otra Jornada' 
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
