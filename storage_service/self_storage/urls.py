from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('', views.index, name='main'),
    path('my-rent', views.my_rent, name='my_rent'),
    path('boxes', views.boxes, name='boxes'),
    path('faq', views.faq, name='faq'),
    path('login', views.login_view, name='login_page'),
    path('logout', views.logout_view, name='logout_page'),

    ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
