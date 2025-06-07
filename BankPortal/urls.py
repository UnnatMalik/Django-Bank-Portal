from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from bank import views
from Manager import views
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ensure_csrf_cookie(TemplateView.as_view(template_name='homepage.html')), name='homepage'),
    path('',include('bank.urls')),
    path('manager/',include('Manager.urls')),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

handler404 = 'bank.views.handler404'
