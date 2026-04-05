from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
# Register your models here.
admin.site.register(models.buyer)
admin.site.register(models.SalesOrder)


@admin.register(models.Account)
class Account(ImportExportModelAdmin):
    list_display = ('Customer','Type','Note','Amount','balance')
    search_fields = ['Customer','Type','Note','Amount']
    pass

@admin.register(models.SO_Transaction)
class SO_Transaction(ImportExportModelAdmin):
    list_display = ('id','SO','Inventory','Quantity','Price')
    search_fields = ['id','SO','Inventory','Quantity','Price']
    pass