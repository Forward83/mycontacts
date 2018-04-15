"""contact URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.contact_list, name='contact_list'),
    url(r'^contact/(?P<pk>\d+)/$', views.edit_contact, name='edit_contact'),
    url(r'dublicates/$', views.dublicate_list, name='dublicate_list'),
    url(r'dublicates/merge/$', views.merge_dublicates, name='merge_dublicates'),
    url(r'^new_contact/$', views.new_contact, name='new_contact'),
    url(r'^contact/(?P<pk>\d+)/remove/$', views.remove_contact, name='remove_contact'),
    url(r'^contact/export/$', views.export_contacts, name='export_contact'),
    url(r'^contact/import/$', views.import_contacts, name='import_contact'),
    url(r'^contact/bulk_delete/$', views.bulk_delete, name='bulk_delete'),
    # url(r'^contact/import/download_template$', views.import_contacts, name='import_contact'),
    url(r'^contact/get_photos/$', views.get_photos, name='get_photos'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^sign-up/$', views.sign_up, name='sign-up'),
    url(r'^password_reset/$', auth_views.password_reset,
        {'template_name': 'registration/password_reset_form.html'}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
] 

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)