from django.urls import path

from . import views




app_name = 'nomina_app'
urlpatterns = [
    path('', views.Dashboard.as_view(), name = 'dashboard'),
    path('company/', views.Company.as_view(), name = 'company'),
    path('employees/', views.Employees.as_view(), name = 'employe'),
    path('users/', views.Users.as_view(), name = 'users'),
    path('vouchers/', views.Vouchers.as_view(), name = 'vouchers'),
    path('uploads', views.Uploads.as_view(), name = 'upload'),



]