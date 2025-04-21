'''
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
'''
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, path, include
from ninja import NinjaAPI

from config.views import permission_denied_view, faq_view
from currency.api import router as currency_router
from section.api import router as section_router
from user.api import router as user_router
from receipt.views import upload_receipts
from user.views import feedback_view, user_language

api = NinjaAPI()
api.add_router('/currencies/', currency_router)
api.add_router('/sections/', section_router)
api.add_router('/users/', user_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('section.urls')),
    path('chart/', include('chart.urls')),
    path('upload/', upload_receipts, name='upload_receipts'),
    path('api/', api.urls),
    path('telegram/', include('telegram.urls')),
    path('feedback/', feedback_view, name='feedback'),
    path('403/', permission_denied_view, name='403'),
    path('user/language/', user_language, name='set_language'),
    path('FAQ/', faq_view, name='set_language'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)