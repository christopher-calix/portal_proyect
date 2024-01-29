from __future__ import absolute_import


from django.db.models import Count

from django.template.context_processors import csrf

from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse


from datetime import datetime
from .models import Business, Employee, Notifications  # Account

from django.http import Http404
import time 

from datetime import datetime



INVOICE_STATUS = {
  'N': 'En proceso de validacion', 
  'R': 'Rechazado',
  'V': 'Válido', 
  'E': 'Pendiente de pago', 
  'F': 'Pagado',
  'C': 'Comprobante Cancelado',
  'A': 'Todos'
}


def get_query(function):
    """
    Decorator to construct a query for filtering invoices based on POST parameters.
    """
    @get_default_account
    def wrap(request, *args, **kwargs):
        template = 'invoices/status.html'
        if request.method == 'POST' and request.is_ajax():
            try:
                account = kwargs['account']
                active_taxpayer_id = kwargs['active_taxpayer_id']
                query = Q()  # Use Q objects for efficient query construction

                # Build query based on user role and request parameters
                if request.user.role in ('A', 'S', 'B'):
                    query = query & Q(business_id=account.id)  # Use '&' for chaining Q objects
                elif request.user.role == 'E':
                    query = query & Q(employee_id=account.id)

                # Add filters based on POST parameters
                filter_fields = (
                    'filter_filename', 'filter_folio', 'filter_serie',
                    'nomina_type', 'estado_sat', 'signed_payroll',
                    'uuid_value', 'get_uuid', 'taxpayer_value', 'name_value',
                    'business_id_value', 'taxpayer_value_e',
                    'date_from', 'date_to', 'date_from_paid', 'date_to_paid'
                )
                for field in filter_fields:
                    if field in request.POST:
                        value = request.POST.get(field)
                        if field in ('date_from', 'date_to', 'date_from_paid', 'date_to_paid'):
                            value = datetime.strptime(value, '%d %B %Y').strftime('%Y-%m-%d')  # Format dates
                        query = query & Q(**{field: value})  # Use kwargs for dynamic filtering

                # Uncomment this block if a default date range is needed:
                # if not query.filter:  # If no filters are applied
                #     date_to = datetime.now()
                #     date_from = datetime(date_to.year, date_to.month, 1)
                #     query = query & Q(emission_date__range=[date_from, date_to])

                print(query)  # For debugging
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print("Exception in decorator wrap ==> {}".format(str(e)))

        parameters = {}
        # parameters = get_counter_invoices(request.user.account)  # Uncomment if needed
        return TemplateResponse(request, template, context=parameters)

    return wrap

def get_query_history(function):
    def wrap(request, *args, **kwargs):
        template = 'history/history.html'
        if request.method == 'POST' and request.is_ajax():
            try:
                query = Q()  # Use Q objects for efficient query construction

                # Add filters based on POST parameters
                filter_fields = ('user', 'taxpayer_value_e', 'date_from', 'date_to')
                for field in filter_fields:
                    if field in request.POST:
                        value = request.POST.get(field)
                        if field in ('date_from', 'date_to'):
                            value = datetime.strptime(value, '%d %B %Y').strftime('%Y-%m-%d')  # Format dates
                        query = query & Q(**{field: value})  # Use kwargs for dynamic filtering

                # Uncomment this block if a default query for role 'P' is needed:
                # if request.user.role == 'P':
                #     account = Account.objects.get(user=request.user)
                #     taxpayer = account.taxpayer_id
                #     query = query & Q(account__taxpayer_id=taxpayer)

                print(query)  # For debugging
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print("ERROR")
                print(str(e))

        parameters = {}
        # parameters = get_counter_invoices(request.user.account)  # Uncomment if needed
        return TemplateResponse(request, template, context=parameters)

    return wrap



