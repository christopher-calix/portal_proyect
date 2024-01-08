
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView



from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard'))
    return render(request, 'auth/login.html')
