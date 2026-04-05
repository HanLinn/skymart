from django.db import models
from django.db.models import Sum,F
from django.conf import settings
from math import ceil
from Product.models import CurrencyRate


# Create your models here.
pricelist = [('1','Retail'),('2','Member')]
class buyer(models.Model):
    Customer_Name = models.CharField(max_length=30)
    Contact = models.CharField(max_length=50,blank=True,null=True)
    Pricelist = models.CharField(max_length=6,choices=pricelist)

    def __str__(self):
        return self.Customer_Name

status = [('O','Open'),('C','Close')]
Currency = [('B','Baht'),('K','Kyat')]

class SalesOrder(models.Model):
    CreateDate = models.DateTimeField(auto_now_add=True)
    Customer = models.ForeignKey(buyer,on_delete=models.PROTECT)
    Note = models.CharField(max_length=50,blank=True,null=True)
    Currency = models.CharField(max_length=4,choices=Currency)
    User=models.ForeignKey(settings.AUTH_USER_MODEL,
        null=True, blank=True, on_delete=models.SET_NULL,related_name='user')
    Status = models.CharField(max_length=5,choices=status,default='O')
    Pay = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def next(self):
        next = SalesOrder.objects.filter(Customer=self.Customer,id__gt=self.id).first()
        return next

    def prev(self):
        prev = SalesOrder.objects.filter(Customer=self.Customer,id__lt=self.id).last()
        return prev

    def Subtotal(self):
        sub = self.so_transaction_set.all().aggregate(s=Sum(F('Price')*F('Quantity')))
        return sub['s']

    def Refund(self):
        total = self.Subtotal()
        pay = self.Pay
        if pay == None:
            pay = 0
        if total == None:
            total = 0
        refund = pay - total
        if refund < 0:
            refund = 0
        return refund


class SO_Transaction(models.Model):
    SO = models.ForeignKey(SalesOrder,on_delete=models.PROTECT)
    Inventory = models.ForeignKey('Product.Product',on_delete=models.PROTECT)
    Quantity = models.IntegerField()
    Price = models.IntegerField()

    def __str__(self):
        return str(self.id)

    def Amount(self):
        amount = self.Quantity * self.Price
        return amount

    def Profit(self):
        rate = CurrencyRate.objects.last().Rate/100
        cost = self.Inventory.Cost
        buying = int(self.Inventory.BuyingPrice)
        if cost == None:
            cost = 0
        if buying == None:
            buying = 0
        capital = cost + buying
        if self.Inventory.Base_Currency == 'K':
            if self.SO.Currency == 'B':
                capital = int(capital * rate)
        else:

            if self.SO.Currency == 'K':
                capital = ceil(capital /rate / 50) * 50
        sub = self.Price - capital
        return sub


type=[('D','Debit'),('C','Credit')]
class Account(models.Model):
    CreateDate = models.DateTimeField(auto_now_add=True)
    Customer = models.ForeignKey(buyer,on_delete=models.PROTECT)
    Amount = models.IntegerField()
    Note = models.CharField(max_length=50)
    Type = models.CharField(max_length=6,choices=type,default='C')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)

    def balance(self):
        credit = Account.objects.filter(Customer=self.Customer,id__lte=self.id,Type='C').aggregate(c=Sum('Amount'))
        debit = Account.objects.filter(Customer=self.Customer,id__lte=self.id,Type='D').aggregate(d=Sum('Amount'))
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

