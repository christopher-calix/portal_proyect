from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
import datetime
from .choices import *
##########################
from __future__ import unicode_literals

from django.conf import settings
from django.db import models  # Use 'models' instead of 'connection'
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import F, Sum
from django.dispatch import receiver  # Use 'receiver' directly
from django.core import signing
from .storage import satfile_storage, logo_storage, signed_storage, zip_storage, txt_storage, report_cfdis_storga
from .cem.utils import FinkokWS

# Additional imports
from django.contrib.postgres.fields import JSONField, ArrayField  # No changes needed
from django.db.models.signals import post_save  # No changes needed
from datetime import datetime, timedelta  # No changes needed
import random  # No changes needed
import string  # No changes needed
import pyminizip  # No changes needed
import os  # No changes needed
import csv  # No changes needed

# Create your models here.

class OverrideFileSystemStorage(FileSystemStorage):

    def __init__(self, location=settings.INVOICE_STORAGE, *args, **kwargs):
        self._location = location
        super(OverrideFileSystemStorage, self).__init__(location, *args, **kwargs)

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self._location, name))
        else:
            name = super(OverrideFileSystemStorage, self).get_available_name(name, max_length)
        return name

class OverrideFileSystemStorageImg(FileSystemStorage):

    def __init__(self, location=settings.MEDIA_ROOT, *args, **kwargs):
        self._location = location
        super(OverrideFileSystemStorageImg, self).__init__(location, *args, **kwargs)

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self._location, name))
        else:
            name = super(OverrideFileSystemStorageImg, self).get_available_name(name, max_length)
        return name




class Account(models.Model):
    taxpayer_id = models.CharField(db_index=True, max_length=14, null=True, unique=True)
    name = models.CharField(db_index=True, max_length=256, null=True)
    email = ArrayField(models.EmailField(u'Correo electrónico', max_length=254, null=True), null=True, default=list)
    address = models.ForeignKey('Address', null=True)
    status = models.CharField(max_length=1, choices=STATUS_ACCOUNT, default='P')
    default = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} - {}'.format(self.taxpayer_id, self.name)


class Business(Account):
    user = models.ManyToManyField('users.User')
    finkok_account = models.ForeignKey('FKAccount', on_delete=models.CASCADE, null=True)
    logo = models.FileField('Logo', storage=OverrideFileSystemStorageImg(), upload_to=logo_storage, null=True, max_length=200, blank=True)
    payroll_filename = ArrayField(models.CharField(max_length=10, null=True), null=True, default=list)
    send_mail_encryption = models.BooleanField(default=False)
    password = models.CharField(max_length=30, null=True)
    type = models.CharField(choices=TYPE_BUSINESS, max_length=1, default='S')
    sat_name = models.CharField(max_length=256, null=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.taxpayer_id)


    def get_logo(self):
        if self.logo:
            return self.logo.url
        return '/static/img/sin-logo.jpg'

    def get_fk_account(self):
        return self.finkok_account.username, self.finkok_account.password



