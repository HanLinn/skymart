from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

@admin.register(models.Product)
class Product(ImportExportModelAdmin,SimpleHistoryAdmin):
    list_display = ('ProductName','Barcode','Tag','Minimum','Image','wh_stock')
    search_fields = ['ProductName','Barcode','Tag']
    pass

# admin.site.register(models.Product,SimpleHistoryAdmin)

admin.site.register(models.Unit)
admin.site.register(models.Category)
admin.site.register(models.CurrencyRate)