from django.db import models
from django.conf import settings
from warehouse.models import Related
from Product.models import Product
from django.db.models import Sum,F

# Create your models here.
class Vendor(models.Model):
    Name = models.CharField(max_length=20)
    Contact = models.CharField(max_length=40,null=True,blank=True)
    Related = models.OneToOneField(Related,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.Name

    def Balance(self):
        credit = Account.objects.filter(Vendor=self.id,Type='C').aggregate(c=Sum('Amount'))
        debit = Account.objects.filter(Vendor=self.id,Type='D').aggregate(d=Sum('Amount'))
        if credit['c'] is None:
            c = 0
        else:
            c = credit['c']
        if debit['d'] is None:
            d = 0
        else:
            d = debit['d']
        balance = c - d
        return balance
        

class Carry(models.Model):
    Name = models.CharField(max_length=30)
    Contact = models.CharField(max_length=40,null=True,blank=True)

    def __str__(self):
        return self.Name

class Warehouse(models.Model):
    Code = models.CharField(max_length=5)
    Name = models.CharField(max_length=10)
    Address = models.CharField(max_length=50)

    def __str__(self):
        return self.Code

class Receiving(models.Model):
    CreateDate = models.DateTimeField(auto_now_add=True)
    Inventory = models.ForeignKey(Product,on_delete=models.CASCADE)
    Quantity = models.IntegerField()
    Note = models.CharField(max_length=50,null=True,blank=True)
    Destination = models.ForeignKey(Warehouse,on_delete=models.CASCADE)
    Vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    CarryBy = models.ForeignKey(Carry,on_delete=models.CASCADE)

status = [('O','Open'),('C','Close')]

Currency = [('B','Baht'),('K','Kyat')]
class PurchaseOrder(models.Model):
    OrderDate = models.DateField()
    Supplier = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    Note = models.CharField(max_length=50,null=True,blank=True)
    Create_By=models.ForeignKey(settings.AUTH_USER_MODEL,
        null=True, blank=True, on_delete=models.SET_NULL,related_name='Create_By')
    Status = models.CharField(max_length=5,choices=status,default='O')
    Currency = models.CharField(choices=Currency,max_length=5,default='B')

    def __str__(self):
        return str(self.id)

    @property
    def Subtotal(self):
        sub = self.po_transaction_set.all().aggregate(s=Sum(F('Price')*F('Quantity')))
        sub = sub['s']
        if sub is None:
            sub = 0
        return sub

class HardCopy(models.Model):
    PO = models.ForeignKey(PurchaseOrder,on_delete=models.CASCADE)
    Photo = models.ImageField(default="invoice/default.png",upload_to='invoice')

    def __str__(self):
        return str(self.id)

class PO_Transaction(models.Model):
    PO = models.ForeignKey(PurchaseOrder,on_delete=models.CASCADE)
    Inventory = models.ForeignKey(Product,on_delete=models.CASCADE)
    Quantity = models.IntegerField()
    Price = models.DecimalField(max_digits=8,decimal_places=2)

    def __str__(self):
        return str(self.id)

    def Amount(self):
        t = self.Quantity * self.Price
        return t

type=[('D','Debit-'),('C','Credit+')]
class Account(models.Model):
    CreateDate = models.DateTimeField(auto_now_add=True)
    AccountDate = models.DateField()
    Vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT)
    Amount = models.IntegerField()
    Note = models.CharField(max_length=50,blank=True,null=True)
    Type = models.CharField(max_length=6,choices=type,default='C')
    Photo = models.ImageField(upload_to='paymentslip',null=True,blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)

    def balance(self):
        credit = Account.objects.filter(Vendor=self.Vendor,id__lte=self.id,Type='C').aggregate(c=Sum('Amount'))
        debit = Account.objects.filter(Vendor=self.Vendor,id__lte=self.id,Type='D').aggregate(d=Sum('Amount'))
        if credit['c'] is None:
            c = 0
        else:
            c = credit['c']
        if debit['d'] is None:
            d = 0
        else:
            d = debit['d']
        balance = c - d
        return balance