class FKAccount(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    pricing = models.FloatField()
    status = models.CharField(max_length=1, choices=STATUS_FK_ACCOUNT, default='S')

    def __str__(self):
        return '%s' % (self.username)






class Employee(Account):
    user = models.OneToOneField('users.User', null=True)
    curp = models.CharField(max_length=20, null=True)
    mbid = models.CharField(max_length=30, null=True)
    department = models.CharField(max_length=250, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    businesses = models.ManyToManyField(Business, related_name='employee_businesses')
    name = models.CharField(max_length=250, null=True)
    taxpayer_id = models.CharField(max_length=14)
    bank = models.CharField(max_length=20, null=True)
    bank_account = models.CharField(max_length=20, null=True)
    modified = models.DateTimeField(null=True, auto_now=True)
    emails = ArrayField(models.EmailField(null=True), null=True)
    nss = models.CharField(max_length=30, null=True)
    joined_date = models.DateTimeField(null=True)
    antiquity = models.CharField(max_length=30, null=True)
    contract_type = models.CharField(choices=CONTRACT_TYPE, default='01', max_length=2, null=True)
    working_type = models.CharField(choices=WORKING_TYPE, default='01', max_length=2, null=True)
    regime_type = models.CharField(choices=REGIMEN_TYPE, default='02', max_length=2, null=True)
    department = models.CharField(max_length=150, null=True)
    position = models.CharField(max_length=100, null=True)
    risk = models.CharField(choices=RISK_TYPE, default='1', max_length=2, null=True)
    periodicity = models.CharField(choices=PERIODICITY_TYPE, default='04', max_length=2, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, null=True)
    daily_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, null=True)
    entfed = models.CharField(max_length=100, null=True)
    unionized = models.CharField(max_length=6, null=True)
    state = models.CharField(max_length=255, null=True)
    municipality = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['taxpayer_id']
        unique_together = (('business', 'taxpayer_id'))
        indexes = [
            models.Index(fields=['taxpayer_id', ]),
        ]

    def __str__(self):
        return "%s (%s)" % (self.name, self.taxpayer_id)

    def get_emails(self):
        return ", ".join(self.emails)

    def send_register_email(self, email):
        try:
            from_email = settings.DEFAULT_FROM_EMAIL
            subject = 'ACCESOS | PORTAL DE NOMINA'
            html_url = 'invoices/send_register_employe.html'
            context = {
                'receiver_name': self.name,
                'username': self.user.email,
                'password': self.taxpayer_id,
                'url': settings.DOMAIN
            }

            html_content = render_to_string(html_url, context)
            msg = EmailMessage(subject, html_content, from_email, [email])
            msg.content_subtype = "html"
            msg.send()

            print('Accesos enviados correctamente a: {} ({})'.format(self.name, self.taxpayer_id))

        except Exception as e:
            print("Exception in send_register_email => {} => {}".format(email, str(e)))

    def get_path_state_municipality(self):
        return '%s/%s' % (self.state, self.municipality)



class SatFile(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=20, null=True)
    status = models.CharField(choices=CSD_STATUS, default='A', max_length=1)
    cer_file = models.FileField('Cer', storage=OverrideFileSystemStorage(), upload_to=satfile_storage, null=True, max_length=200, blank=True)
    key_file = models.FileField('Key', storage=OverrideFileSystemStorage(), upload_to=satfile_storage, null=True, max_length=200, blank=True)
    passphrase = models.CharField(max_length=256, null=True)
    default = models.BooleanField(default=False)


class News(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)


class Address(models.Model):
    country = models.CharField(max_length=128, null=True)
    state = models.CharField(max_length=128, null=True)
    municipality = models.CharField(max_length=128, null=True)
    locality = models.CharField(max_length=128, null=True)
    neighborhood = models.CharField(max_length=128, null=True)
    zipcode = models.CharField(max_length=10, null=True)
    street = models.CharField(max_length=128, null=True)
    external_number = models.CharField(max_length=100, null=True)
    internal_number = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=15, default='', null=True)

    def __unicode__(self):
        return (
            u'%s %s %s, %s, %s, %s, %s' %
            (
                self.street, self.external_number, self.internal_number,
                self.zipcode, self.municipality, self.state,
                self.country
            )
        )



