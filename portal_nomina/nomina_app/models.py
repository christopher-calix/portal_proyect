from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
import datetime

# Create your models here.



def home(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

# def my_view(request):

    ...

    # if foo:

        # return HttpResponseNotFound("<h1>Page not foun
        # d</h1>")
    # else:

        # return HttpResponse("<h1>Page was found</h1>")
