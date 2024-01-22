from django.contrib import admin

from Apps.nomina_app.models import Business, Employee, SatFile, Address, FKAccount

class BusinessInfo(admin.ModelAdmin):
  list_display = ('taxpayer_id', 'name')

class EmployeeInfo(admin.ModelAdmin):
  list_display = ('taxpayer_id', 'name')

class SatfilesInfo(admin.ModelAdmin):
  list_display = ('business_id', 'serial_number')

class AddressInfo(admin.ModelAdmin):
  list_display = ('country', 'state')

class FKAccountInfo(admin.ModelAdmin):
  list_display = ('username', 'pricing', 'status')

admin.site.register(Business, BusinessInfo)
admin.site.register(Employee, EmployeeInfo)
admin.site.register(SatFile, SatfilesInfo)
admin.site.register(Address, AddressInfo)
admin.site.register(FKAccount, FKAccountInfo)