class PayRoll(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    filename = models.CharField(max_length=255, null=True)
    upload = models.ForeignKey('Upload', on_delete=models.CASCADE, null=True)
    version = models.CharField(max_length=5, default='3.3')
    taxpayer_id = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=250, null=True)
    rtaxpayer_id = models.CharField(max_length=15, null=True)
    rname = models.CharField(max_length=250, null=True)
    uuid = models.CharField(max_length=40, null=True)
    serial = models.CharField(max_length=30, null=True)
    folio = models.CharField(max_length=50, null=True)
    emission_date = models.DateTimeField(null=True)
    stamping_date = models.DateTimeField(null=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=24, decimal_places=6, default=0.0)
    total = models.DecimalField(max_digits=24, decimal_places=6, default=0.0)
    discount = models.DecimalField(max_digits=24, decimal_places=6, default=0.0)
    status = models.CharField(choices=INVOICE_STATUS, default='P', max_length=1)
    status_sat = models.CharField(max_length=1, choices=INVOICE_STATUS_SAT, default='V')
    payment_way = models.CharField(choices=PAYMENT_WAY, default='01', max_length=10, null=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD, default='PUE', max_length=10, null=True)
    _xml = models.FileField(storage=OverrideFileSystemStorage(), upload_to='%Y/%m/%d/%H/', null=True, db_column='xml')
    _pdf = models.FileField(storage=OverrideFileSystemStorage(), upload_to='%Y/%m/%d/%H/', null=True, db_column='pdf')
    _txt = models.FileField('Txt', storage=OverrideFileSystemStorage(), upload_to=txt_storage, null=True, db_column='txt')
    sign = models.FileField('Sign', storage=OverrideFileSystemStorage(), upload_to=signed_storage, null=True, max_length=200, blank=True)
    signed = models.BooleanField(default=False)
    notes = models.TextField(null=True)
    payroll_num = models.PositiveSmallIntegerField(default=1)
    total_per = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_ded = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_oth = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    observations = models.TextField(null=True)
    relation_type = models.CharField(choices=RELATION_TYPE, null=True, default=None, max_length=2)
    relation_lst = ArrayField(models.CharField(max_length=40, null=True), null=True, default=[])
    last_status_sat = models.DateTimeField(auto_now_add=True, db_index=True)
    business_number = models.CharField(max_length=30, null=True)
    period = models.CharField(max_length=15, null=True)
    mbid = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=60, null=True)

    def __str__(self):
        if self.status == "S":
            return self.uuid
        else:
            return "Serie:{} - Folio:{}".format(self.serial, self.folio)

    class Meta:
        index_together = [['business', 'emission_date'], ['business', 'rtaxpayer_id']]
        unique_together = [['uuid', ], ['business', 'serial', 'folio']]
        ordering = ['-emission_date']
        indexes = [
            models.Index(fields=['taxpayer_id', ]),
            models.Index(fields=['uuid', ]),
            models.Index(fields=['status', ]),
        ]

    @property
    def xml(self):
        xml_string = self._xml.read()
        try:
            xml_string = xml_string.encode('utf-8')
        except:
            pass
        finally:
            self._xml.seek(0)
        return xml_string

    @xml.setter
    def xml(self, value):
        name = self.filename
        if self.filename is None:
            name = self.uuid
        else:
            name = self.filename.replace('txt', 'xml')
        content_file = ContentFile(value, name=name)
        self._xml.save(content_file.name, content_file, save=True)

    @property
    def txt(self):
        txt_string = self._txt.read()
        try:
            txt_string = txt_string.encode('utf-8')
        except:
            pass
        finally:
            self._txt.seek(0)
        return txt_string

    @txt.setter
    def txt(self, value):
        content_file = ContentFile(value, name='%s.txt' % self.filename)
        self._txt.save(content_file.name, content_file, save=True)

    def xml_etree(self):
        from lxml import etree
        xml_string = self.xml
        return etree.fromstring(xml_string)

    def get_satquery_str(self):
        return '?re={}&rr={}&tt={:017f}&id={}'.format(self.taxpayer_id.replace('&', '&amp;'), self.rtaxpayer_id.replace('&', '&amp;'), float(self.total), self.uuid)

    def get_total_per(self):
        result_sum = self.details.aggregate(sum=models.Sum('total_per'))['sum']
        if result_sum is not None:
            self.total_per = result_sum
            self.save()
        return result_sum if result_sum is not None else 0.00

    def get_total_ded(self):
        result_sum = self.details.aggregate(sum=models.Sum('total_ded'))['sum']
        if result_sum is not None:
            self.total_ded = result_sum
            self.save()
        return result_sum if result_sum is not None else 0.00

    def get_total_oth(self):
        result_sum = self.details.aggregate(sum=models.Sum('total_oth'))['sum']
        if result_sum is not None:
            self.total_oth = result_sum
            self.save()
        return result_sum if result_sum is not None else 0.00

    def reset(self):
        self.details.all().delete()

    def send_mail(self):
        from app.core.utils import CreatePDF
        success = False
        try:
            if self.status == 'S' and ((self.employee and self.employee.email) or (self.business.id in (94,) and self.email)):
                result_pdf = CreatePDF(xml_path=self._xml.path, filename=self.filename, business_number=self.details.first().business_number)
                if not result_pdf.success:
                    raise Exception("Error al crear PDF")

                filenamepdf = '/tmp/%s' % (self.filename.replace('txt', 'pdf'))
                subject = u'Envio de Comprobante Fiscal de Nómina'
                from_email = settings.DEFAULT_FROM_EMAIL
                extra_dic = {
                    'receiver_name':self.rname,
                    'emision_date':self.emission_date,
                    'uuid':self.uuid,
                    'issuces_name':self.name,
                    'taxpayer_id':self.taxpayer_id,
                    'rtaxpayer_id':self.rtaxpayer_id
                }

                html_content = render_to_string('invoices/send_cfdi.html', extra_dic)

                if self.business.id in (94,):
                    emails_send = [self.email]
                else:
                    emails_send = self.employee.email

                msg = EmailMessage(subject, html_content, from_email, emails_send)
                msg.content_subtype = "html"
                if self.business.send_mail_encryption:
                  zip_path = '{}{}'.format(settings.PATH_REPORTS_TMP, self.filename.replace('txt', 'zip'))
                  pyminizip.compress_multiple([self._xml.path, filenamepdf], ['', ''], zip_path, self.business.password, 5)
                  msg.attach_file(zip_path)
                  msg.send()
                  os.remove(zip_path)
                  os.remove(filenamepdf)
                else:
                  msg.attach_file(self._xml.path)
                  msg.attach_file(filenamepdf)
                  smtp_response = msg.send()
                  if smtp_response == 1:
                    if self.business.id not in (94,):
                        self.email = self.employee.email[0]
                        self.save()
                    print('Correo Enviado satisfactoriamente => Emisor:{} => UUID:{} => Emails:{}'.format(self.taxpayer_id, self.uuid, emails_send))
                    success = True
                  os.remove(filenamepdf)
        except Exception as e:
            print("Exception in send_mail => {}".format(str(e)))
        return success

    def get_filename(self):
        return '%s-%s-%s-%s-%s' % (
            self.rtaxpayer_id,
            self.employee.mbid,
            self.details.filter()[0].departament,
            self.details.filter()[0].paid_date_from,
            self.details.filter()[0].paid_date_to,
        )

    def get_xml(self):
        response, client = FinkokWS.get_xml(self.uuid, self.taxpayer_id)
        if hasattr(response, 'xml') and response['xml']:
            self.xml = response['xml'].encode('utf8')
            self.save()
            print("XMl:{} saved seccessfuly".format(self.uuid))

    def get_path_xml_employee(self):
        path = 'SIN_LUGAR_DE_PAGO'
        try:
            path = '%s/%s' % (self.employee.get_path_state_municipality(), os.path.basename(self._xml.path))
        except:
            path = 'SIN_LUGAR_DE_PAGO/%s' % (os.path.basename(self._xml.path))
        return  path

