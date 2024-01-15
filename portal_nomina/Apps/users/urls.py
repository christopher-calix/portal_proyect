from django.urls import path

from . import views




app_name = 'users'

urlpatterns = [
    

 path('register/', views.RegistrationView.as_view(), name = 'register'),
 path('reset/', views.PassResetView.as_view(), name = 'reset_pass'),
 path('back_passresset/', views.BackPassResetView.as_view(), name = 'back_resset'),
 path('activate/(?P<activation_key>[-:\w]+)/$', views.ActivationView.as_view(), name = 'activate'),
 
 
#LOGIN URLS

 path('login/', views.LoginView.as_view(), name = 'login'),
 path('logout/', views.LogoutView.as_view(), name = 'logout'),
 path('logout/', views.PasswordResetView.as_view(), name = 'logout'),
 path('update/', views.UpdatePasswordAndEmailView.as_view(), name = 'update'),
 
 


]