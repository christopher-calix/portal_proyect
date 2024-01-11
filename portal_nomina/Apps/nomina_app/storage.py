# -*- coding: utf-8 -*-
import os
from datetime import datetime
from django.db import models

def satfile_storage(instance, filename):
    ext = filename.split('.')[-1]
    upload_to = os.path.join('satfiles', instance.serial_number[16:18], instance.serial_number[18:20])
    return os.path.join(upload_to, f'{instance.serial_number}.{ext}')  #

def logo_storage(instance, filename):
    ext = filename.split('.')[-1]
    upload_to = os.path.join('logo', instance.taxpayer_id)
    return os.path.join(upload_to, f'{instance.taxpayer_id}.{ext}')

def signed_storage(instance, filename):
    ext = filename.split('.')[-1]
    upload_to = os.path.join('firmas', instance.uuid)
    return os.path.join(upload_to, f'{instance.uuid}.{ext}')

def zip_storage(instance, filename):
    try:
        upload_to = os.path.join('zip', instance.upload.name.replace('.zip', ''))
    except models.ObjectDoesNotExist:  # Handle potential model errors
        upload_to = os.path.join('zip', instance.name.replace('.zip', ''))
    return os.path.join(upload_to, f'{instance.name}')

def txt_storage(instance, filename):
    upload_to = os.path.join('txt', instance.upload.name.replace('.zip', ''))
    return os.path.join(upload_to, f'{instance.filename}')

def report_cfdis_storga(instance, filename):
    account = instance.business or instance.employee  # Use concise logic for account check
    filename = f'NOMINAS_{account.taxpayer_id if account else ""}_{datetime.now().replace(microsecond=0).isoformat()}.zip'
    return os.path.join('reportes', filename)
