from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from pfm import views

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.main),
    path('test1', views.test1),
    path('test2', views.test2),
    path('result1', views.result1),
    path('result2', views.result2),
    path('getpfmlist', views.getpfmlist),
    path('top10', views.top10),
    path('aroma', views.aroma),
    path('result3', views.result3),
]


