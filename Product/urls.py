from django.urls import path,include
from . import views

urlpatterns = [
    path('searchproduct/',views.searchproduct,name='searchproduct'),
    path('editprice/<int:id>',views.EditPrice,name='editprice'),
    path('editpricemodal/<int:id>',views.EditPriceModal,name='editpricemodal'),
]

