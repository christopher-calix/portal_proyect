INVOICE_STATUS = {
  'V': '<button title="Vigente" class="btn btn-success btn-xs" ><strong>Vigente</strong></button>',
  'C': '<button title="Cancelado" class="btn btn-danger btn-xs" ><strong>Cancelado</strong></button>',
}

INVOICE_SIGNED = {
  True: '<i class="fa fa-check text-success" aria-hidden="true"></i>',
  False:'<i class="fa fa-close text-danger" aria-hidden="true"></i>',
}

INVOICE_TYPE = {
  'I': '<button title="Ingreso" class="btn btn-success btn-xs"><strong>Ingreso</strong></button>',
  'E': '<button title="Egreso" class="btn btn-primary btn-xs"><strong>Egreso</strong></button>',
  'T': '<button title="Traslado" class="btn btn-default btn-xs"><strong>Traslado</strong></button>',
  'N': '<button title="Nomina" class="btn btn-info btn-xs"><strong>Nomina</strong></button>',
  'P': '<button title="Pago" class="btn btn-warning btn-xs"><strong>Pago</strong></button>',
}

PROVIDER_STATUS = {
  'A': '<span class="label label-success" title="Activo">Activo</span>',
  'S': '<span class="label label-default" title="Suspendido">Suspendido</span>',
  'R': '<span class="label label-danger" title="Revocado">Suspendido</span>',
  'P': '<span class="label label-warning" title="Pendiente">Pendiente</span>', 
  '': 'Todos'
}
ROLES = {
  'A': 'Adquiriente',
  'P': 'Company',
  'S': 'SuperAdmin',
  'F': 'Finance',
  'E': 'Employee'
}

DETAILS_STATUS_HISTORY = {
  'A': '<span class="label label-success" title="Aceptado">Aceptado</span>',
  'R': '<span class="label label-danger" title="Rechazado">Rechazado</span>',
}

DETAILS_CAUSE_HISTORY = {
  'D': '<span" title="">Nomina duplicada</span>', 
  'E': '<span" title="">Nomina no corresponde a emisor</span>', 
  'T': '<span" title="">CFDI no es nomina</span>',
  'N': '<span" title="">CFDI no timbrado</span>',
  'I': '<span" title="">CFDI invalido</span>',
  '': ''
}

C69_STATUS = {
  True : '<i class="fa fa-times text-danger" aria-hidden="true" title="Con creditos pendientes ante el sat"></i>',
  False : '<i class="fa fa-check text-success" aria-hidden="true" title="Sin creditos pendientes"></i>'
}

TYPEROLE = {
  '': '<button class="btn btn-default btn-xs" title="Sin Grupo"><strong>Sin Tipo</strong></button>',
  'S': '<button class="btn btn-default btn-xs" title="Staff"><strong>Staff</strong></button>', 
  'A': '<button class="btn btn-primary btn-xs" title="Administrador"><strong>Administrador</strong></button>',
  'E': '<button class="btn btn-info btn-xs" title="Empleado"><strong>Empleado</strong></button>',
}

TYPEUSER = {
  True : '<button title="Activo" class="btn btn-success btn-xs into" style="pointer-events: none; width: 100%; font-weight: bold;">Activo</button>',
  False : '<button title="Suspendido" class="btn btn-danger btn-xs into" style="pointer-events: none; width: 100%; font-weight: bold;">Suspendido</button>'
}

STATUS_ACCOUNT = {
  'A': '<span class="label label-success">Activo</span>',
  'S': '<span class="label label-default">Suspendido</span>',
  'P': '<span class="label label-warning">Pendiente</span>',
  'R': '<span class="label label-danger">Revocado</span>'
}