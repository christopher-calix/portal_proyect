from django.urls import path, re_path

from . import views




app_name = 'users'

urlpatterns = [
    

 path('register/', views.RegistrationView.as_view(), name = 'register'),
 path('reset/', views.PassResetView.as_view(), name = 'reset_pass'),
 path('back_passresset/', views.BackPassResetView.as_view(), name = 'back_resset'),
 re_path(r'activate/(?P<activation_key>[-:\w]+)/$', views.ActivationView.as_view(), name = 'activate'),
 
 
#LOGIN URLS

 path('login/', views.LoginView.as_view(), name = 'login'),
 path('logout/', views.LogoutView.as_view(), name = 'logout'),
 re_path(r'password_reset/(?P<id_user>[^|]{1,25})+/$', views.PasswordResetView.as_view(), name = 'logout'),
 path('update/', views.UpdatePasswordAndEmailView.as_view(), name = 'update'),
 
 


]
"""

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("articles/2003/", views.special_case_2003),
    re_path(r"^articles/(?P<year>[0-9]{4})/$", views.year_archive),
    re_path(r"^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$", views.month_archive),
    re_path(r"^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<slug>[\w-]+)/$", views.article_detail, ),
]
"""