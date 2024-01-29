# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import F, Count
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import reverse


from Apps.services.utils import import_payroll
from .models import (
    # Notifications,
    Upload,
    PayRoll,
    PayRollDetail,
    Business,
    Employee,
    PayrollReport
)
from .utils import CreatePDF
from .cem.parser_nom import PARSER_NOM, PARSER_NOM_V4_PAE
from .cem.utils import FinkokWS

#from portal.celery import app
from celery.utils.log import get_task_logger
from zipfile import ZipFile
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyPDF2 import PdfFileMerger
import os
import csv
import time
# import shutil
from os.path import basename
import csv
import json

logger = get_task_logger(__name__)


@app.task(queue=settings.CELERY_QUEUE_NAME)
def test(a, b):
    return a + b


@app.task(queue=settings.CELERY_QUEUE_NAME)
def import_upload(upload_id=None):
    try:
        time.sleep(5)
        upload_obj = Upload.objects.get(id=upload_id)
        upload_obj.total_txt = 0
        upload_obj.total_txt_error = 0
        upload_obj.total_txt_good = 0
        upload_obj.save()

        file = upload_obj.file
        zipfile = ZipFile(file, 'r')
        zip_namelist = zipfile.namelist()

        total_txt = 0
        total_txt_error = 0
        for file_name in zip_namelist:

            txt_path = zipfile.extract(
                file_name, settings.PATH_EXTRACT_ZIP_TMP)

            if txt_path.split('.')[-1].lower() == 'txt':

                if settings.ASYNC_PROCCESS:
                    process_txt.apply_async((txt_path, upload_id))
                else:
                    process_txt(txt_path, upload_id)

            else:
                total_txt_error += 1

            total_txt += 1

        upload_obj.refresh_from_db()
        upload_obj.total_txt = total_txt
        upload_obj.total_txt_error = F('total_txt_error') + total_txt_error
        upload_obj.status = 1
        upload_obj.save()
        print('Upload:{} process successfull'.format(upload_obj))
        print('Upload:{} total_txt => {}'.format(upload_obj, total_txt))
        print('Upload:{} total_txt_error => {}'.format(
            upload_obj, total_txt_error))
        if settings.ASYNC_PROCCESS:
            check_import_upload.apply_async((upload_id, ))
        else:
            check_import_upload(upload_id)

    except Exception as e:
        print('Exception in import_upload | upload_id:{} => {}'.format(
            upload_id, str(e)))