def get_counter_invoices(account):
    invoice_counts = Invoice.objects.filter(provider=account).values(
        'status'
    ).annotate(
        count=Count('id')
    ).order_by()

    parameters = {
        'n': invoice_counts.get(status='N', count=0) or 0,  # En procesos de validacion
        'e': invoice_counts.get(status='E', count=0) or 0,  # Con Fecha de Pago
        'v': invoice_counts.get(status='V', count=0) or 0,  # Sin Fecha de Pago
        'p': invoice_counts.get(status='P', count=0) or 0,  # Pagados sin confirmar
        'd': invoice_counts.get(status='D', count=0) or 0,  # Fecha de pago vencida
        'f': invoice_counts.get(status='F', count=0) or 0,  # finalizado pagados
        'c': invoice_counts.get(status='C', count=0) or 0,  # cancelado
        'r': invoice_counts.get(status='R', count=0) or 0,  # rechazados
        'total': invoice_counts.aggregate(total=Count('id'))['total'],
        'notifications': Notifications.objects.filter(account=account, status='N').order_by('date'),
    }
    return parameters


def validate_role(method):
    def role(request, *args, **kwargs):
        user = request.user
        role = 'provider' if user.role == 'P' else 'admin'
        template = f'{role}/dashboard.html'
        parameters = {}

        if role == 'provider':
            parameters = get_counter_invoices(request.user.account)

        return TemplateResponse(request, template, parameters)

    return role



def get_query_providers(function):
    def wrap(request, *args, **kwargs):
        template = 'providers/status.html'
        if request.method == 'POST':
            try:
                account = Account.objects.get(user=request.user)        ##          Esta funcion debe retornar los valores almacenados desde el Account, via del Modelo de Bussines?
                query = Q()
                filter_fields = ('taxpayer_id', 'provider_mail', 'provider_name', 'provider_status')
                for field in filter_fields:
                    if field in request.POST:
                        value = request.POST.get(field)
                        if field == 'provider_status' and value:
                            value = value.upper()  # Convert status to uppercase
                        query = query & Q(**{f'provider__{field}': value})  # Use kwargs for dynamic filtering
                # Uncomment this line if needed:
                # query = query & (Q(provider=account) | Q(account=account))
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print("Exception in get_query_providers")
                print(str(e))

        parameters = {'status': INVOICE_STATUS}  # Assuming INVOICE_STATUS is defined
        # Uncomment this line if needed:
        # parameters.update(get_counter_invoices(request.user.account))
        return TemplateResponse(request, template, context=parameters)

    return wrap

def get_query_business(function):
    def wrap(request, *args, **kwargs):
        template = 'admin/business.html'
        if request.method == 'POST':
            try:
                active_account = request.session.get('active_taxpayer_id')
                query = Q()
                if request.user.role in ('S',):
                    query = query & Q(user=request.user)
                elif request.user.role == 'A' and not request.user.is_superuser:
                    query = query & Q(type=request.user.type_business)
                filter_fields = ('taxpayer_id', 'provider_mail', 'provider_name', 'provider_status')
                for field in filter_fields:
                    if field in request.POST:
                        value = request.POST.get(field)
                        query = query & Q(**{field: value})  # Use kwargs for dynamic filtering
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print("Exception in get_query_business")
                print(str(e))

        parameters = {}
        # Uncomment this line if needed:
        # parameters.update(get_counter_invoices(request.user.account))
        return TemplateResponse(request, template, context=parameters)

    return wrap


def get_query_employee(function):
    def wrap(request, *args, **kwargs):
        template = 'admin/employee.html'
        if request.method == 'POST':
            try:
                active_account = request.session.get('active_taxpayer_id')
                query = Q(businesses__taxpayer_id=active_account)  # Start with base query

                # Add filters based on POST parameters
                filter_fields = (
                    'taxpayer_id', 'curp', 'email', 'name', 'status',
                    'department', 'puesto', 'company'
                )
                for field in filter_fields:
                    if field in request.POST:
                        value = request.POST.get(field)
                        query = query & Q(**{field: value})  # Use kwargs for dynamic filtering

                print(query)  # For debugging
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print("Exception in get_query_employee")
                print(str(e))

        parameters = {}
        return TemplateResponse(request, template, context=parameters)

    return wrap

