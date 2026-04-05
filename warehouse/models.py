from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum,F,Func
from django.core.exceptions import ObjectDoesNotExist


# Create your models here.
class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()

type=[('I','Inbound'),('O','Outbound')]
status = [('W','Waiting'),('C','Complete')]

class StockCount(models.Model):
    CountDate = models.DateTimeField(auto_now = True)
    Inventory = models.OneToOneField("Product.Product",on_delete=models.CASCADE,primary_key=True)
    CountQty = models.IntegerField()
    LastTransaction = models.IntegerField(blank=True,null=True)
    Note = models.CharField(max_length=80,blank=True,null=True)

class Related(models.Model):
    RelatedName = models.CharField(max_length=20)

    class Meta:
        ordering = ['RelatedName']

    def __str__(self):
        return self.RelatedName


warehouse = [('W','Warehouse'),('2','Warehouse2'),('S','Shop')]
class Job(models.Model):
    Type = models.CharField(max_length=10,choices=type,default="O")
    Status = models.CharField(choices=status,max_length=8,default='W')
    CreateDate = models.DateTimeField(auto_now_add=True)
    Agent = models.CharField(max_length=20,null=True,blank=True)
    CustomerOrVendor = models.ForeignKey(Related,on_delete=models.CASCADE)
    Vehicle = models.CharField(max_length=10)
    Note = models.CharField (max_length=50,blank=True,null=True)
    CreateBy=models.ForeignKey(settings.AUTH_USER_MODEL,
        null=True, blank=True, on_delete=models.SET_NULL,related_name='CreateBy')
    OperateBy=models.ForeignKey(settings.AUTH_USER_MODEL,
        null=True, blank=True, on_delete=models.SET_NULL,related_name='OperateBy')
    Photo = models.ImageField(default="default.png",upload_to='Job_photo')
    OperateTime = models.DateTimeField(auto_now=True)
    Warehouse = models.CharField(choices=warehouse,max_length=1,default='W')

    def __str__(self):
        return str(self.id)

    def totalQty(self):
        tq = Transaction.objects.filter(JobId=self.id).aggregate(q= Sum('Qty'))
        total = tq['q']
        return total

class Transaction(models.Model):
    Inventory = models.ForeignKey("Product.Product",on_delete=models.CASCADE)
    Qty = models.IntegerField()
    JobId = models.ForeignKey(Job,on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)

    def actualQty(self):
        if self.JobId.Type == 'O':
            aq = self.Qty * -1
        else:
            aq = self.Qty 
        return aq

    def RunningStock(self):
        try:
            stocktable = StockCount.objects.get(Inventory=self.Inventory.id)
            lastCount = stocktable.CountQty
            lt = stocktable.LastTransaction
        except ObjectDoesNotExist:
            lastCount = 0
            lt = 0
        totalInbound = Transaction.objects.filter(JobId__Type = 'I').filter(id__lte=self.id).filter(Inventory__id = self.Inventory.id).filter(id__gt=lt).filter(JobId__Warehouse='W').aggregate(q = Sum('Qty'))
        totalOutbound = Transaction.objects.filter(JobId__Type = 'O').filter(id__lte=self.id).filter(Inventory__id = self.Inventory.id).filter(id__gt=lt).filter(JobId__Warehouse='W').aggregate(p = Sum('Qty'))
        inbound = totalInbound['q']
        outbound = totalOutbound['p']
        if inbound is None:
            inbound = 0
        if outbound is None:
            outbound = 0
        stock = inbound - outbound + lastCount
        return stock

staff = [('w','warehouse'),('m','manager'),('c','cashier')]
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Name=models.CharField(max_length=25)
    Staff = models.CharField(max_length=1,choices=staff)
    

Account =[('C','Credit'),('D','Debit')]
class CashBook(models.Model):
    CreateDate = models.DateTimeField(auto_now_add=True)
    CreateBy = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    Description = models.CharField(max_length=30)
    Type = models.CharField(max_length=1,choices=Account,default='C')
    Amount = models.IntegerField()

    def __str__(self):
        return(str(self.CreateDate))

    @property
    def balance(self):
        credit = CashBook.objects.filter(id__lte=self.id,Type='C').aggregate(c=Sum('Amount'))
        debit = CashBook.objects.filter(id__lte=self.id,Type='D').aggregate(d=Sum('Amount'))
        if credit['c'] is None:
            c = 0
        else:
            c = credit['c']
        if debit['d'] is None:
            d = 0
        else:
            d = debit['d']
        balance = d - c
        return balance