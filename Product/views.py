from django.shortcuts import render,redirect
from django.http.response import HttpResponse, JsonResponse
from .models import Product
from .forms import ProductForm2,ProductPriceForm
from warehouse.forms import ProductForm
from django.contrib.auth.decorators import login_required
from warehouse.models import Transaction,StockCount
from django.db.models import Q,Sum,Count

# Create your views here.

@login_required(login_url='/login/')
def searchproduct(request):
    search_text = request.GET.get('search')

    if len(search_text) > 1:
        results = Product.objects.filter(Q(ProductName__icontains=search_text)|Q(Barcode__iexact=search_text)|Q(Tag__icontains=search_text))
    else:
        results =[]

    context = {"results": results}
    return render(request, 'warehouse/partials/select.html', context)


@login_required(login_url='/login/')
def editProduct(request,id):
    p = Product.objects.get(id=id)
    try:
        stocktable = StockCount.objects.get(Inventory=id)
        lastCount = stocktable.CountQty
        lt = stocktable.LastTransaction
        CountDate = stocktable.CountDate

    except ObjectDoesNotExist:
        lastCount = 0
        lt = 0
        CountDate = "-"

    transactions = Transaction.objects.filter(Inventory = id).filter(id__gt=lt).order_by('JobId')
    if request.method == 'POST':
        form = ProductForm2(request.POST or None,request.FILES,instance=p)
    else:
        form = ProductForm2(request.POST or None,instance=p)
    if form.is_valid():
        form.save()
        return redirect('productlist')
    context={'form':form,'CountDate':CountDate,'lastCount':lastCount,'transactions':transactions}
    return render(request,'warehouse/editproduct.html',context)

def EditPrice(request,id):
    p = Product.objects.get(id=id)
    form = ProductForm2(request.POST or None,instance = p)
    if form.is_valid():
        form.save()
        return HttpResponse('<h1>Update success</h1>')
    context = {'form':form}
    return render(request,'Product/partials/editprice.html',context)

@login_required(login_url='/login/')
def EditPriceModal(request,id):
    p = Product.objects.get(id=id)
    form = ProductForm2(request.POST or None,instance = p)
    if form.is_valid():
        form.save()
        return HttpResponse('<h1>Update success</h1>')
    context = {'form':form}
    return render(request,'Product/partials/editpricemodal.html',context)

