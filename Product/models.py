from io import BytesIO
from django.db import models
from warehouse.models import StockCount,Transaction
#from purchase.models import PO_Transaction
from django.db.models import Sum,F
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from math import ceil
from PIL import Image as img
from simple_history.models import HistoricalRecords
from PIL import Image, ImageOps
from django.core.files import File
from imagekit.models import ProcessedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
# Create your models here.

class Unit(models.Model):
    Unit = models.CharField(max_length=15)

    def __str__(self):
        return self.Unit

class Category(models.Model):
    Name = models.CharField(max_length=20)
    Code = models.CharField(max_length=3)

    def __str__(self):
        return self.Name

Currency = [('B','Baht'),('K','Kyat')]

Status = [('A','Available'),('N','Not available')]

class Product(models.Model):
    ProductName = models.CharField(max_length=50)
    Barcode = models.CharField(max_length=15,null=True,blank=True)
    # Image = models.ImageField(default="product_photo/default.png",upload_to='product_photo')
    Image = ProcessedImageField(upload_to='product_photo',
                                           default = "product_photo/default.png",
                                           processors=[ResizeToFill(1080, 1080)],
                                           format='JPEG',
                                           options={'quality': 90})
    Tag = models.CharField(max_length=100,null=True,blank=True)
    Minimum = models.IntegerField(null=True,blank=True)
    Unit = models.ForeignKey(Unit,on_delete=models.PROTECT,default=1)
    BuyingPrice = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,default=0)
    Cost = models.IntegerField(null=True,blank=True,default=0)
    Expected_Profit = models.IntegerField(null=True,blank=True)
    Category = models.ForeignKey(Category,on_delete=models.PROTECT,default='1')
    Base_Currency = models.CharField(max_length=4,choices = Currency,default='B')
    Status = models.CharField(max_length=1,choices=Status,default='A')
    MemberPrice = models.IntegerField(null=True,blank=True,default=0)
    RetailPrice = models.IntegerField(null=True,blank=True,default=0)
    history = HistoricalRecords()

    class Meta:
        ordering = ['ProductName']    

    def __str__(self):
        return self.ProductName

    def profit(self):
        p = self.RetailPrice(self.BuyingPrice + self.Cost)
        return str(p)

    def sellingprice(self):
        if self.BuyingPrice is None:
            buying = 0
        if self.Cost is None:
            cost = 0
        if self.Expected_Profit is None:
            profit = 0
        price = buying+cost+profit

    @property    
    def wh_stock(self):
         try:
             stocktable = StockCount.objects.get(Inventory=self.id)
             lastCount = stocktable.CountQty
             lt = stocktable.LastTransaction
         except ObjectDoesNotExist:
             lastCount = 0
             lt = 0
         totalInbound = Transaction.objects.filter(JobId__Type = 'I').filter(Inventory__id = self.id).filter(id__gt=lt).filter(JobId__Warehouse='W').aggregate(q = Sum('Qty'))
         #totalOutbound = Transaction.objects.filter(JobId__Type = 'O').filter(Inventory__id = self.id).filter(id__gt=lt).filter(JobId__Warehouse='W').aggregate(p = Sum('Qty'))
         totalOutbound = self.so_transaction_set.all().filter(Inventory__id=self.id).aggregate(p=Sum('Quantity'))
         #totalPurchase = PO_Transaction.objects.filter(Inventory__id=self.id).aggregate(p=Sum('Quantity'))
         totalPurchase = self.po_transaction_set.all().aggregate(p=Sum('Quantity'))
         inbound = totalInbound['q']
         outbound = totalOutbound['p']
         purchase = totalPurchase['p']
         if inbound is None:
             inbound = 0
         if outbound is None:
             outbound = 0
         if purchase is None:
             purchase = 0
         stock = inbound - outbound + lastCount + purchase
         return stock

    @property    
    def wh2_stock(self):
         try:
             stocktable = StockCount.objects.get(Inventory=self.id)
             lastCount = stocktable.CountQty
             lt = stocktable.LastTransaction
         except ObjectDoesNotExist:
             lastCount = 0
             lt = 0
         totalInbound = Transaction.objects.filter(JobId__Type = 'I').filter(Inventory__id = self.id).filter(id__gt=lt).filter(JobId__Warehouse='2').aggregate(q = Sum('Qty'))
         totalOutbound = Transaction.objects.filter(JobId__Type = 'O').filter(Inventory__id = self.id).filter(id__gt=lt).filter(JobId__Warehouse='2').aggregate(p = Sum('Qty'))
         inbound = totalInbound['q']
         outbound = totalOutbound['p']
         if inbound is None:
             inbound = 0
         if outbound is None:
             outbound = 0
         stock = inbound - outbound
         return stock

    
    @property    
    def shop_stock(self):
         try:
             stocktable = StockCount.objects.get(Inventory=self.id)
             lastCount = stocktable.CountQty
             lt = stocktable.LastTransaction
         except ObjectDoesNotExist:
             lastCount = 0
             lt = 0
         totalInbound = Transaction.objects.filter(JobId__Type = 'I').filter(Inventory__id = self.id).filter(id__gt=lt).filter(JobId__Warehouse='S').aggregate(q = Sum('Qty'))
         totalOutbound = Transaction.objects.filter(JobId__Type = 'O').filter(Inventory__id = self.id).filter(id__gt=lt).filter(JobId__Warehouse='S').aggregate(p = Sum('Qty'))
         inbound = totalInbound['q']
         outbound = totalOutbound['p']
         if inbound is None:
             inbound = 0
         if outbound is None:
             outbound = 0
         stock = inbound - outbound
         return stock

    @property
    def RetailBaht(self):
        rate = CurrencyRate.objects.last().Rate/100
        list = self.RetailPrice
        if list is None:
            retail_price = 0
        else:
            if self.Base_Currency == 'K':
                retail_price = int(list * rate)
            else:
                retail_price = list
        return retail_price

    @property
    def MemberBaht(self):
        rate = CurrencyRate.objects.last().Rate/100
        list = self.MemberPrice
        if list is None:
            member_price = 0
        else:
            if self.Base_Currency == 'K':
                member_price = int(list * rate)
            else:
                member_price = list
        return member_price

    @property
    def RetailKyat(self):
        rate = CurrencyRate.objects.last().Rate/100
        list = self.RetailPrice
        if list is None:
            retail_price = 0
        else:
            if self.Base_Currency == 'B':
                retail_price = ceil(list /rate / 50) * 50
            else:
                retail_price = list
        return retail_price

    @property
    def MemberKyat(self):
        rate = CurrencyRate.objects.last().Rate/100
        list = self.MemberPrice
        if list is None:
            member_price = 0
        else:
            if self.Base_Currency == 'K':
                member_price = list
            else:
                member_price = ceil(list /rate / 50) * 50
        return member_price

    def mbprice(self):
        buying = self.BuyingPrice
        if self.BuyingPrice == None:
            buying = 0
        if self.Cost == None:
            cost = 0
        else:
            cost = self.Cost
        if self.Expected_Profit == None:
            profit = 0
        else:
            profit = self.Expected_Profit
        mbprice = buying + cost + profit
        return mbprice

    def rtprice(self):
        rtprice = self.mbprice() + 5
        return rtprice

    
    # def save(self, *args, **kwargs):
    #   im = Image.open(self.Image)
    #   # Convert Image to RGB color mode
    #   im = im.convert('RGB')
    #   # auto_rotate image according to EXIF data
    #   im = ImageOps.exif_transpose(im)
    #   # save image to BytesIO object
    #   im_io = BytesIO() 
    #   # save image to BytesIO object
    #   im.save(im_io, 'JPEG', quality=70) 
    #   # create a django-friendly Files object
    #   new_image = File(im_io, name=self.Image.name)
    #   # Change to new image
    #   self.Image = new_image
    #   super().save(*args, **kwargs)

     

class CurrencyRate(models.Model):
    CreateDate = models.DateTimeField(auto_now_add=True)
    Rate = models.FloatField()
    Note = models.CharField(max_length=20,blank=True,null=True)