def get_query_users(function):
    def wrap(request, *args, **kwargs):
        template = 'admin/users.html'
        if request.method == 'POST' and request.is_ajax():
            try:
                query = Q(role__in=('S', 'A'), is_superuser=False)  # Start with base query

                # Add filters based on POST parameters
                filter_fields = ('taxpayer_id', 'email', 'name', 'status', 'role')
                for field in filter_fields:
                    if field in request.POST:
                        value = request.POST.get(field)
                        if field == 'status':
                            active = True if value == 'A' else False
                            value = Q(is_active=active)
                        elif field == 'role':
                            value = Q(role=value)
                        else:
                            value = Q(**{field + '__icontains': value})  # Use icontains for case-insensitive matching
                        query = query & value

                print(query)  # For debugging
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print("Exception in get_query_users")
                print(str(e))

        parameters = {}
        return TemplateResponse(request, template, context=parameters)

    return wrap



def is_admin(user):
    return user.role in ('F', 'A')

def is_superuser(user):
    return user.role == 'S'  # Use '==' for equality comparison

def get_default_account(function):
    def wrap(request, *args, **kwargs):
        try:
            account = None
            role = None
            taxpayer_id = None

            if not request.user.is_anonymous:  # Use 'is_anonymous' to check for anonymous users
                role = request.user.role
                taxpayer_id = request.session.get('active_account')  # No need for 'None' as default
                if taxpayer_id:
                    if role in ('A', 'B', 'S'):
                        account = Business.objects.get(taxpayer_id=taxpayer_id)
                    elif role == 'E':
                        account = Employee.objects.get(user=request.user, taxpayer_id=taxpayer_id)

            kwargs['account'] = account
            kwargs['active_taxpayer_id'] = taxpayer_id
            kwargs['role'] = role
        except Exception as e:  # Use 'as' for exception handling
            print(f'Exception in get_default_account: {e}')
        return function(request, *args, **kwargs)
    return wrap

def get_query_uploads(function):
    def wrap(request, *args, **kwargs):
        template = 'uploads/uploads.html'
        if request.method == 'POST':
            try:
                query = Q()
                for field in ('filter_id', 'filter_name', 'filter_estado'):
                    if field in request.POST:
                        value = request.POST.get(field)
                        if value:  # Check if value is not empty
                            query = query & Q(**{field: value})  # Use kwargs for dynamic filtering
                if 'date_from' in request.POST and 'date_to' in request.POST:
                    date_from = request.POST.get('date_from')
                    date_to = request.POST.get('date_to')
                    if date_from and date_to:
                        date_from = datetime.strptime(date_from, '%d %B %Y').strftime('%Y-%m-%d')
                        date_to = datetime.strptime(date_to, '%d %B %Y').strftime('%Y-%m-%d')
                        query = query & Q(created__range=[date_from, date_to])
                return function(request, query, *args, **kwargs)
            except Exception as e:
                print(f"Exception in get_query_uploads: {e}")
        parameters = {}
        return TemplateResponse(request, template, context=parameters)
    return wrap

def get_query_zip(function):
    # This function is almost identical to get_query_uploads, consider combining them
    def wrap(request, *args, **kwargs):
        template = 'zips/zips.html'
        template = 'zips/zips.html'
        if request.method == 'POST':
          try:
            query = Q()
            if 'filter_id' in request.POST:
              query = query.__and__(Q(id=request.POST.get('filter_id')))
            if 'filter_id_carga' in request.POST:
              query = query.__and__(Q(upload_id=request.POST.get('filter_id_carga')))
            if 'filter_name' in request.POST:
              query = query.__and__(Q(name__icontains=request.POST.get('filter_name')))
            if 'filter_estado' in request.POST and request.POST.get('filter_estado') != '':
              query = query.__and__(Q(task_status=request.POST.get('filter_estado')))
            if 'date_from' in request.POST and 'date_to' in request.POST:
              date_from = request.POST.get('date_from')
              date_from = datetime.strptime(date_from, '%d %B %Y').strftime('%Y-%m-%d') if date_from else None
              date_to = request.POST.get('date_to')
              date_to = datetime.strptime(date_to, '%d %B %Y').strftime('%Y-%m-%d') if date_to else None
              if date_to and date_from:
                query = query.__and__(Q(date_created__range=[date_from, date_to]))
            return function(request, query, *args, **kwargs)
          except Exception as e:
            print ("Exception in get_query_uploads")
            print (str(e))
        parameters = {}
        return TemplateResponse(request, template, context=parameters)
    return wrap
