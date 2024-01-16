
from django.contrib import admin
from Apps.users.views import index
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', index, name = 'index'),
    path('dashboard/', include('Apps.nomina_app.urls')),
    path('users/', include('Apps.users.urls')),
   
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
