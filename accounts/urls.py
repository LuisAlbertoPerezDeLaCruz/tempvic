from django.conf.urls import url
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views


app_name = 'accounts'

urlpatterns = [
    url(r'^$',accounts_views.login, name='login'),
    url(r'^login$', accounts_views.login, name='login'),
    url(r'^logout$', accounts_views.user_logout, name='logout'),
    url(r'^ajax/validate_username/$', accounts_views.validate_username, name='validate_username'),
    url(r'^ajax/validate_useralias/$', accounts_views.validate_useralias, name='validate_useralias'),
    url(r'^ajax/validate_marcaalias/$', accounts_views.validate_marcaalias, name='validate_marcaalias'),
    url(r'^cambiarmarca/(?P<pk>[\w\-]+)$', accounts_views.cambiarmarca),
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
]
