from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(models.StockCount)
class StockCount(ImportExportModelAdmin):
    list_display = ('Inventory','CountQty','LastTransaction','Note')
    search_fields = ['Inventory','CountQty','LastTransaction','Note']
    pass

@admin.register(models.Job)
class Job(ImportExportModelAdmin):
    list_display = ('id','Type','Status','CreateDate','Vehicle','CustomerOrVendor')
    search_fields = []
    pass

@admin.register(models.Transaction)
class Transaction(ImportExportModelAdmin):
    list_display = ('id','JobId','Inventory','Qty')
    pass

admin.site.register(models.Related)
admin.site.register(models.Profile)

admin.site.register(models.CashBook)