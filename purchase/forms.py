from django import forms
from django.forms import ModelForm, widgets
from .models import Receiving,PurchaseOrder,PO_Transaction,Vendor,Carry,HardCopy,Account

class ReceivingForm(ModelForm):
    class Meta:
        model = Receiving
        fields = ['Inventory','Quantity','Note','Destination','Vendor','CarryBy']

        widgets = {
            'Inventory' : forms.Select(attrs={'class':'form-control mr-1 ml-1','id':'Inventory'}),
            'Quantity' : forms.NumberInput(attrs={'class':'form-control mr-1 ml-1'}),
            'Note' : forms.TextInput(attrs={'class':'form-control mr-1 ml-1'}),
            'Destination' : forms.Select(attrs={'class':'form-control mr-1 ml-1'}),
            'Vendor' : forms.Select(attrs={'class':'form-control mr-1 ml-1'}),
            'CarryBy' : forms.Select(attrs={'class':'form-control mr-1 ml-1'})
        }

class POForm(ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['OrderDate','Supplier','Note','Create_By','Currency']

        widgets = {
            'OrderDate' : forms.TextInput(attrs={'class':'form-control','type':'date','placeholder':'mm/dd/yyyy','style':'min-height: 2.5rem;','id':'OrderDate'}),
            'Supplier' : forms.Select(attrs={'class':'form-control','id':'Supplier','placeholder':'Supplier'}),
            'Currency' : forms.Select(attrs={'class':'form-control','id':'Currency','placeholder':'Currency'}),
            'Note' : forms.TextInput(attrs={'class':'form-control','id':'Note','placeholder':'Note'}),
            'Create_By': forms.HiddenInput()
        }


class PTForm(ModelForm):
    class Meta:
        model = PO_Transaction
        fields = ['PO','Inventory','Quantity','Price']

        widgets = {
            'PO' : forms.HiddenInput(attrs={'class' : 'form-control'}),
            'Inventory' : forms.HiddenInput(attrs={'class':'form-control','placeholder':'product','id':'inventory'}),
            'Quantity' : forms.NumberInput(attrs={'class':'form-control','placeholder':'Quantity','id':'Quantity'}),
            'Price' : forms.NumberInput(attrs={
                'class':'form-control',
                'placeholder':'Price',
                'id':'Price'
                })
        }

class VendorForm(ModelForm):
    class Meta:
        model = Vendor
        fields = ['Name','Contact']

        widgets = {
            'Name' : forms.TextInput(attrs={'class' : 'form-control','id':'Name','placeholder':'Name'}),
            'Contact' : forms.TextInput(attrs={'class':'form-control','id':'Contact','placeholder':'Contact'}),
        }

class CarryForm(ModelForm):
    class Meta:
        model = Vendor
        fields = ['Name','Contact']

        widgets = {
            'Name' : forms.TextInput(attrs={'class' : 'form-control','id':'Name','placeholder':'Name'}),
            'Contact' : forms.TextInput(attrs={'class':'form-control','id':'Contact','placeholder':'Contact'}),
        }

class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['Type','AccountDate','Vendor','Amount','Note','Photo']

        widgets = {
            'Type' : forms.Select(attrs={'class' : 'form-control'}),
            'AccountDate' : forms.TextInput(attrs={'class':'form-control','type':'date','placeholder':'MM/DD/YYYY','style':'min-height: 2.5rem;','id':'AccountDate'}),
            'Vendor' : forms.Select(attrs={'class' : 'form-control','id':'Vendor','placeholder':'Vendor'}),
            'Amount' : forms.NumberInput(attrs={'class' : 'form-control','id':'Amount','placeholder':'Amount'}),
            'Note' : forms.TextInput(attrs={'class':'form-control','id':'Note','placeholder':'Note'}),
            'Photo' : forms.ClearableFileInput(attrs={'class':'form-control','id':'Photo'}),
        }

