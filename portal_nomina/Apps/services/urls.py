from django.urls import path, re_path

from . import views

app_name = 'services'
urlpatterns = [
    path('v1/payroll/upload', views.payrolls_upload.as_view()),
    path('v1/payroll', views.payrolls_list.as_view()),
    path('v1/payroll/status', views.payrolls_status_sat.as_view()),
]
