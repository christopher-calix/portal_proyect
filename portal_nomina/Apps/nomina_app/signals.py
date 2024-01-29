from django.apps import apps
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

STATUS_DICC = {
  'V':'Tu comprobante fiscal digital por internet (CFDI) es completamente valido.',
  'N':'Tu comprobante fiscal es válido, pero seguimos buscandolo en el SAT, te avisaremos cuando la busqueda se haya completado.',
  'E':'Su conprobante se le ha asignado una fecha de pago',
  'P':'Se ha subido un comprobante de pago',
  'F':'La factura ha sido pagada',
  'R':'La factura ha sido rechazada',
  'C':'La factura ha sido cancelada, verifique con la persona o entidad que emitio la factura',
  }
INVOICE_STATUS = {
  'N': 'En proceso de validacion', 
  'R': 'Rechazado',
  'V': 'Válido', 
  'P': 'Por confirmar pago', 
  'E': 'Pendiente de pago', 
  'F': 'Pagado',
  'C': 'Comprobante Cancelado',
  #'A': u'Todos'
}



def notify(instance, created, **kwargs):
  try:
    mail_list = []
    DOMAIN = 'http://localhost:8000'

    user = instance.account.user
    name = ''
    extra_mail = False

    if instance.status in ['F', 'C']:
      name = instance.account.first_name
    elif instance.status in ['E', 'P', 'N']:
      user = instance.provider.user
      name = instance.provider.first_name
    else:
      extra_mail = True
      mail_list.append(instance.account.user.email)

    Notification = apps.get_model('core', 'Notifications')
    title = settings.NOTIFICATIONS['title'][instance.status] % str(instance.uuid).upper()
    message = settings.NOTIFICATIONS['message'][instance.status]

    if created:
      notification = Notification.objects.create(
          invoice=instance,
          account=instance.account,
          title=title,
          message=message,
          status='N'
      )
    else:
      notification = Notification.objects.get(invoice=instance)
      notification.status = 'O'
      notification.save()

    try:
      description = instance.account_notes + instance.provider_notes  # Concatenación de cadenas

      message_render = {'html_message': render_to_string('notification/notification_new.html', {
          'title': title,
          'name': name,
          'message': message,
          'status': INVOICE_STATUS[instance.status],
          'description': description,
          'uuid': str(instance.uuid).upper(),
          'url_base': DOMAIN,
          'url_invoice': reverse('list_invoices', args=[str(instance.uuid)])
      })}

      user.email_user(subject=title, message=message, mail_list=mail_list, **message_render)
    except Exception as e:
      print(str(e))

  except Exception as e:
    print(str(e))
