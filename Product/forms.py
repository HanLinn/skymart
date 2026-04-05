from django import forms
from django.forms import ModelForm, widgets
from .models import Product

class ProductForm2(ModelForm):
    class Meta:
        model = Product
        fields = [
            'BuyingPrice',
            'Cost',
            'Expected_Profit',
            'MemberPrice',
            'RetailPrice'
        ]

        widgets = {
            'BuyingPrice' : forms.NumberInput(attrs={'class':'form-control','id':'BuyingPrice','placeholder':'BuyingPrice'}),
            'Cost' : forms.NumberInput(attrs={'class':'form-control','id':'Cost','placeholder':'Cost'}),
            'Expected_Profit' :forms.NumberInput(attrs={'class':'form-control','id':'Expected_Profit','placeholder':'Expected_Profit'}),
            'MemberPrice' :forms.NumberInput(attrs={'class':'form-control','id':'MemberPrice','placeholder':'MemberPrice'}),
            'RetailPrice' :forms.NumberInput(attrs={'class':'form-control','id':'RetailPrice','placeholder':'RetailPrice'})
        }

class ProductPriceForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'ProductName',
            'Base_Currency',
            'BuyingPrice',
            'Cost',
            'Expected_Profit',
            'MemberPrice',
            'RetailPrice'
        ]

        widgets = {
            'ProductName' : forms.TextInput(attrs={'class':'form-control'}),
            'Base_Currency' : forms.Select(attrs={'class':'form-control'}),
            'BuyingPrice' : forms.NumberInput(attrs={'class':'form-control'}),
            'Cost' : forms.NumberInput(attrs={'class':'form-control'}),
            'Expected_Profit' :forms.NumberInput(attrs={'class':'form-control'}),
            'MemberPrice' :forms.NumberInput(attrs={'class':'form-control'}),
            'RetailPrice' :forms.NumberInput(attrs={'class':'form-control'})
        }