@app.task(queue=settings.CELERY_QUEUE_NAME)
def process_txt(txt_path, upload_id):
    try:

        # OBTENER EL OBJETO UPLOAD
        upload_obj = Upload.objects.get(id=upload_id)
        business_obj = upload_obj.business

        # PARSEAR EL TXT
        cfdi_version = '3.3'
        with open(txt_path, 'r') as file:
            reader = csv.reader(file, delimiter = '|')
            cfdi_version = next(reader)[1]
        if cfdi_version == '3.3':
            parser_nom_obj = PARSER_NOM(txt_path, business_obj.taxpayer_id)
        elif cfdi_version == '4.0':
            parser_nom_obj = PARSER_NOM_V4_PAE(txt_path, business_obj)
        else:
            raise Exception("CFDI version invalid: {}".format(cfdi_version))

        file_name = os.path.basename(txt_path)

        if parser_nom_obj.is_valid:

            print('Upload:{} File:{} parser successfull'.format(
                upload_obj, file_name))

            payroll_dict = parser_nom_obj.json
            xml_string = parser_nom_obj.cfdi
            serie = parser_nom_obj.serie
            folio = parser_nom_obj.folio
            receptor = parser_nom_obj.receptor
            payroll_obj, created = PayRoll.objects.get_or_create(
                business=business_obj,
                rtaxpayer_id=receptor,
                serial=serie,
                folio=folio
            )

            if payroll_dict['Emisor']['Rfc'] == business_obj.taxpayer_id:
                print('Upload:{} File:{} PayRoll:{} get_or_create successfull'.format(upload_obj, file_name, payroll_obj))

                if created or payroll_obj.status in ('E', 'P'):
                    payroll_obj.upload = upload_obj
                    payroll_obj.filename = file_name
                    payroll_obj.txt = open(txt_path, 'r').read()
                    payroll_obj.xml = xml_string
                    payroll_obj.version = cfdi_version
                    payroll_obj.save()

                    if not created:
                        payroll_obj.reset()
                        print('Upload:{} File:{} PayRoll:{} reset'.format(
                            upload_obj, file_name, payroll_obj))

                    # procesar json a objetos
                    success, message = import_payroll(
                        business_obj.id, payroll_dict)
                    payroll_obj.refresh_from_db()
                    if success:

                        # mandar a timbrar
                        response, client = FinkokWS.stamp(xml_string, business_obj=business_obj)

                        # CUANDO EL XML SE TIMBRA
                        if hasattr(response, 'CodEstatus') and \
                                'timbrado' in response.CodEstatus:

                            print('Upload:{} File:{} PayRoll:{} Comprobante timbrado Satisfactoriamente'.format(
                                upload_obj, file_name, payroll_obj))

                            payroll_obj.uuid = response['UUID']
                            payroll_obj.stamping_date = response['Fecha']
                            payroll_obj.status = 'S'
                            payroll_obj.notes = response['CodEstatus']
                            payroll_obj.xml = response['xml'].encode('utf8')
                            payroll_obj.get_total_per()
                            payroll_obj.get_total_ded()
                            payroll_obj.get_total_oth()
                            payroll_obj.save()
                            upload_obj.add_txt_good()
                            print('Upload:{} File:{} PayRoll:{} stamped'.format(
                                upload_obj, file_name, payroll_obj))

                        # CUANDO EL XML YA TIENE UN TIMBRE PREVIO
                        elif hasattr(response, 'CodEstatus') and 'Comprobante \
                                timbrado previamente' in response.CodEstatus:
                            print('Upload:{} File:{} PayRoll:{} previously stamped'.format(upload_obj, file_name, payroll_obj))

                        # CUANDO EL XML TIENE ERRORES EN EL TIMBRADO
                        elif hasattr(response, 'Incidencias') and \
                                response.Incidencias:
                            print (response)
                            save_error = True
                            incidencia = response['Incidencias'][0][0]

                            # PARCHE PARA TIMBRAR EL CFDI EN VERSION 3.3 CUANDO DE UNO DE LOS SIGUIENTES ERRORES DE TIMBRADO:
                            #   CFDI40147 => ERROR REFERENTE AL CODIGO POSTAL DEL EMPLEADO
                            #   CFDI40144 => ERROR REFERENTE AL NOMBRE DEL EMPLEADO
                            # if business_obj.taxpayer_id in ('BXH110304HQ7', 'BEC170802NY8', 'SIS850502E33', 'BDF900209VC0', 'NSM1101288B1', 'HAZ000225RC4', 'DTS181008KM1', 'DMM171208LT4', 'LUI180927JV0', 'ILS980323AS5', 'LMO080401895', 'LMS080401C8A', 'DPA190530898', 'LEM020204CE6', 'DME080425SLA', 'DME010320E70', 'HME790831MFA', 'TLM120613UN9', 'DME080825AX6', 'WME970822IP5', 'PPM1409023F0', 'SSS110422MBA', 'CLP130401IV3', 'NLM171219CB6', 'LFM171219GPA', 'LFM171219GPA', 'MDE171219PD8', 'TOR060515VA2', 'IIN920701G55', 'BHM2207044B9', 'TAM1112169N0', 'LUM150408S69', 'SDM0708168H3', 'GDM100309JL1', 'BUC000703MN3', 'TIN901219CP9'):
                            if business_obj.taxpayer_id in ('BDF900209VC0', 'DME080425SLA', 'GDM100309JL1', 'SDM0708168H3', 'BEC170802NY8', 'AFE170313197', 'BUC000703MN3', 'TIN901219CP9', 'NSM1101288B1', 'DMM171208LT4', 'LUI180927JV0', 'DPA190530898', 'DTS181008KM1'):
                                if incidencia['CodigoError'] in ('CFDI40147', 'CFDI40144'):
                                    new_parser_nom_obj = PARSER_NOM(txt_path, business_obj.taxpayer_id)
                                    if new_parser_nom_obj.is_valid:
                                        new_payroll_dict = new_parser_nom_obj.json
                                        print(new_payroll_dict)
                                        new_xml_string = new_parser_nom_obj.cfdi
                                        payroll_obj.reset()
                                        mew_success, mew_message = import_payroll(business_obj.id, new_payroll_dict)
                                        payroll_obj.refresh_from_db()
                                        if success:
                                            new_response, new_client = FinkokWS.stamp(new_xml_string, business_obj=business_obj)
                                            if hasattr(new_response, 'CodEstatus') and \
                                                    'timbrado' in new_response.CodEstatus:

                                                print('Upload:{} File:{} PayRoll:{} Comprobante timbrado Satisfactoriamente cambio de version de 4.0 a 3.3'.format(
                                                    upload_obj, file_name, payroll_obj))

                                                payroll_obj.uuid = new_response['UUID']
                                                payroll_obj.stamping_date = new_response['Fecha']
                                                payroll_obj.status = 'S'
                                                payroll_obj.notes = new_response['CodEstatus']
                                                payroll_obj.xml = new_response['xml'].encode('utf8')
                                                payroll_obj.get_total_per()
                                                payroll_obj.get_total_ded()
                                                payroll_obj.get_total_oth()
                                                payroll_obj.save()
                                                upload_obj.add_txt_good()
                                                print('Upload:{} File:{} PayRoll:{} stamped'.format(
                                                    upload_obj, file_name, payroll_obj))
                                                save_error = False
                                            elif hasattr(new_response, 'Incidencias') and new_response.Incidencias:
                                                new_incidencia = new_response['Incidencias'][0][0]
                                                payroll_obj.status = 'E'
                                                payroll_obj.xml = new_xml_string
                                                payroll_obj.notes = "{} => {}".format(
                                                    new_incidencia['CodigoError'],
                                                    new_incidencia['MensajeIncidencia'])
                                                payroll_obj.save()
                                                upload_obj.add_txt_error()
                                                print('Upload:{} File:{} PayRoll:{} error stamped => {}'.format(upload_obj, file_name, payroll_obj, payroll_obj.notes))
                                                save_error = False
                                        else:
                                            print('Upload:{} File:{} PayRoll:{} cambio de version de 4.0 a 3.3 error al importar a la base de datos'.format(upload_obj, file_name, payroll_obj))
                                    else:
                                        print('Upload:{} File:{} PayRoll:{} cambio de version de 4.0 a 3.3 Error al parsear'.format(upload_obj, file_name, payroll_obj))

                            if save_error:
                                payroll_obj.status = 'E'
                                payroll_obj.notes = "{} => {}".format(
                                    incidencia['CodigoError'],
                                    incidencia['MensajeIncidencia'])
                                payroll_obj.save()
                                upload_obj.add_txt_error()
                            print('Upload:{} File:{} PayRoll:{} error stamped => {}'.format(upload_obj, file_name, payroll_obj, "{} => {}".format(incidencia['CodigoError'], incidencia['MensajeIncidencia'])))

                        # ERROR NO CONTROLADO
                        else:
                            payroll_obj.status = 'E'
                            payroll_obj.save()
                            payroll_obj.notes = "Error no controlado"
                            upload_obj.add_txt_error()
                            print('Upload:{} File:{} PayRoll:{} Exception in stamp process'.format(upload_obj, file_name, payroll_obj))
                            raise Exception('Exception in stamp process')

                    else:
                        payroll_obj.status = 'E'
                        payroll_obj.save()
                        payroll_obj.notes = u"Error al importar información"
                        upload_obj.add_txt_error()
                        print('Upload:{} File:{} PayRoll:{} Exception in import_payroll'.format(upload_obj, file_name, payroll_obj))

                else:
                    # Procesado previamente
                    # Notificacion
                    # payroll_obj.status = 'E'
                    # payroll_obj.notes = 'Procesado Previamente'
                    print('Upload:{} File:{} PayRoll:{} Previously processed'.format(upload_obj, file_name, payroll_obj))
            else:
                payroll_obj.status = 'E'
                payroll_obj.notes = 'RFC emisor no corresponde con el negocio'
                payroll_obj.upload = upload_obj
                payroll_obj.save()
                print('Upload:{} File:{} PayRoll:{} RFC emisor no corresponde con el negocio'.format(upload_obj, file_name, payroll_obj))

        else:
            # Notifiacion
            # payroll_obj.status = 'E'
            # payroll_obj.notes = 'Parser Error => {}'.format(parser_nom_obj.error)
            # payroll_obj.save()
            upload_obj.add_txt_error()

            print('Upload:{} File:{} {}'.format(upload_obj, file_name, parser_nom_obj.error))

    except Exception as e:
        print('Exception in process_txt upload_id:{} txt:{} Error:{}'.format(
            upload_id, txt_path, str(e)))


