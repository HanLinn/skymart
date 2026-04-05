from django import forms
from django.forms import ModelForm, widgets
from . models import buyer,SalesOrder,SO_Transaction
from Product.models import CurrencyRate

class BuyerForm(ModelForm):
    class Meta:
        model = buyer
        fields = ['Customer_Name','Contact']

        widgets = {
            'Customer_Name' : forms.TextInput(attrs={'class':'form-control','id':'Customer_Name','placeholder':'Customer_Name'}),
            'Contact' : forms.TextInput(attrs={'class':'form-control','id':'Contact','placeholder':'Contact'}),
        }

class SalesOrderForm(ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['Customer','Currency','Note','Status','Pay']

        widgets = {
            'Customer' : forms.Select(attrs={'class':'form-control','id':'Customer','placeholder':'Customer'}),
            'Currency' : forms.Select(attrs={'class':'form-control','id':'Currency','placeholder':'Currency'}),
            'Note' : forms.TextInput(attrs={'class':'form-control','id':'Note','placeholder':'Note'}),
            'Status' : forms.Select(attrs={'class':'form-control','id':'Status','placeholder':'Status'}),
            'Pay' : forms.NumberInput(attrs={'class':'form-control','id':'Pay','placeholder':'Pay'}),
        }

class STForm(ModelForm):

    class Meta:
        model = SO_Transaction
        fields = ['SO','Inventory','Quantity','Price']

        widgets = {
            'SO' : forms.HiddenInput(attrs={'class' : 'form-control'}),
            'Inventory' : forms.HiddenInput(attrs={'class':'form-control','placeholder':'product','id':'inventory'}),
            'Quantity' : forms.NumberInput(attrs={'class':'form-control','placeholder':'Quantity','id':'Quantity'}),
            'Price' : forms.NumberInput(attrs={'class':'form-control','placeholder':'Price','id':'Price'})
        }


class CurrencyRateForm(ModelForm):
    class Meta:
        model = CurrencyRate
        fields = ['Rate','Note']

        widgets = {
            'Rate' : forms.NumberInput(attrs={'class':'form-control','id':'Rate','placeholder':'Rate'}),
            'Note' : forms.TextInput(attrs={'class':'form-control','id':'Note','placeholder':'Note'}),
        }

class CustomerForm(ModelForm):
    class Meta:
        model = buyer
        fields = ['Customer_Name','Contact','Pricelist']

        widgets = {
            'Customer_Name' : forms.TextInput(attrs={'class':'form-control','id':'Customer_Name','placeholder':'Customer_Name'}),
            'Contact' : forms.TextInput(attrs={'class':'form-control','id':'Contact','placeholder':'Contact'}),
            'Pricelist' : forms.Select(attrs={'class':'form-control','id':'Pricelist','placeholder':'Pricelist'})
        }