from __future__ import absolute_import

from .choices import INVOICE_STATUS




from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse


from datetime import datetime
from .models import Business, Employee, Notifications

from django.http import Http404
import time 



from datetime import datetime

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