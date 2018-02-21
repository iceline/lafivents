
from .views import IndexView
from django.conf.urls import url

from django.contrib.auth import views as auth_views

from meterdata.views import ListMeters
from meterdata.views import sync_files
from meterdata.views import list_input_data


urlpatterns = [
    url(r'^$', ListMeters.as_view(), name = 'index'), 
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name = 'login-view'),
    url(r'^accounts/profile/$', auth_views.PasswordChangeView.as_view(template_name = "password_change.html"), name = 'password-change'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page = '/accounts/login/'), name = 'logout'),  
    url(r'^sync/$', sync_files, name = 'sync-log'),
    url(r'^input/(\d+)/$', list_input_data, name = 'input-data'),
]
