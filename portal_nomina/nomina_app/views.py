
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView


class Dashboard(TemplateView):
     template_name = 'views/base.html'
     
class Companias(TemplateView):
     template_name = 'views/companias.html'
     
class Empleados(TemplateView):
     template_name = 'views/empleados.html'
     
class Usuarios(TemplateView):
     template_name = 'users/.html'
     
class Comprobantes(TemplateView):
     template_name = 'views/comprobantes.html'
     
class Cargas(TemplateView):
     template_name = 'views/cargas.html'
    
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    # Additional logic or customizations can be added here
class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html' 