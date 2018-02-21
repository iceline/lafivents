
from .views import IndexView
from django.conf.urls import url

from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', IndexView.as_view(), name = 'index'), 
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name = 'login-view'),
    url(r'^accounts/profile/$', auth_views.PasswordChangeView.as_view(template_name = "password_change.html"), name = 'password-change'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page = '/accounts/login/'), name = 'logout')
]
