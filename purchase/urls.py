from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.PO_List,name='purchaseindex'),
    path('receiving',views.Receive,name='receiving'),
    path('newreceive',views.NewReceive,name='newreceive'),
    path('PO',views.PO,name='PO'),
    path('polistfilter',views.PO_List_Filter,name='polistfilter'),
    path('PD/<int:id>',views.PO_Detail,name='PD'),
    path('newpotransaction/<int:id>',views.newtransaction,name='newpotransaction'),
    path('deletetransaction/<int:id>',views.deletetransaction,name='podeletetransaction'),
    path('edittransaction/<int:id>',views.geteditform,name='poedittransaction'),
    path('filtertransactionp/<int:id>/<int:p>',views.filtertransaction,name='filtertransactionp'),
    path('getsearchresult/<int:id>',views.getsearchresult,name='getsearchresultp'),
    path('newvendor',views.newvendor,name='newvendor'),
    path('newcarry',views.newcarry,name='newcarry'),
    path('importjob/<int:pid>',views.ImportFromJob,name='importjobp'),
    path('updateprice/<int:id>',views.UpdateBuyingPrice,name='updateprice'),
    path('upload/<int:id>',views.upload,name='upload'),
    path('invoice/<int:id>/<int:p>',views.PurchaseInvoice,name='Pinvoice'),
    path('receive',views.ShopReceive,name='shopreceive'),
    path('account',views.GetAccount,name='Account'),
    path('postaccount/<int:id>',views.PostAccount,name='postaccount'),
    path('accountlistfilter',views.Account_List_Filter,name='accountlistfilter'),
    path('purchasehistory/<int:id>',views.purchasehistory,name='purchasehistory')
]