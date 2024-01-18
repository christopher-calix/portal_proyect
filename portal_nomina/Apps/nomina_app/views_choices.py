INVOICE_STATUS = {
  'V': u'<button title="Vigente" class="btn btn-success btn-xs" ><strong>Vigente</strong></button>',
  'C': u'<button title="Cancelado" class="btn btn-danger btn-xs" ><strong>Cancelado</strong></button>',
}

INVOICE_SIGNED = {
  True: u'<i class="fa fa-check text-success" aria-hidden="true"></i>',
  False: u'<i class="fa fa-close text-danger" aria-hidden="true"></i>',
}

INVOICE_TYPE = {
  'I': u'<button title="Ingreso" class="btn btn-success btn-xs"><strong>Ingreso</strong></button>',
  'E': u'<button title="Egreso" class="btn btn-primary btn-xs"><strong>Egreso</strong></button>',
  'T': u'<button title="Traslado" class="btn btn-default btn-xs"><strong>Traslado</strong></button>',
  'N': u'<button title="Nomina" class="btn btn-info btn-xs"><strong>Nomina</strong></button>',
  'P': u'<button title="Pago" class="btn btn-warning btn-xs"><strong>Pago</strong></button>',
}

PROVIDER_STATUS = {
  'A': u'<span class="label label-success" title="Activo">Activo</span>',
  'S': u'<span class="label label-default" title="Suspendido">Suspendido</span>',
  'R': u'<span class="label label-danger" title="Revocado">Suspendido</span>',
  'P': u'<span class="label label-warning" title="Pendiente">Pendiente</span>', 
  '': u'Todos'
}
ROLES = {
  'A': u'Adquiriente',
  'P': u'Company',
  'S': u'SuperAdmin',
  'F': u'Finance',
  'E': u'Employee'
}

DETAILS_STATUS_HISTORY = {
  'A': u'<span class="label label-success" title="Aceptado">Aceptado</span>',
  'R': u'<span class="label label-danger" title="Rechazado">Rechazado</span>',
}

DETAILS_CAUSE_HISTORY = {
  'D': u'<span" title="">Nomina duplicada</span>', 
  'E': u'<span" title="">Nomina no corresponde a emisor</span>', 
  'T': u'<span" title="">CFDI no es nomina</span>',
  'N': u'<span" title="">CFDI no timbrado</span>',
  'I': u'<span" title="">CFDI invalido</span>',
  '': u''
}

C69_STATUS = {
  True : u'<i class="fa fa-times text-danger" aria-hidden="true" title="Con creditos pendientes ante el sat"></i>',
  False : u'<i class="fa fa-check text-success" aria-hidden="true" title="Sin creditos pendientes"></i>'
}

TYPEROLE = {
  '': u'<button class="btn btn-default btn-xs" title="Sin Grupo"><strong>Sin Tipo</strong></button>',
  'S': u'<button class="btn btn-default btn-xs" title="Staff"><strong>Staff</strong></button>', 
  'A': u'<button class="btn btn-primary btn-xs" title="Administrador"><strong>Administrador</strong></button>',
  'E': u'<button class="btn btn-info btn-xs" title="Empleado"><strong>Empleado</strong></button>',
}

TYPEUSER = {
  True : '<button title="Activo" class="btn btn-success btn-xs into" style="pointer-events: none; width: 100%; font-weight: bold;">Activo</button>',
  False : '<button title="Suspendido" class="btn btn-danger btn-xs into" style="pointer-events: none; width: 100%; font-weight: bold;">Suspendido</button>'
}

STATUS_ACCOUNT = {
  'A': u'<span class="label label-success">Activo</span>',
  'S': u'<span class="label label-default">Suspendido</span>',
  'P': u'<span class="label label-warning">Pendiente</span>',
  'R': u'<span class="label label-danger">Revocado</span>'
}