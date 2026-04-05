from django import forms
from django.forms import ModelForm, widgets
from .models import StockCount,Job, Transaction,Related,CashBook
from Product.models import Product

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'ProductName',
            'Barcode',
            'Category',
            'Unit',
            'Image',
            'Tag',
            'Minimum',
            'Base_Currency',
            'MemberPrice',
            'RetailPrice'

        ]

        widgets = {
            'ProductName' : forms.TextInput(attrs={'class':'form-control','type':'search','hx-get':'/wh/similarproduct/','hx-trigger':'keyup changed delay:500ms, search','hx-target':'#similar','id':'ProductName','placeholder':'Product Name'}),
            'Barcode' : forms.TextInput(attrs={'class':'form-control','id':'barcode','placeholder':'Barcode'}),
            'Category' : forms.Select(attrs={'class':'form-select','id':'category','placeholder':'Category'}),
            'Unit' : forms.Select(attrs={'class':'form-select','id':'unit','placeholder':'Unit'}),
            'Image' : forms.ClearableFileInput(attrs={'class':'form-control','id':'image'}),
            'Tag' : forms.TextInput(attrs={'class':'form-control','id':'tag','placeholder':'Tag'}),
            'Minimum' : forms.NumberInput(attrs={'class':'form-control','id':'minimum','placeholder':'Minimum'}),
            'Base_Currency' : forms.Select(attrs={'class':'form-select','id':'Base_Currency','placeholder':'Base_Currency'}),
            'MemberPrice' : forms.NumberInput(attrs={'class':'form-control','id':'MemberPrice','placeholder':'MemberPrice'}),
            'RetailPrice' : forms.NumberInput(attrs={'class':'form-control','id':'RetailPrice','placeholder':'RetailPrice'})
        }

class StockCountForm(ModelForm):
    class Meta:
        model = StockCount
        fields = [
            'Inventory',
            'CountQty',
            'LastTransaction',
            'Note'
        ]

        widgets = {
            'Inventory' : forms.Select(attrs={'class':'form-select'}),
            'CountQty' : forms.NumberInput(attrs={'class':'form-control'}),
            'LastTransaction' : forms.HiddenInput(attrs={'class':'form-control'}),
            'Note' : forms.TextInput(attrs={'class':'form-control'}),
        }

class JobCompleteForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            'Note',
            'Photo',
            'Status',
            'Vehicle',
            'OperateBy'
        ]

        widgets = {
            'Note' : forms.TextInput(attrs={'class':'form-control'}),
            'Photo' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'Status' : forms.Select(attrs={'class':'form-select'}),
            'Vehicle' : forms.TextInput(attrs={'class' : 'form-control'}),
            'OperateBy' : forms.HiddenInput(),
            
        }

class NewJobForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            'Warehouse',
            'Type',
            'Status',
            'Agent',
            'Vehicle',
            'Note',
            'CreateBy',
            'CustomerOrVendor'
        ]

        widgets = {
            'Warehouse' : forms.Select(attrs={'class':'form-select','id':'Warehouse'}),
            'Type' : forms.Select(attrs={'class':'form-select','id':'Type'}),
            'Status' : forms.Select(attrs={'class':'form-select','id':'Status'}),
            'Agent' : forms.TextInput(attrs={'class' : 'form-control','id':'Agent','placeholder':'Agent'}),
            'Vehicle' : forms.TextInput(attrs={'class' : 'form-control','id':'Vehicle','placeholder':'Vehicle'}),
            'Note' : forms.TextInput(attrs={'class' : 'form-control','id':'Note','placeholder':'Note'}),
            'CreateBy' : forms.HiddenInput(),
            'CustomerOrVendor' : forms.Select(attrs={'class':'form-select','id':'CustomerOrVendor'})
        }

class NewTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ('__all__')

        widgets = {
            'Inventory' : forms.Select(attrs={'class':'form-select mr-1 me-1','id':'inventory'}),
            'Qty' : forms.NumberInput(attrs={'class':'form-control mr-1 me-1','placeholder':'Qty'}),
            'JobId' : forms.HiddenInput(attrs={'class':'form-control disabled'})
        }

#    def clean(self):
#        super(NewTransactionForm,self).clean()
#       Inventory = self.cleaned_data.get('Inventory')
#        stock = Inventory.stock()
#        Qty = self.cleaned_data.get('Qty')

#        if Qty > stock:
#            self.errors['Qty'] = self.error_class(['Available quantity:'+ str(Inventory.stock())])

#        return self.cleaned_data

class RelatedForm(ModelForm):
    class Meta:
        model = Related
        fields =['RelatedName']

        widgets = {
            'RelatedName' : forms.TextInput(attrs={'class' : 'form-control','id':'RelatedName','placeholder':'Customer or Vendor'}),
        }

class CashBookForm(ModelForm):
    class Meta:
        model = CashBook
        fields = ['Type','Description','Amount']

        widgets = {
            'Type' : forms.Select(attrs={'class':'form-select','placeholder':'Type','id':'Type'}),
            'Description' : forms.TextInput(attrs={'class':'form-control','placeholder':'Description','id':'Description'}),
            'Amount' : forms.NumberInput(attrs={'class':'form-control','placeholder':'Amount','id':'Amount'}),
        }