@app.task(queue=settings.CELERY_QUEUE_NAME, default_retry_delay=10, max_retries=5)
def check_import_upload(upload_id):
    try:

        time.sleep(5)
        upload_obj = Upload.objects.get(id=upload_id)
        payroll_filter = PayRoll.objects.filter(upload_id=upload_id)

        # VERIFICAR EL NUMERO DE TXTS COINCIDAN CON LOS PAYROLL
        # if payroll_filter.count() < upload_obj.total_txt:
        #     raise Exception('AUN NO SE TERMINA DE PROCESAR TODOS LOS TXT')

        if payroll_filter.count() < 1:
            raise Exception('AUN NO SE TERMINA DE PROCESAR TODOS LOS TXT')

        payroll_filter_pending = payroll_filter.filter(status='P')
        # VERIFICAR QUE LOS PAYROLL NO TENGAN ESTATUS P
        if payroll_filter_pending.count():
            raise Exception('AUN HAY NOMINAS PENDIENTES')

        # RECONTAR ERRORES, TIMBRADOS
        status_result = payroll_filter.values('status')\
            .annotate(total=Count('status')).order_by()

        for status_total in status_result:
            total = status_total['total']
            if status_total['status'] == 'S':
                upload_obj.total_txt_good = total
                upload_obj.save()
            elif status_total['status'] == 'E':
                upload_obj.total_txt_error = total
                upload_obj.save()

        upload_obj.status = 2
        upload_obj.task_status = 'SUCCESS'
        upload_obj.save()

        # ENVIAR REPORTE CORRESPONDIENTE
        upload_obj.send_report_mail()

        # ENVIAR LAS NOMINAS POR CORREO
        for payroll_obj in payroll_filter.filter(status='S'):
            # if settings.ASYNC_PROCCESS:
            #     send_mail_payroll.apply_async((payroll_obj.id, ))
            # else:
            #     payroll_obj.send_mail()
            payroll_obj.send_mail()

        # ENVIAR REPORTE DE CORREOS ENVIADOS
        upload_obj.send_report_send_mail()


    except Exception as e:
        print('Exception in check_import_upload')
        print('upload_id: {}'.format(upload_id))
        print('Error: {}'.format(str(e)))
        check_import_upload.retry(args=[upload_id])


