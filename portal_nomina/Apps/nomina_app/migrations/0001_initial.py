# Generated by Django 4.2.6 on 2024-01-11 17:55

import Apps.nomina_app.models
import Apps.nomina_app.storage
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=128, null=True)),
                ('state', models.CharField(max_length=128, null=True)),
                ('municipality', models.CharField(max_length=128, null=True)),
                ('locality', models.CharField(max_length=128, null=True)),
                ('neighborhood', models.CharField(max_length=128, null=True)),
                ('zipcode', models.CharField(max_length=10, null=True)),
                ('street', models.CharField(max_length=128, null=True)),
                ('external_number', models.CharField(max_length=100, null=True)),
                ('internal_number', models.CharField(max_length=100, null=True)),
                ('phone', models.CharField(default='', max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taxpayer_id', models.CharField(db_index=True, max_length=14, null=True, unique=True)),
                ('name', models.CharField(db_index=True, max_length=256, null=True)),
                ('email', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254, null=True, verbose_name='Correo electrónico'), default=list, null=True, size=None)),
                ('status', models.CharField(choices=[('A', 'Active'), ('P', 'Pending'), ('S', 'Suspended'), ('R', 'Revoked')], default='P', max_length=1)),
                ('default', models.BooleanField(default=False)),
                ('logo', models.FileField(blank=True, max_length=200, null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorageImg(), upload_to=Apps.nomina_app.storage.logo_storage, verbose_name='Logo')),
                ('payroll_filename', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10, null=True), default=list, null=True, size=None)),
                ('send_mail_encryption', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=30, null=True)),
                ('type', models.CharField(choices=[('S', 'Staff'), ('O', 'Operaciones'), ('P', 'Payroll'), ('L', 'latin')], default='S', max_length=1)),
                ('sat_name', models.CharField(max_length=256, null=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.address')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curp', models.CharField(max_length=20, null=True)),
                ('mbid', models.CharField(max_length=30, null=True)),
                ('name', models.CharField(max_length=250, null=True)),
                ('taxpayer_id', models.CharField(max_length=14, unique=True)),
                ('bank', models.CharField(max_length=20, null=True)),
                ('bank_account', models.CharField(max_length=20, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('emails', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254, null=True), null=True, size=None)),
                ('nss', models.CharField(max_length=30, null=True)),
                ('joined_date', models.DateTimeField(null=True)),
                ('antiquity', models.CharField(max_length=30, null=True)),
                ('contract_type', models.CharField(choices=[('01', 'Contrato de trabajo por tiempo indeterminado'), ('02', 'Contrato de trabajo para obra determinada'), ('03', 'Contrato de trabajo por tiempo determinado'), ('04', 'Contrato de trabajo por temporada'), ('05', 'Contrato de trabajo sujeto a prueba'), ('06', 'Contrato de trabajo con capacitación inicial'), ('07', 'Modalidad de contratación por pago de hora laborada'), ('08', 'Modalidad de trabajo por comisión laboral'), ('09', 'Modalidades de contratación donde no existe relación de trabajo'), ('10', 'Jubilación, pensión, retiro.'), ('99', 'Otro contrato')], default='01', max_length=2, null=True)),
                ('working_type', models.CharField(choices=[('01', '01 - Diurna'), ('02', '02 - Nocturna'), ('03', '03 - Mixta'), ('04', '04 - Por hora'), ('05', '05 - Reducida'), ('06', '06 - Continuada'), ('07', '07 - Partida'), ('08', '08 - Por turnos'), ('99', '99 - Otra Jornada')], default='01', max_length=2, null=True)),
                ('regime_type', models.CharField(choices=[('02', '02 - Sueldos'), ('03', '03 - Jubilados'), ('04', '04 - Pensionados'), ('05', '05 - Asimilados Miembros Sociedades Cooperativas Produccion'), ('06', '06 - Asimilados Integrantes Sociedades Asociaciones Civiles'), ('07', '07 - Asimilados Miembros consejos'), ('08', '08 - Asimilados comisionistas'), ('09', '09 - Asimilados Honorarios'), ('10', '10 - Asimilados acciones'), ('11', '11 - Asimilados otros'), ('12', '12 - Jubilados o Pensionados'), ('99', '99 - Otro Regimen')], default='02', max_length=2, null=True)),
                ('department', models.CharField(max_length=150, null=True)),
                ('position', models.CharField(max_length=100, null=True)),
                ('risk', models.CharField(choices=[('1', '1 Clase I'), ('2', '2 Clase II'), ('3', '3 Clase III'), ('4', '4 Clase IV'), ('5', '5 Clase V'), ('99', '99 No aplica')], default='1', max_length=2, null=True)),
                ('periodicity', models.CharField(choices=[('01', 'Diario'), ('02', 'Semanal'), ('03', 'Catorcenal'), ('04', 'Quincenal'), ('05', 'Mensual'), ('06', 'Bimestral'), ('07', 'Unidad obra'), ('08', 'Comisión'), ('09', 'Precio alzado'), ('10', 'Decenal'), ('99', 'Otra Periodicidad')], default='04', max_length=2, null=True)),
                ('base_salary', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, null=True)),
                ('daily_salary', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, null=True)),
                ('entfed', models.CharField(max_length=100, null=True)),
                ('unionized', models.CharField(max_length=6, null=True)),
                ('state', models.CharField(max_length=255, null=True)),
                ('municipality', models.CharField(max_length=255, null=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('businesses', models.ManyToManyField(related_name='employee_businesses', to='nomina_app.business')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.profile')),
            ],
            options={
                'ordering': ['taxpayer_id'],
            },
        ),
        migrations.CreateModel(
            name='FKAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('pricing', models.FloatField()),
                ('status', models.CharField(choices=[('A', 'Active'), ('S', 'Suspended')], default='S', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='PayRoll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255, null=True)),
                ('version', models.CharField(default='3.3', max_length=5)),
                ('taxpayer_id', models.CharField(max_length=20, null=True)),
                ('name', models.CharField(max_length=250, null=True)),
                ('rtaxpayer_id', models.CharField(max_length=15, null=True)),
                ('rname', models.CharField(max_length=250, null=True)),
                ('uuid', models.CharField(max_length=40, null=True)),
                ('serial', models.CharField(max_length=30, null=True)),
                ('folio', models.CharField(max_length=50, null=True)),
                ('emission_date', models.DateTimeField(null=True)),
                ('stamping_date', models.DateTimeField(null=True)),
                ('cancellation_date', models.DateTimeField(blank=True, null=True)),
                ('subtotal', models.DecimalField(decimal_places=6, default=0.0, max_digits=24)),
                ('total', models.DecimalField(decimal_places=6, default=0.0, max_digits=24)),
                ('discount', models.DecimalField(decimal_places=6, default=0.0, max_digits=24)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('E', 'Error'), ('C', 'Cancelado'), ('S', 'Stamped')], default='P', max_length=1)),
                ('status_sat', models.CharField(choices=[('V', 'Vigente'), ('C', 'Cancelado'), ('N', 'No Encontrado')], default='V', max_length=1)),
                ('payment_way', models.CharField(choices=[('01', 'Efectivo'), ('02', 'Cheque nominativo'), ('03', 'Transferencia electrónica de fondos'), ('04', 'Tarjeta de crédito'), ('05', 'Monedero electrónico'), ('06', 'Dinero electrónico'), ('08', 'Vales de despensa'), ('12', 'Dación en pago'), ('13', 'Pago por subrogación'), ('14', 'Pago por consignación'), ('15', 'Condonación'), ('17', 'Compensación'), ('23', 'Novación'), ('24', 'Confusión'), ('25', 'Remisión de deuda'), ('26', 'Prescripción o caducidad'), ('27', 'A satisfacción del acreedor'), ('28', 'Tarjeta de débito'), ('29', 'Tarjeta de servicios'), ('30', 'Aplicación de anticipos'), ('31', 'Intermediario pagos'), ('99', 'Por definir')], default='01', max_length=10, null=True)),
                ('payment_method', models.CharField(choices=[('PUE', 'Pago en una sola exhibición'), ('PPD', 'Pago en parcialidades o diferido')], default='PUE', max_length=10, null=True)),
                ('_xml', models.FileField(db_column='xml', null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to='%Y/%m/%d/%H/')),
                ('_pdf', models.FileField(db_column='pdf', null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to='%Y/%m/%d/%H/')),
                ('_txt', models.FileField(db_column='txt', null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to=Apps.nomina_app.storage.txt_storage, verbose_name='Txt')),
                ('sign', models.FileField(blank=True, max_length=200, null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to=Apps.nomina_app.storage.signed_storage, verbose_name='Sign')),
                ('signed', models.BooleanField(default=False)),
                ('notes', models.TextField(null=True)),
                ('payroll_num', models.PositiveSmallIntegerField(default=1)),
                ('total_per', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_ded', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_oth', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('observations', models.TextField(null=True)),
                ('relation_type', models.CharField(choices=[('01', 'Nota de crédito de los documentos relacionados'), ('02', 'Nota de débito de los documentos relacionados'), ('03', 'Devolución de mercancía sobre facturas o traslados previos'), ('04', 'Sustitución de los CFDI previos'), ('05', 'Traslados de mercancias facturados previamente'), ('06', 'Factura generada por los traslados previos'), ('07', 'CFDI por aplicación de anticipo'), ('08', 'Factura generada por pagos en parcialidades'), ('09', 'Factura generada por pagos diferidos')], default=None, max_length=2, null=True)),
                ('relation_lst', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=40, null=True), default=list, null=True, size=None)),
                ('last_status_sat', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('business_number', models.CharField(max_length=30, null=True)),
                ('period', models.CharField(max_length=15, null=True)),
                ('mbid', models.CharField(max_length=30, null=True)),
                ('email', models.CharField(max_length=60, null=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.employee')),
            ],
            options={
                'ordering': ['-emission_date'],
            },
        ),
        migrations.CreateModel(
            name='PayRollDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(default='1.2', max_length=5)),
                ('payroll_type', models.CharField(choices=[('O', 'Ordinaria'), ('E', 'ExtraOrdinaria'), ('C', 'Combinada')], default='O', max_length=1)),
                ('departament', models.CharField(max_length=100, null=True)),
                ('business_number', models.CharField(max_length=30, null=True)),
                ('period', models.CharField(max_length=15, null=True)),
                ('paid_date', models.DateField(null=True)),
                ('paid_date_from', models.DateField(null=True)),
                ('paid_date_to', models.DateField(null=True)),
                ('paid_days', models.FloatField(null=True)),
                ('total_per', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_ded', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_oth', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('perceptions_json', models.JSONField(null=True)),
                ('deductions_json', models.JSONField(null=True)),
                ('registropatronal', models.CharField(max_length=30, null=True)),
                ('retirement', models.JSONField(null=True)),
                ('separation', models.JSONField(null=True)),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='nomina_app.payroll')),
            ],
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=150, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, max_length=200, null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to=Apps.nomina_app.storage.zip_storage, verbose_name='Zip')),
                ('total_txt', models.IntegerField(blank=True, default=0)),
                ('total_txt_good', models.IntegerField(blank=True, default=0)),
                ('total_txt_error', models.IntegerField(blank=True, default=0)),
                ('status', models.CharField(choices=[(0, 'Pending'), (1, 'In Process'), (2, 'Completed'), (3, 'Failed')], default=0, max_length=1)),
                ('task_id', models.TextField(blank=True, max_length=50, null=True)),
                ('task_status', models.CharField(default='PENDING', max_length=30)),
                ('period_date_from', models.DateField()),
                ('period_date_to', models.DateField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile')),
            ],
        ),
        migrations.CreateModel(
            name='TokensUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile')),
            ],
        ),
        migrations.CreateModel(
            name='SatFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=20, null=True)),
                ('status', models.CharField(choices=[('A', 'Activo'), ('C', 'Caducado'), ('R', 'Revocado')], default='A', max_length=1)),
                ('cer_file', models.FileField(blank=True, max_length=200, null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to=Apps.nomina_app.storage.satfile_storage, verbose_name='Cer')),
                ('key_file', models.FileField(blank=True, max_length=200, null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to=Apps.nomina_app.storage.satfile_storage, verbose_name='Key')),
                ('passphrase', models.CharField(max_length=256, null=True)),
                ('default', models.BooleanField(default=False)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
            ],
        ),
        migrations.CreateModel(
            name='Perception',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('001', 'Sueldos, Salarios  Rayas y Jornales'), ('002', 'Gratificación Anual (Aguinaldo)'), ('003', 'Participación de los Trabajadores en las Utilidades PTU'), ('004', 'Reembolso de Gastos Médicos Dentales y Hospitalarios'), ('005', 'Fondo de Ahorro'), ('006', 'Caja de ahorro'), ('009', 'Contribuciones a Cargo del Trabajador Pagadas por el Patrón'), ('010', 'Premios por puntualidad'), ('011', 'Prima de Seguro de vida'), ('012', 'Seguro de Gastos Médicos Mayores'), ('013', 'Cuotas Sindicales Pagadas por el Patrón'), ('014', 'Subsidios por incapacidad'), ('015', 'Becas para trabajadores y/o hijos'), ('019', 'Horas extra'), ('020', 'Prima dominical'), ('021', 'Prima vacacional'), ('022', 'Prima por antigüedad'), ('023', 'Pagos por separación'), ('024', 'Seguro de retiro'), ('025', 'Indemnizaciones'), ('026', 'Reembolso por funeral'), ('027', 'Cuotas de seguridad social pagadas por el patrón'), ('028', 'Comisiones'), ('029', 'Vales de despensa'), ('030', 'Vales de restaurante'), ('031', 'Vales de gasolina'), ('032', 'Vales de ropa'), ('033', 'Ayuda para renta'), ('034', 'Ayuda para artículos escolares'), ('035', 'Ayuda para anteojos'), ('036', 'Ayuda para transporte'), ('037', 'Ayuda para gastos de funeral'), ('038', 'Otros ingresos por salarios'), ('039', 'Jubilaciones, pensiones o haberes de retiro'), ('044', 'Jubilaciones, pensiones o haberes de retiro en parcialidades'), ('045', 'Ingresos en acciones o títulos valor que representan bienes'), ('046', 'Ingresos asimilados a salarios'), ('047', 'Alimentación'), ('048', 'Habitación'), ('049', 'Premios por asistencia'), ('050', 'Viáticos'), ('051', 'Pagos por gratificaciones, primas, compensaciones, recompensas u otros a extrabajadores derivados de jubilación en parcialidades'), ('052', 'Pagos que se realicen a extrabajadores que obtengan una jubilación en parcialidades derivados de la ejecución de resoluciones judicial o de un laudo'), ('053', 'Pagos que se realicen a extrabajadores que obtengan una jubilación en una sola exhibición derivados de la ejecución de resoluciones judicial o de un laudo')], max_length=3)),
                ('code', models.CharField(max_length=15, null=True)),
                ('concept', models.CharField(max_length=150, null=True)),
                ('amount_exp', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('amount_grav', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('extra_hrs', models.JSONField(null=True)),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='perceptions', to='nomina_app.payrolldetail')),
            ],
        ),
        migrations.CreateModel(
            name='PayrollReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('xml', models.BooleanField(default=False)),
                ('pdf', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('I', 'In Process'), ('F', 'Failed'), ('C', 'Completed'), ('D', 'downloaded')], default='P', max_length=1)),
                ('invoices_ids', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=list, null=True, size=None)),
                ('file', models.FileField(blank=True, max_length=200, null=True, storage=Apps.nomina_app.models.OverrideFileSystemStorage(), upload_to=Apps.nomina_app.storage.report_cfdis_storga, verbose_name='file')),
                ('password', models.TextField(null=True)),
                ('notes', models.TextField(null=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.employee')),
            ],
        ),
        migrations.AddField(
            model_name='payroll',
            name='upload',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.upload'),
        ),
        migrations.CreateModel(
            name='OtherPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('001', 'Reintegro de ISR pagado en exceso (siempre que no haya sido enterado al SAT).'), ('002', 'Subsidio para el empleo (efectivamente entregado al trabajador).'), ('003', 'Viáticos (entregados al trabajador).'), ('004', 'Aplicación de saldo a favor por compensación anual.'), ('005', 'Reintegro de ISR retenido en exceso de ejercicio anterior (siempre que no haya sido enterado al SAT).'), ('999', 'Pagos distintos a los listados y que no deben considerarse como ingreso por sueldos, salarios o ingresos asimilados.')], max_length=3)),
                ('code', models.CharField(max_length=15, null=True)),
                ('concept', models.CharField(max_length=150, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otherpayments', to='nomina_app.payrolldetail')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(default='')),
                ('message', models.TextField(default='')),
                ('status', models.CharField(choices=[('N', 'new'), ('O', 'old'), ('D', 'delete')], default='N', max_length=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.employee')),
                ('invoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.payroll')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=128)),
                ('read', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Inability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('01', '01 - Riesgo de trabajo.'), ('02', '02 - Enfermedad en general.'), ('03', '03 - Maternidad.')], max_length=3)),
                ('days', models.IntegerField(null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inabilities', to='nomina_app.payrolldetail')),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('totales_files', models.IntegerField(null=True)),
                ('failed_files', models.IntegerField(null=True)),
                ('successful_files', models.IntegerField(null=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.business')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.employee')),
            ],
        ),
        migrations.CreateModel(
            name='DetailsHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=50, null=True)),
                ('uuid', models.TextField(blank=True, max_length=36, null=True)),
                ('status', models.CharField(choices=[('A', 'Accepted'), ('R', 'Rejected')], default='R', max_length=1)),
                ('notes', models.TextField(blank=True, null=True)),
                ('history', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.history')),
            ],
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('001', 'Seguridad social'), ('002', 'ISR'), ('003', 'Aportaciones a retiro, cesantía en edad avanzada y vejez.'), ('004', 'Otros'), ('005', 'Aportaciones a Fondo de vivienda'), ('006', 'Descuento por incapacidad'), ('007', 'Pensión alimenticia'), ('008', 'Renta'), ('009', 'Préstamos provenientes del Fondo Nacional de la Vivienda para los Trabajadores'), ('010', 'Pago por crédito de vivienda'), ('011', 'Pago de abonos INFONACOT'), ('012', 'Anticipo de salarios'), ('013', 'Pagos hechos con exceso al trabajador'), ('014', 'Errores'), ('015', 'Pérdidas'), ('016', 'Averías'), ('017', 'Adquisición de artículos producidos por la empresa o establecimiento'), ('018', 'Cuotas para la constitución y fomento de sociedades cooperativas y de cajas de ahorro'), ('019', 'Cuotas sindicales'), ('020', 'Ausencia (Ausentismo)'), ('021', 'Cuotas obrero patronales'), ('022', 'Impuestos Locales'), ('023', 'Aportaciones voluntarias'), ('024', 'Ajuste en Gratificación Anual (Aguinaldo) Exento'), ('025', 'Ajuste en Gratificación Anual (Aguinaldo) Gravado'), ('026', 'Ajuste en Participación de los Trabajadores en las Utilidades PTU Exento'), ('027', 'Ajuste en Participación de los Trabajadores en las Utilidades PTU Gravado'), ('028', 'Ajuste en Reembolso de Gastos Médicos Dentales y Hospitalarios Exento'), ('029', 'Ajuste en Fondo de ahorro Exento'), ('030', 'Ajuste en Caja de ahorro Exento'), ('031', 'Ajuste en Contribuciones a Cargo del Trabajador Pagadas por el Patrón Exento'), ('032', 'Ajuste en Premios por puntualidad Gravado'), ('033', 'Ajuste en Prima de Seguro de vida Exento'), ('034', 'Ajuste en Seguro de Gastos Médicos Mayores Exento'), ('035', 'Ajuste en Cuotas Sindicales Pagadas por el Patrón Exento'), ('036', 'Ajuste en Subsidios por incapacidad Exento'), ('037', 'Ajuste en Becas para trabajadores y/o hijos Exento'), ('038', 'Ajuste en Horas extra Exento'), ('039', 'Ajuste en Horas extra Gravado'), ('040', 'Ajuste en Prima dominical Exento'), ('041', 'Ajuste en Prima dominical Gravado'), ('042', 'Ajuste en Prima vacacional Exento'), ('043', 'Ajuste en Prima vacacional Gravado'), ('044', 'Ajuste en Prima por antigüedad Exento'), ('045', 'Ajuste en Prima por antigüedad Gravado'), ('046', 'Ajuste en Pagos por separación Exento'), ('047', 'Ajuste en Pagos por separación Gravado'), ('048', 'Ajuste en Seguro de retiro Exento'), ('049', 'Ajuste en Indemnizaciones Exento'), ('050', 'Ajuste en Indemnizaciones Gravado'), ('051', 'Ajuste en Reembolso por funeral Exento'), ('052', 'Ajuste en Cuotas de seguridad social pagadas por el patrón Exento'), ('053', 'Ajuste en Comisiones Gravado'), ('054', 'Ajuste en Vales de despensa Exento'), ('055', 'Ajuste en Vales de restaurante Exento'), ('056', 'Ajuste en Vales de gasolina Exento'), ('057', 'Ajuste en Vales de ropa Exento'), ('058', 'Ajuste en Ayuda para renta Exento'), ('059', 'Ajuste en Ayuda para artículos escolares Exento'), ('060', 'Ajuste en Ayuda para anteojos Exento'), ('061', 'Ajuste en Ayuda para transporte Exento'), ('062', 'Ajuste en Ayuda para gastos de funeral Exento'), ('063', 'Ajuste en Otros ingresos por salarios Exento'), ('064', 'Ajuste en Otros ingresos por salarios Gravado'), ('065', 'Ajuste en Jubilaciones, pensiones o haberes de retiro Exento'), ('066', 'Ajuste en Jubilaciones, pensiones o haberes de retiro Gravado'), ('067', 'Ajuste en Pagos por separación Acumulable'), ('068', 'Ajuste en Pagos por separación No acumulable'), ('069', 'Ajuste en Jubilaciones, pensiones o haberes de retiro Acumulable'), ('070', 'Ajuste en Jubilaciones, pensiones o haberes de retiro No acumulable'), ('071', 'Ajuste en Subsidio para el empleo (efectivamente entregado al trabajador)'), ('072', 'Ajuste en Ingresos en acciones o títulos valor que representan bienes Exento'), ('073', 'Ajuste en Ingresos en acciones o títulos valor que representan bienes Gravado'), ('074', 'Ajuste en Alimentación Exento'), ('075', 'Ajuste en Alimentación Gravado'), ('076', 'Ajuste en Habitación Exento'), ('077', 'Ajuste en Habitación Gravado'), ('078', 'Ajuste en Premios por asistencia'), ('079', 'Ajuste en Pagos distintos a los listados y que no deben considerarse como ingreso por sueldos, salarios o ingresos asimilados.'), ('080', 'Ajuste en Viáticos gravados'), ('081', 'Ajuste en Viáticos (entregados al trabajador)'), ('082', 'Ajuste en Fondo de ahorro Gravado'), ('083', 'Ajuste en Caja de ahorro Gravado'), ('084', 'Ajuste en Prima de Seguro de vida Gravado'), ('085', 'Ajuste en Seguro de Gastos Médicos Mayores Gravado'), ('086', 'Ajuste en Subsidios por incapacidad Gravado'), ('087', 'Ajuste en Becas para trabajadores y/o hijos Gravado'), ('088', 'Ajuste en Seguro de retiro Gravado'), ('089', 'Ajuste en Vales de despensa Gravado'), ('090', 'Ajuste en Vales de restaurante Gravado'), ('091', 'Ajuste en Vales de gasolina Gravado'), ('092', 'Ajuste en Vales de ropa Gravado'), ('093', 'Ajuste en Ayuda para renta Gravado'), ('094', 'Ajuste en Ayuda para artículos escolares Gravado'), ('095', 'Ajuste en Ayuda para anteojos Gravado'), ('096', 'Ajuste en Ayuda para transporte Gravado'), ('097', 'Ajuste en Ayuda para gastos de funeral Gravado'), ('098', 'Ajuste a ingresos asimilados a salarios gravados'), ('099', 'Ajuste a ingresos por sueldos y salarios gravados'), ('100', 'Ajuste en Viáticos exentos'), ('101', 'ISR Retenido de ejercicio anterior'), ('102', 'Ajuste a pagos por gratificaciones, primas, compensaciones, recompensas u otros a extrabajadores derivados de jubilación en parcialidades, gravados'), ('103', 'Ajuste a pagos que se realicen a extrabajadores que obtengan una jubilación en parcialidades derivados de la ejecución de una resolución judicial o de un laudo gravados'), ('104', 'Ajuste a pagos que se realicen a extrabajadores que obtengan una jubilación en parcialidades derivados de la ejecución de una resolución judicial o de un laudo exentos'), ('105', 'Ajuste a pagos que se realicen a extrabajadores que obtengan una jubilación en una sola exhibición derivados de la ejecución de una resolución judicial o de un laudo gravados'), ('106', 'Ajuste a pagos que se realicen a extrabajadores que obtengan una jubilación en una sola exhibición derivados de la ejecución de una resolución judicial o de un laudo exentos')], max_length=3)),
                ('code', models.CharField(max_length=15, null=True)),
                ('concept', models.CharField(max_length=150, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='nomina_app.payrolldetail')),
            ],
        ),
        migrations.AddField(
            model_name='business',
            name='finkok_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nomina_app.fkaccount'),
        ),
        migrations.AddField(
            model_name='business',
            name='user',
            field=models.ManyToManyField(to='users.profile'),
        ),
        migrations.AddIndex(
            model_name='payrolldetail',
            index=models.Index(fields=['business_number'], name='nomina_app__busines_68f938_idx'),
        ),
        migrations.AlterIndexTogether(
            name='payrolldetail',
            index_together={('paid_date_from', 'paid_date_to')},
        ),
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(fields=['taxpayer_id'], name='nomina_app__taxpaye_ed88b1_idx'),
        ),
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(fields=['uuid'], name='nomina_app__uuid_b9b082_idx'),
        ),
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(fields=['status'], name='nomina_app__status_0d69c2_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='payroll',
            unique_together={('business', 'serial', 'folio'), ('uuid',)},
        ),
        migrations.AlterIndexTogether(
            name='payroll',
            index_together={('business', 'emission_date'), ('business', 'rtaxpayer_id')},
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['taxpayer_id'], name='nomina_app__taxpaye_a19598_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='employee',
            unique_together={('business', 'taxpayer_id')},
        ),
    ]