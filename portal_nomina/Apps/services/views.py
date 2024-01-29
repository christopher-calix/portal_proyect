# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.core.files import File
from django.core.files.base import ContentFile

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .utils import proccess_data, stamp_data 
from .utils import proccess_data_zr, stamp_data_zr
from .utils import is_stamped
# from .utils import consulta_qr_sat
from Apps.nomina_app.models import Business, SatFile, Upload, PayRoll
from Apps.nomina_app.tasks import import_upload
from Apps.nomina_app.stamp import FINKOKWS

from pdb import set_trace

import tempfile
import zipfile

class payrolls_upload(APIView):

  permission_classes = (IsAuthenticated,)
  http_method_names = ['post']

  def get(self, request, format=None):
    response = {'success':True, u'message':'Importa tus comprobante de nómina'}
    return Response(response)

  def post(self, request, format=None):
    try:
      success = False
      message = u'Error no controlado'
      upload_id = None
      user = request.user
      if user.role == 'B':
        account = Business.objects.get(user=user)
        if request.data:
          if ["data", "filename", "period_end_date", "period_start_date"] == sorted(request.data.keys()):
            data = request.data['data']

            filename = request.data['filename']
            if '.zip' not in filename.lower():
              filename = '{}.zip'.format(filename)

            period_date_from = request.data['period_start_date']
            period_date_to = request.data['period_end_date']

            try:
              content_file = ContentFile(data.decode('base64'), name=filename)
              upload_obj = Upload.objects.create(
                business_id=account.id,
                user_id=user.id,
                name=content_file.name,
                file=content_file,
                period_date_from=period_date_from,
                period_date_to=period_date_to
              )
              if True or settings.ASYNC_PROCCESS:
                task_upload = import_upload.apply_async((upload_obj.id,),)
                upload_obj.task_id = task_upload.id
                upload_obj.task_status = task_upload.status
                upload_obj.save()
              else:
                import_upload(upload_obj.id)
              success, message, upload_id = True, 'Archivo subido exitosamente', upload_obj.task_id
            except Exception as e:
              message = u'Archivo ZIP invalido'
              print ('Exception in proccess ZIP ==> {}'.format(str(e)))
          else:
            message = u'Algun campo requerido no existe'
        else:
          message = u'Petición vacia'
      else:
        message = u'Usuario no autorizado para cargar nominas'
    except Exception as e:
      print ('Exception in payrolls_upload POST ==> {}'.format(str(e)))
    response = {'success':success, 'message': message, 'upload_id':upload_id}
    print (response)
    return Response(response)


class payrolls_list(APIView):
  """
    Clase encargada de regresar el listado de UUIDS timbrados
    que corresponden a una carga de ZIP
    Datos de entrada:
        * Task_id
  """

  permission_classes = (IsAuthenticated,)
  http_method_names = ['get']

  def get(self, request, format=None):

    response = {"status": "Error", "message": "Archivo zip no pudo ser procesado.", "data": None }
    try:

      if 'upload_id' in request.query_params:
        task_id = request.query_params.get('upload_id')
        upload_filter = Upload.objects.filter(task_id=task_id)

        if upload_filter.exists():
          upload_obj = upload_filter[0]

          if upload_obj.status == '0':
            response['status'] = 'Pendiente'
            response['message'] = 'Archivo zip pendiente para ser procesado.'

          elif upload_obj.status == '1':
            response['status'] = 'En proceso'
            response['message'] = 'Archivo zip en proceso.'

          elif upload_obj.status == '2':
            response['status'] = 'Finalizado'
            response['message'] = 'Archivo zip en procesado exitosamente.'
            response['data'] = upload_obj.payroll_set.filter(status__in=['S', 'C']).values(
              'uuid',
              'emission_date',
              'details__period',
              'details__business_number',
              'taxpayer_id',
              'name', 
              'rtaxpayer_id',
              'rname',
              'filename',
              'mbid'
            )

          elif upload_obj.status == '3':
            response['status'] = 'Error'
            response['message'] = upload_obj.notes

        else:
          response['message'] = 'upload_id:{} no encontrado.'.format(task_id)

      else:
        response['message'] = 'URL no tiene definido el parametro upload_id.'

    except Exception as e:
      print("Exception in payrolls_list(APIView) => {}".format(str(e)))
    print(response)
    return Response(response)


class payrolls_status_sat(APIView):
  """
    Clase encargada de consultar el estatus SAT del comprobante
    Datos de entrada:
        * UUID de la nomina
  """

  permission_classes = (IsAuthenticated,)
  http_method_names = ['get']

  def get(self, request, format=None):

    response = {"status":"No encontrado", "message": "Comprobante no encontrado"}
    try:

      if 'uuid' in request.query_params:
        uuid = request.query_params.get('uuid').upper()
        payroll_filter = PayRoll.objects.filter(uuid=uuid)

        if payroll_filter.exists():
          payroll_obj = payroll_filter[0]

          if payroll_obj.status_sat == 'V':
          

            FKWS = FINKOKWS()
            response_, client = FKWS.get_sat_status(
              payroll_obj.uuid,
              payroll_obj.taxpayer_id,
              payroll_obj.rtaxpayer_id,
              payroll_obj.total
            )

            if response_:
              if hasattr(response_, 'sat') and hasattr(response_.sat, 'Estado'):
                response['status'] = response_.sat.Estado
                response['message'] = 'Comprobante {}'.format(response_.sat.Estado)

          elif  payroll_obj.status_sat == 'C':
            response['status'] = 'Cancelado'
            response['message'] = 'Comprobante Cancelado'

        else:
          response['message'] = 'uuid:{} no encontrado.'.format(uuid)

      else:
        response['message'] = 'URL no tiene definido el parametro uuid.'

    except Exception as e:
      print("Exception in payrolls_status_sat(APIView) => {}".format(str(e)))

    return Response(response)