class PayRollDetail(models.Model):
    payroll = models.ForeignKey(PayRoll, related_name='details', on_delete=models.CASCADE)
    version = models.CharField(max_length=5, default='1.2')
    payroll_type = models.CharField(choices=PAYROLL_TYPE, default='O', max_length=1)
    departament = models.CharField(max_length=100, null=True)
    business_number = models.CharField(max_length=30, null=True)
    period = models.CharField(max_length=15, null=True)
    paid_date = models.DateField(null=True)
    paid_date_from = models.DateField(null=True)
    paid_date_to = models.DateField(null=True)
    paid_days = models.FloatField(null=True)
    total_per = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_ded = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_oth = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    perceptions_json = JSONField(null=True)
    deductions_json = JSONField(null=True)
    registropatronal = models.CharField(max_length=30, null=True)
    retirement = JSONField(null=True)
    separation = JSONField(null=True)

    def get_total_per(self, ptype='gravado'):
        if ptype == 'gravado':
            result_sum = self.perceptions.aggregate(sum=models.Sum('amount_grav'))
        elif ptype == 'exento':
            result_sum = self.perceptions.aggregate(sum=models.Sum('amount_exp'))
        return result_sum['sum'] if result_sum['sum'] is not None else 0.00

    def get_total_ded(self):
        result_sum = self.deductions.aggregate(sum=models.Sum('amount'))
        return result_sum['sum'] if result_sum['sum'] is not None else 0.00

    def get_total_oth(self):
        result_sum = self.otherpayments.aggregate(sum=models.Sum('amount'))
        return result_sum['sum'] if result_sum['sum'] is not None else 0.00

    def get_perseptions_list(self):

        perceptions_dict = perceptions_dicts
        perceptions_list = []

        try:

            perceptions = self.perceptions.values('type').order_by('type').annotate(grav=Sum('amount_grav'), exp=Sum('amount_exp'))
            for perception in perceptions:
                perceptions_dict['perception_{}_grav'.format(perception['type'])] = float(perception['grav'])
                perceptions_dict['perception_{}_exp'.format(perception['type'])] = float(perception['exp'])
            for key in sorted(perceptions_dict):
                perceptions_list.append(perceptions_dict[key])

        except Exception as e:
            print("Exception in get_perseptions_dic => {}".format(str(e)))

        return perceptions_list

    def get_deductions_list(self):

        deductions_dict = deductions_dicts
        deductions_list = []

        try:

            deductions = self.deductions.values('type').order_by('type').annotate(amount=Sum('amount'))
            for deduction in deductions:
                deductions_dict['deduction_{}'.format(deduction['type'])] = float(deduction['amount'])
            for key in sorted(deductions_dict):
                deductions_list.append(deductions_dict[key])

        except Exception as e:
            print("Exception in get_deductions_list => {}".format(str(e)))

        return deductions_list

    def get_otherpayments_list(self):

        otherpayments_dict = otherpayments_dicts
        otherpayments_list = []

        try:

            otherpayments = self.otherpayments.values('type').order_by('type').annotate(amount=Sum('amount'))
            for otherpayment in otherpayments:
                otherpayments_dict['otherpayment_{}'.format(otherpayment['type'])] = float(otherpayment['amount'])
            for key in sorted(otherpayments_dict):
                otherpayments_list.append(otherpayments_dict[key])

        except Exception as e:
            print("Exception in get_otherpayments_list => {}".format(str(e)))

        return otherpayments_list

    def get_info_to_report(self):
        try:
            payroll_obj = self.payroll
            employee_obj = payroll_obj.employee

            return [
                str(payroll_obj.folio), # Folio
                payroll_obj.taxpayer_id, # "CFDI:Emisor RFC"
                payroll_obj.mbid, # CLIENTE @DUDA??????????
                employee_obj.position, # Departamento
                payroll_obj.rname, # "Nombre"
                payroll_obj.rtaxpayer_id, # "Receptor RFC"
                employee_obj.curp, # "CURP"
                employee_obj.nss, # "Num Seguridad Social"
                self.registropatronal, # "Registro Patronal"
                payroll_obj.stamping_date, # "Fecha Timbrado"
                self.paid_date_from, # "Fecha Inicial de Pago"
                self.paid_date_to, # "Fecha Final de Pago"
                self.period, # "Periodo" @DUDA??????????
                self.get_payroll_type_display(), # "Tipo"
                payroll_obj.uuid, # "UUID"
                self.paid_days, # "Num Dias Pagados"
                employee_obj.periodicity, # "Periodicidad Pago"
                float(employee_obj.daily_salary) if employee_obj.daily_salary else 0.00, # "Salario Diario Integral"
                float(employee_obj.base_salary) if employee_obj.base_salary else 0.00, # "Salario Base de Cotizacion"
            ] + self.get_perseptions_list() + self.get_deductions_list() + self.get_otherpayments_list() + [
                float(self.perceptions_json['TotalGravado'] if self.perceptions_json['TotalGravado'] else '0.00'), # "Percepciones Total Gravado"
                float(self.perceptions_json['TotalExento'] if self.perceptions_json['TotalExento'] else '0.00'), # "Percepciones Total Exento"
                float(self.total_ded), # Deducciones Total
                float(self.total_oth), # "OtrosPagos Total"
                float(payroll_obj.total), # "Total"
                self.payroll.get_status_sat_display(), # "Estado"
                payroll_obj.version, # "Version"
            ]

        except Exception as e:
            print("Exception in get_info_to_report => {}".format(str(e)))
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(self.perceptions_json)
            print(payroll_obj)
            return None

    class Meta:
        index_together = [['paid_date_from', 'paid_date_to']]
        indexes = [
            models.Index(fields=['business_number', ]),
        ]



