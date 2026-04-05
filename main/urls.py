from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index,name='mainindex'),
    path('universalsearch/',views.unisearch,name='universalsearch'),
    path('saleschart',views.saleschart,name='saleschart')
]