"""victorius URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from accounts import views
from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$',views.login, name='login'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    url(r'^ajax/validate_useralias/$', views.validate_useralias, name='validate_useralias'),
    url(r'^ajax/validate_marcaalias/$', views.validate_marcaalias, name='validate_marcaalias'),
    url(r'^cambiarmarca/(?P<pk>[\w\-]+)$', views.cambiarmarca),
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
    path('', include('web.urls')),
    path('', include('apis.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

