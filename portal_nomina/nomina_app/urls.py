from django.urls import path

from . import views




app_name = 'nomina_app'
urlpatterns = [
    path('', views.Dashboard.as_view(), name = 'home'),
    path('', views.Companias.as_view(), name = 'companias'),
    path('', views.Empleados.as_view(), name = 'empleados'),
    path('', views.Usuarios.as_view(), name = 'users'),
    path('', views.Comprobantes.as_view(), name = 'comprobantes'),
    path('', views.Cargas.as_view(), name = 'cargas'),
  # path('', views.Dashboard.as_view(), name = 'home'),


]