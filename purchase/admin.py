from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Vendor)
admin.site.register(models.Receiving)
admin.site.register(models.PurchaseOrder)
admin.site.register(models.PO_Transaction)
admin.site.register(models.Warehouse)
admin.site.register(models.Carry)
admin.site.register(models.HardCopy)
admin.site.register(models.Account)