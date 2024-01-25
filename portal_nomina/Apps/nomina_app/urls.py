from django.urls import path, re_path

from . import views




app_name = 'nomina_app'
urlpatterns = [
    
    # MAIN VIEWS #
    path('', views.Dashboard.as_view(), name = 'dashboard'),
    path('company/', views.Company.as_view(), name = 'company'),
    path('employees/', views.Employees.as_view(), name = 'employe'),
    path('users/', views.Users.as_view(), name = 'users'),
    path('vouchers/', views.Vouchers.as_view(), name = 'vouchers'),
    path('uploads/', views.Uploads.as_view(), name = 'upload'),
    
    # EXTRA CONTENT #
    
   #---- vouchers views -----#
    re_path(r'vouchers/(?P<status>[A|N|E|V|P|R|F|C]+)/$', views.ListInvoicesView.as_view(), name='list_invoices'),
    re_path(r'vouchers/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})+/$', views.ListInvoicesView.as_view(), name='list_invoices'),
    
    path('vouchers/upload/', views.UploadView.as_view(), name='upload'),
    path('vouchers/cancel/', views.CancelView.as_view(), name='cancel'),
    
    re_path(r'vouchers/download/(?P<payroll_id>[^|]{1,25})+/$', views.DownloadView.as_view(), name='download'),
    path('vouchers/delete', views.DeleteView.as_view(), name='delete'),
    re_path(r'vouchers/pdf/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})+/$', views.PDFView.as_view(), name='pdf'),

    re_path(r'invoices/txt/(?P<payroll_id>[^|]{1,25})+/$', views.TxtView.as_view(), name='txt'),
    path('vouchers/send', views.SendEmailView.as_view(), name='send'),
    path('vouchers/history/', views.HistoryView.as_view(), name='history'), 
    re_path(r'vouchers/details/(?P<id_history>[^|]{1,25})+/$', views.DetailsHistoryView.as_view(), name='details_history'), 
    
    #------  ------#
    path('notification/', views.NotificationView.as_view(), name='notification'),
    path('account/profile/', views.ProfileView.as_view(), name='profile'),
    path('account/profile/edit/', views.EditInformationView.as_view(), name='edit_information'),
    path('activate/', views.StuffsView.as_view(), name='stuffs'),
    path('users/options/', views.UserOptions.as_view(), name='user_options'),
    path('sign_payroll/', views.SignPayrollView.as_view(), name='sign_payroll'),
    
    path('$', views.GetCodeView.as_view(), name='get_code'),
    path('qr$', views.GetCodeView.as_view(), name='obtener'),
    path('tokens/add/', token_add, name='token_add'),
    path('notifications/list/', list_news, name='list_news'),
    re_path(r'notifications/list/(?P<read>[|read|0-9]+)/$', list_news, name='list_news'),
    re_path(r'secure/sign/(?P<base64string>{})$'.format(base64_pattern), sign, name='secure'),
    re_path(r'upload/zip/(?P<upload_id>[^|]{1,25})+/$', download_upload, name='download_upload'),
    path('zips', list_zips, name='list_zips'),

]