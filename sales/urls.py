from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.SalesIndex,name='salesindex'),
    path('SO',views.NewSalesOrder,name='SO'),
    path('SE/<int:id>',views.EditSalesOrder,name='SE'),
    path('SD/<int:id>',views.SalesDetail,name='SD'),
    path('newsotransaction/<int:id>',views.newtransaction,name='newsotransaction'),
    path('deletetransaction/<int:id>',views.deletetransaction,name='sodeletetransaction'),
    path('edittransaction/<int:id>',views.geteditform,name='soedittransaction'),
    path('filtertransaction/<int:id>/<int:p>',views.filtertransaction,name='filtertransaction'),
    path('getsearchresult/<int:id>',views.getsearchresult,name='getsearchresult'),
    path('getPayment/<int:id>',views.getPayment,name='getPayment'),
    path('currencyrate/',views.newcurrencyrate,name='newcurrencyrate'),
    path('ncustomer',views.newcustomer,name='ncustomer'),
    path('editcustomer/<int:id>',views.editcustomer,name='editcustomer'),
    path('importjob/<int:sid>',views.ImportFromJob,name='importjob'),
    path('invoice/<int:id>/<int:p>',views.SalesInvoice,name='invoice'),
    path('customerlist',views.customerlist,name='customerlist'),
    path('history/<int:id>',views.saleshistory,name='saleshistory'),
    path('POS/<int:id>',views.POS,name='POS'),
    path('barcode/<int:id>',views.Barcode,name='barcode'),
    path('solistfilter',views.SO_List_Filter,name='solistfilter'),
    path('quicksales/<int:c>',views.QuickSales,name='quicksales'),
    path('export/',views.export_to_excel,name='export_to_excel'),
    path('test/',views.test,name='test')
]