@app.task(queue=settings.CELERY_QUEUE_NAME, default_retry_delay=5, max_retries=5)
def send_mail_payroll(payroll_id):
    try:
        payroll_obj = PayRoll.objects.get(id=payroll_id)
        payroll_obj.send_mail()
    except Exception as e:
        print('Exception in send_mail_payroll')
        print('invoice_id: {}'.format(payroll_id))
        print('Error: {}'.format(str(e)))
        send_mail_payroll.retry(args=[payroll_id])


@app.task(queue=settings.CELERY_QUEUE_NAME)
def generate_report_payrolls(business_id=None, ids=None):
    try:

        if not business_id:
            raise Exception("business_id is empty")

        if not ids:
            raise Exception("query_string and upload_id are empty")

        business_obj = Business.objects.get(id=business_id)
        payroll_filter = PayRollDetail.objects.filter(id__in=ids)

        filename = 'reporte_timbrado_{}_{}.csv'.format(
            business_obj.taxpayer_id,
            datetime.now().replace(
                microsecond=0).isoformat('T').replace(':', '-')
        )

        path = '{}{}'.format(
            settings.PATH_REPORTS_TMP,
            filename
        )

        with open(path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow([u'Reporte de CFDI emitidos por pago de nómina.'])
            writer.writerow([u'Empresa: {}({})'.format(
                business_obj.name, business_obj.taxpayer_id)])
            writer.writerow([])
            writer.writerow([])
            writer.writerow([])
            writer.writerow(settings.HEADERS_REPORT_STAMPING)
            writer.writerow(settings.SUBHEADERS_REPORT_STAMPING)
            for payroll_obj in payroll_filter:
                writer.writerow(payroll_obj.get_info_to_report())

        # Cargar a dropbox
        # success, url = upload_file_to_dropbox(path)
        # Enviar por correo
        html_content = render_to_string(
            'uploads/template_report.html',
            {"business": business_obj, "is_business": True}
        )

        subject = u'Reporte de nómima {}({})'.format(
            business_obj.name, business_obj.taxpayer_id)

        msg = EmailMessage(
            subject,
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            business_obj.email
        )
        msg.content_subtype = "html"
        msg.attach_file(path)
        msg.send()
        print('Correo Enviado satisfactoriamente')

    except Exception as e:
        print('Exception in generate_report_payrolls')
        print('Error: {}'.format(str(e)))
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


@app.task(queue=settings.CELERY_QUEUE_NAME)
def generate_report_payrolls_employee(employe_id=None, ids=None):
    try:

        if not employe_id:
            raise Exception("employe_id is empty")

        if not ids:
            raise Exception("query_string and upload_id are empty")

        business_obj = Employee.objects.get(id=employe_id)
        payroll_filter = PayRollDetail.objects.filter(id__in=ids)

        filename = 'reporte_timbrado_{}_{}.csv'.format(
            business_obj.taxpayer_id,
            datetime.now().replace(
                microsecond=0).isoformat('T').replace(':', '-')
        )

        path = '{}{}'.format(
            settings.PATH_REPORTS_TMP,
            filename
        )

        with open(path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow([u'Reporte de CFDI emitidos por pago de nómina.'])
            writer.writerow([u'Empleado: {}({})'.format(
                business_obj.name, business_obj.taxpayer_id)])
            writer.writerow([])
            writer.writerow([])
            writer.writerow([])
            writer.writerow(settings.HEADERS_REPORT_STAMPING)
            writer.writerow(settings.SUBHEADERS_REPORT_STAMPING)
            for payroll_obj in payroll_filter:
                writer.writerow(payroll_obj.get_info_to_report())

        # Cargar a dropbox
        # success, url = upload_file_to_dropbox(path)
        # Enviar por correo
        html_content = render_to_string(
            'uploads/template_report.html',
            {"business": business_obj, "is_business": False}
        )

        subject = u'Reporte de nómima {}({})'.format(
            business_obj.name, business_obj.taxpayer_id)

        msg = EmailMessage(
            subject,
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            business_obj.email
        )
        msg.content_subtype = "html"
        msg.attach_file(path)
        msg.send()
        print('Correo Enviado satisfactoriamente')

    except Exception as e:
        print('Exception in generate_report_payrolls')
        print('Error: {}'.format(str(e)))


@app.task(queue=settings.CELERY_QUEUE_NAME)
def create_zip_invoices(payroll_report_id=None, account_id=None, invoices_ids=None, role=None, split_path=False):
    """
        Funcion encargada de creae un zip de xmls:
            Entrada:
                account_id =>
                invoices_ids =>
                role =>
    """

    payroll_report_obj = None
    try:

        # validar payroll_report_id
        if not payroll_report_id:
            raise Exception(u"payroll_report_id no tiene información")

        payroll_report_obj = PayrollReport.objects.get(id=payroll_report_id)
        payroll_report_obj.status = 'I'
        payroll_report_obj.save()
        print("Se obtuvo el objeto PayrollReport")
        print(payroll_report_obj)

        # validar account_id
        if not account_id:
            raise Exception(u"account_id no tiene información")

        # validar role
        if role in ('A', 'S', 'B'):
            account_filter = Business.objects.filter(id=account_id)
            is_business = True
        elif role == "E":
            account_filter = Employee.objects.filter(id=account_id)
            is_business = False
        else:
            raise Exception("role esta vacio o es diferente de A, S, B o E")

        # Obtener el objeto business/employee
        if not account_filter.exists():
            raise Exception("El business/employee no existe")
        account_obj = account_filter[0]
        print("Se obtuvo el objeto Business/Employee")
        print(account_obj)

        # validar invoices_ids
        if not invoices_ids:
            raise Exception("invoices_ids esta vacio")
        print("IDS")
        print(invoices_ids)

        # Crear una carpta de destino
        # filename = '{}'.format(account_obj.name.strip().replace(' ', '_'))

        destination_path = '{}{}'.format(
            settings.PATH_REPORTS_TMP,
            account_obj.taxpayer_id.strip(),
        )
        print("Ruta Destino")
        print(destination_path)

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        path_zip = '{}/Nominas_{}_{}.zip'.format(
            destination_path,
            account_obj.taxpayer_id,
            datetime.now().replace(microsecond=0).isoformat()
        )
        print("Ruta del archivo ZIP")
        print(path_zip)

        # Crear el zip
        with ZipFile(path_zip, 'w') as zip_obj:

            # Iterar los invoices para copiar el XML
            payroll_filter = PayRoll.objects.filter(id__in=invoices_ids)
            if payroll_report_obj.xml and payroll_report_obj.pdf:
                for payroll_obj in payroll_filter:
                    try:
                        if split_path:
                            zip_obj.write(payroll_obj._xml.path, payroll_obj.get_path_xml_employee())
                        else:
                            zip_obj.write(payroll_obj._xml.path, basename(payroll_obj._xml.path))
                        business_number = payroll_obj.details.first().business_number
                        result_pdf = CreatePDF(
                            xml_path=payroll_obj._xml.path,
                            filename=payroll_obj.filename,
                            business_number=business_number,
                        )
                        if result_pdf.success:
                            if split_path:
                                zip_obj.write(result_pdf.path_pdf_, payroll_obj.get_path_xml_employee().replace('.xml', '.pdf'))
                            else:
                                zip_obj.write(result_pdf.path_pdf_, basename(result_pdf.path_pdf_))
                    except Exception as e:
                        print("Exception in add xml/pdf to zip => {} => {}".format(payroll_obj.id, str(e)))

            elif payroll_report_obj.xml:
                for payroll_obj in payroll_filter:
                    try:
                        if split_path:
                            zip_obj.write(payroll_obj._xml.path, payroll_obj.get_path_xml_employee())
                        else:
                            zip_obj.write(payroll_obj._xml.path)
                    except Exception as e:
                        print("Exception in add xml to zip => {} => {}".format(payroll_obj.id, str(e)))

            elif payroll_report_obj.pdf:
                for payroll_obj in payroll_filter:
                    business_number = payroll_obj.details.first().business_number
                    try:
                        result_pdf = CreatePDF(
                            xml_path=payroll_obj._xml.path,
                            filename=payroll_obj.filename,
                            business_number=business_number,
                        )
                        if result_pdf.success:
                            if split_path:
                                zip_obj.write(result_pdf.path_pdf_, payroll_obj.get_path_xml_employee().replace('.xml', '.pdf'))
                            else:
                                zip_obj.write(result_pdf.path_pdf_)
                    except Exception as e:
                        print("Exception in add xml to zip => {} => {}".format(payroll_obj.id, str(e)))

        print("Se genero el ZIP")
        # Gener enlace de descarga

        from django.core.files.base import ContentFile
        content_file = ContentFile(open(path_zip, 'rb').read(), name='algo')

        payroll_report_obj.status = 'C'
        payroll_report_obj.file = content_file
        payroll_report_obj.save()
        print("Se actualizo el objeto PayrollReport")

        # Eliminar el zip temporal
        os.remove(path_zip)
        print("Se elimino zip temporal")

        # Enviar por correo
        html_content = render_to_string(
            'uploads/template_report_payrolls.html',
            {
                "business": account_obj,
                "is_business": is_business,
                "url": '%s/dashboard/file/zip/%s' %(settings.DOMAIN, payroll_report_obj.get_encrypted_id()),
                "password": payroll_report_obj.get_decrypted_password(),
            }
        )

        subject = u'Cfdis de nómima {}({})'.format(
            account_obj.name, account_obj.taxpayer_id)

        msg = EmailMessage(
            subject,
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            account_obj.email
        )
        msg.content_subtype = "html"
        # msg.attach_file(payroll_report_obj.file.path)
        msg.send()
        print('Correo Enviado satisfactoriamente')

    except Exception as e:
        print("Exception in create_zip_invoices => {}".format(str(e)))
        print("account_id:{}".format(account_id))
        print("invoices_ids:{}".format(invoices_ids))
        print("role:{}".format(role))
        if payroll_report_obj is not None:
            payroll_report_obj.status = 'F'
            payroll_report_obj.notes = str(e)
            payroll_report_obj.save()


@app.task(queue=settings.CELERY_QUEUE_NAME, default_retry_delay=3)
def create_zip_invoices_pdf(payroll_report_id=None):
    """
        Funcion encargada de crear un solo archivo PDF con varias nominas:
            Entrada:
                payroll_report_id =>
    """

    payroll_report_obj = None
    try:
        # validar payroll_report_id
        if not payroll_report_id:
            raise Exception(u"payroll_report_id no tiene información")

        payroll_report_obj = PayrollReport.objects.get(id=payroll_report_id)
        payroll_report_obj.status = 'I'
        payroll_report_obj.save()
        print("Se obtuvo el objeto PayrollReport")
        print(payroll_report_obj)

        # validar y obtener el objeto business
        if not payroll_report_obj.business:
            raise Exception(u"business_id no tiene información")
        business_obj = payroll_report_obj.business
        print("Se obtuvo el objeto Business")
        print(business_obj)

        # validar invoices_ids
        if not payroll_report_obj.invoices_ids:
            raise Exception("invoices_ids esta vacio")
        print("IDS")
        print(payroll_report_obj.invoices_ids)

        # Crear una carpta de destino
        destination_path = '{}PDFS/{}_{}'.format(
            settings.PATH_REPORTS_TMP,
            business_obj.taxpayer_id.strip(),
            datetime.now().replace(microsecond=0).isoformat(),
        )
        print("Ruta Destino de lo PDFS")
        print(destination_path)

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # CREAR TODOS LOS PDFS
        payroll_filter = PayRoll.objects.filter(id__in=payroll_report_obj.invoices_ids)
        pdfs_list = []
        for payroll_obj in payroll_filter:
            try:
                business_number = payroll_obj.details.first().business_number
                result_pdf = CreatePDF(
                    xml_path=payroll_obj._xml.path,
                    filename=payroll_obj.filename,
                    business_number=business_number,
                )
                if result_pdf.success:
                    pdfs_list.append(result_pdf.path_pdf_)
            except Exception as e:
                print("Exception in create pdf => {} => {}".format(payroll_obj.id, str(e)))

        destination_pdf_path = '{}PDFS/{}.pdf'.format(
            settings.PATH_REPORTS_TMP,
            business_obj.taxpayer_id.strip(),
        )
        print("Ruta Destino del PDF final")
        print(destination_pdf_path)

        # Crear un solo PDF
        merger = PdfFileMerger()
        for pdf in pdfs_list:
           merger.append(pdf)
        merger.write(destination_pdf_path)
        merger.close()
        print("Se genero el PDF")

        path_zip = destination_pdf_path.replace('pdf', 'zip')
        print("Ruta del archivo ZIP")
        print(path_zip)
        with ZipFile(path_zip, 'w') as zip_obj:
            zip_obj.write(destination_pdf_path, basename(destination_pdf_path))

        # Gener enlace de descarga
        from django.core.files.base import ContentFile
        content_file = ContentFile(open(path_zip, 'rb').read(), name='algo')
        payroll_report_obj.status = 'C'
        payroll_report_obj.file = content_file
        payroll_report_obj.save()
        print("Se actualizo el objeto PayrollReport")

        # Enviar por correo
        html_content = render_to_string(
            'uploads/template_report_payrolls_pdf.html',
            {
                "business": business_obj,
                "is_business": True,
                "url": '%s/dashboard/file/zip/%s' %(settings.DOMAIN, payroll_report_obj.get_encrypted_id()),
                "password": payroll_report_obj.get_decrypted_password(),
            }
        )

        subject = u'Cfdis de nómima {}({})'.format(
            business_obj.name, business_obj.taxpayer_id)

        msg = EmailMessage(
            subject,
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            business_obj.email
        )
        msg.content_subtype = "html"
        # msg.attach_file(payroll_report_obj.file.path)
        msg.send()
        print('Correo Enviado satisfactoriamente')

        # Eliminar los archivos generados
        os.remove(destination_pdf_path)
        print("Se elimino PDF temporal")

        os.remove(path_zip)
        print("Se elimino ZIP temporal")

        for pdfs_path in pdfs_list:
            os.remove(pdfs_path)

    except Exception as e:
        print("Exception in create_zip_invoices_pdf => {}".format(str(e)))
        if payroll_report_obj is not None:
            payroll_report_obj.status = 'F'
            payroll_report_obj.notes = str(e)
            payroll_report_obj.save()


from suds.client import Client as suds_client
url = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?WSDL"
client = suds_client(url, location=url, cache=None)


@app.task(queue=settings.CELERY_QUEUE_NAME)
def consulta_sat(invoice_id):
    invoice = PayRoll.objects.get(id=invoice_id)
    result = client.service.Consulta(invoice.get_satquery_str())
    if result.Estado == "Cancelado":
        invoice.status_sat = "C"
        invoice.status = "C"
        invoice.save()
        print ("UUID:{} Cancelado".format(invoice.uuid))

    if result.Estado == "Vigente":
        invoice.status_sat = "V"
        invoice.status = "S"
        invoice.save()
        print ("UUID:{} Vigente".format(invoice.uuid))