class Perception(models.Model):
    payroll = models.ForeignKey(PayRollDetail, related_name='perceptions', on_delete=models.CASCADE)
    type = models.CharField(choices=PERCEPTION_TYPE, max_length=3)
    code = models.CharField(max_length=15, null=True)
    concept = models.CharField(max_length=150, null=True)
    amount_exp = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    amount_grav = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    extra_hrs = JSONField(null=True)





class Deduction(models.Model):
    payroll = models.ForeignKey(PayRollDetail, related_name='deductions', on_delete=models.CASCADE)
    type = models.CharField(choices=DEDUCTION_TYPE, max_length=3)
    code = models.CharField(max_length=15, null=True)
    concept = models.CharField(max_length=150, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)




class OtherPayment(models.Model):
    payroll = models.ForeignKey(PayRollDetail, related_name='otherpayments', on_delete=models.CASCADE)
    type = models.CharField(choices=OTHERPAYMENT_TYPE, max_length=3)
    code = models.CharField(max_length=15, null=True)
    concept = models.CharField(max_length=150, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)





class Inability(models.Model):
    payroll = models.ForeignKey(PayRollDetail, related_name='inabilities', on_delete=models.CASCADE)
    type = models.CharField(choices=INABILITY_TYPE, max_length=3)
    days = models.IntegerField(null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)




