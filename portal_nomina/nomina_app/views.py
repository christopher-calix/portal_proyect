
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView


class Dashboard(TemplateView):
     template_name = 'views/main_views/dashboard.html'
     
class Company(TemplateView):
     template_name = 'views/main_views/companies.html'

class Users(TemplateView):
     template_name = 'views/main_views/users.html'
     
class Employees(TemplateView):
     template_name = 'views/main_views/employees.html'

class Vouchers(TemplateView):
     template_name = 'views/main_views/vouchers.html'

class Uploads(TemplateView):
     template_name = 'views/main_views/uploads.html'
     
     
     