class Notifications(models.Model):
    invoice = models.ForeignKey(PayRoll, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    title = models.TextField(default='')
    message = models.TextField(default='')
    status = models.CharField(max_length=1, choices=NOTIFICATION_STATUS, default='N')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class History(models.Model):
    business = models.ForeignKey(Business, null=True)
    employee = models.ForeignKey(Employee, null=True)
    date = models.DateTimeField(null=True, auto_now_add=True)
    totales_files = models.IntegerField(null=True)
    failed_files = models.IntegerField(null=True,)
    successful_files = models.IntegerField(null=True,)


class DetailsHistory(models.Model):
    history = models.ForeignKey(History, null=True)
    name = models.TextField(max_length=50, null=True, blank=True)
    uuid = models.TextField(max_length=36, null=True, blank=True)
    status = models.CharField(max_length=1, choices=HISTORY_STATUS, default='R')
    notes = models.TextField(null=True, blank=True)


class TokensUser(models.Model):
    token = models.TextField(null=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)





class Upload(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    business = models.ForeignKey(Business, null=True)
    name = models.TextField(max_length=150, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField('Zip', storage=OverrideFileSystemStorage(), upload_to=zip_storage, null=True, max_length=200, blank=True)
    total_txt = models.IntegerField(default=0, blank=True)
    total_txt_good = models.IntegerField(default=0, blank=True)
    total_txt_error = models.IntegerField(default=0, blank=True)
    status = models.CharField(max_length=1, choices=TASKS_STATUS, default=0)
    task_id = models.TextField(max_length=50, null=True, blank=True)
    task_status = models.CharField(max_length=30, default='PENDING')
    period_date_from = models.DateField()
    period_date_to = models.DateField()
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def add_txt_good(self):
        self.refresh_from_db()
        self.total_txt_good = F('total_txt_good')  + 1
        self.save()

    def add_txt_error(self):
        self.refresh_from_db()
        self.total_txt_error = F('total_txt_error')  + 1
        self.save()

    def generate_simple_report(self):
        success = False
        csv_path = ''

        try:
            cursor = connection.cursor()
            csv_path = '{}{}'.format(
                settings.PATH_REPORTS_TMP,
                self.name.replace('zip', 'csv')
            )
            query = settings.SIMPLE_REPORT.format(self.id, csv_path)
            cursor.execute(query)
            success = True

        except Exception as e:
            print("Exception in generate_simple_report")
            print('Upload: {}'.format(self))
            print('Error: {}'.format(str(e)))

        return success, csv_path

    def generate_report_emails_sent(self):
        success = False
        csv_path = ''

        try:
            cursor = connection.cursor()
            csv_path = '{}reporte_correos_enviados_{}'.format(
                settings.PATH_REPORTS_TMP,
                self.name.replace('zip', 'csv')
            )
            query = settings.SIMPLE_REPORT_MAILS_SENDS.format(self.id, csv_path)
            cursor.execute(query)
            success = True

        except Exception as e:
            print("Exception in generate_report_emails_sent")
            print('Upload: {}'.format(self))
            print('Error: {}'.format(str(e)))

        return success, csv_path

    def generate_stamping_report(self):
        try:

            business_obj = self.business

            payroll_filter = PayRollDetail.objects.filter(payroll__upload_id=self.id, payroll__status__in=['S', 'C'])

            filename = 'reporte_timbrado_{}'.format(
                self.name.replace('zip', 'csv')
            )

            path = '{}{}'.format(
                settings.PATH_REPORTS_TMP,
                filename
            )

            with open(path, 'w') as file:
                writer = csv.writer(file)
                writer.writerow([u'Reporte de CFDI emitidos por pago de nómina.'])
                writer.writerow([u'Correspondientes al periodo ({} - {})'.format(self.period_date_from, self.period_date_to)])
                writer.writerow([])
                writer.writerow([])
                writer.writerow(settings.HEADERS_REPORT_STAMPING)
                writer.writerow(settings.SUBHEADERS_REPORT_STAMPING)
                for payroll_obj in payroll_filter:
                    writer.writerow(payroll_obj.get_info_to_report())

            return True, path

        except Exception as e:
            print("Exception in generate_stamping_report => {}".format(str(e)))

        return False, None

    def send_report_mail(self):
        try:
            subject = u'REPORTE DEL PROCESAMIENTO DE NOMINAS'
            from_email = settings.DEFAULT_FROM_EMAIL
            extra_dic = {'upload': self}
            html_content = render_to_string('uploads/template_report_upload.html', extra_dic)
            msg = EmailMessage(subject, html_content, from_email, self.business.email)
            msg.content_subtype = "html"
            success, csv_path = self.generate_simple_report()
            if success:
                msg.attach_file(csv_path)
            success_2, csv_path_2 = self.generate_stamping_report()
            if success_2:
                msg.attach_file(csv_path_2)
            msg.send()
            print('Upload:{} Correo Enviado satisfactoriamente'.format(self))
        except Exception as e:
            print('Exception in Upload send_report_mail')
            print('Upload: {}'.format(self))
            print('Error: {}'.format(str(e)))

    def send_report_send_mail(self):
        try:
            if self.total_txt_good > 0:
                subject = u'REPORTE DEL PROCESAMIENTO DE NOMINAS (Lista de correos envaidos)'
                from_email = settings.DEFAULT_FROM_EMAIL
                extra_dic = {'upload': self}
                html_content = render_to_string('uploads/template_report_upload.html', extra_dic)
                msg = EmailMessage(subject, html_content, from_email, self.business.email)
                msg.content_subtype = "html"
                success, csv_path = self.generate_report_emails_sent()
                if success:
                    msg.attach_file(csv_path)
                msg.send()
                print('Upload:{} Correo Enviado satisfactoriamente send_report_send_mail'.format(self))
        except Exception as e:
            print('Exception in Upload send_report_send_mail')
            print('Upload: {}'.format(self))
            print('Error: {}'.format(str(e)))


REPORT_TASKS_STATUS = (
    ('P', 'Pending'),
    ('I', 'In Process'),
    ('F', 'Failed'),
    ('C', 'Completed'),
    ('D', 'downloaded'),
)

class PayrollReport(models.Model):
    business = models.ForeignKey(Business, null=True, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    xml = models.BooleanField(default=False)
    pdf = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=REPORT_TASKS_STATUS, default='P')
    invoices_ids = ArrayField(models.IntegerField(null=True), null=True, default=list)
    file = models.FileField('file', storage=OverrideFileSystemStorage(), upload_to=report_cfdis_storga, null=True, max_length=200, blank=True)
    password = models.TextField(null=True)
    notes = models.TextField(null=True)

    def __str__(self):
        return '%s (%s)' % (self.business, self.id)

    def create_only_pdf(self):
        from .tasks import create_zip_invoices_pdf
        self.set_encrypted_password()
        account = self.business
        role = account.user.first().role
        create_zip_invoices_tasks = create_zip_invoices_pdf.apply_async((self.id,),)
        return create_zip_invoices_tasks

    def create_payroll_zip(self, split_path=False):
        from .tasks import create_zip_invoices
        role = None
        account = None

        if self.business is not None:
          account = self.business
          role = account.user.first().role
        elif self.employee is not None:
          account = self.employee
          role = 'E'

        self.set_encrypted_password()
        create_zip_invoices_tasks = create_zip_invoices.apply_async((self.id, account.id, self.invoices_ids, role, split_path),)
        return create_zip_invoices_tasks.id

    def generate_password(self, length=24):
        letters = string.ascii_letters + string.ascii_uppercase + string.digits + string.punctuation
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def set_encrypted_password(self):
        self.password = signing.dumps(self.generate_password())
        self.save()

    def get_decrypted_password(self):
        return signing.loads(self.password)

    def get_encrypted_id(self):
        return signing.dumps(self.id)

    def get_file_name(self):
        return os.path.basename(self.file.path)

    def link_expiration_date(self):
        return self.created + timedelta(days=1)






