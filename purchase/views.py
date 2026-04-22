from django.shortcuts import get_object_or_404, redirect, render
from django.http.response import HttpResponse
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from Product.models import Product
from warehouse.models import Transaction,Job
from .models import Receiving,PurchaseOrder,PO_Transaction,HardCopy,Vendor,Account
from .forms import ReceivingForm,POForm,PTForm,VendorForm,CarryForm,AccountForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date

# Create your views here.
@login_required(login_url='/login/')
def Receive(request):
    receivelist = Receiving.objects.all().order_by('-id')
    form = ReceivingForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            form = ReceivingForm()
        context = {'receivelist':receivelist,'form':form}
        return render(request,'purchase/receive.html',context)
    else:
        context = {'receivelist':receivelist,'form':form}
        return render(request,'purchase/receive.html',context)

@login_required(login_url='/login/')
def NewReceive(request):
    receivelist = Receiving.objects.all().order_by('-id')
    form = ReceivingForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ReceivingForm()
    context = {'receivelist':receivelist,'form':form}
    return render(request,'purchase/partials/receiveform.html',context)

@login_required(login_url='/login/')
def PO(request):
    form = POForm(request.POST or None)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.Create_By = request.user
        temp.save()
        return redirect('PD',id=PurchaseOrder.objects.last().id)
    context = {'form':form}
    return render(request,'purchase/PO.html',context)

@login_required(login_url='/login/')
def PO_List(request):
    PO_list = PurchaseOrder.objects.all().order_by('-OrderDate')
    vendor = Vendor.objects.all().order_by('Name')
    page = request.GET.get('page',1)
    paginator = Paginator(PO_list,30)
    last = paginator.num_pages
    try:
        PO = paginator.page(page)
    except PageNotAnInteger:
        PO = paginator.page(1)
    except EmptyPage:
        PO = paginator.page(paginator.num_pages)
    context={'PO': PO,'last':last,'vendors':vendor}

    return render(request,'purchase/PO_list.html',context)

@login_required(login_url='/login/')
def PO_List_Filter(request):
    v = request.GET.get('vendor')
    page = request.GET.get('page',1)
    PO_list = PurchaseOrder.objects.filter(Supplier_id=v).order_by('-OrderDate')

    paginator = Paginator(PO_list,30)
    last = paginator.num_pages
    try:
        PO = paginator.page(page)
    except PageNotAnInteger:
        PO = paginator.page(1)
    except EmptyPage:
        PO = paginator.page(paginator.num_pages)
    context={'PO': PO,'last':last,'vendor':v}

    return render(request,'purchase/partials/POlist.html',context)

@login_required(login_url='/login/')
def PO_Detail(request,id):
    PO = PurchaseOrder.objects.get(id=id)
    form = PTForm(request.POST or None,initial={'PO':id})
    accounts = Account.objects.filter(Vendor = PO.Supplier)
    
    # Get next and previous POs for the same vendor
    vendor_pos = PurchaseOrder.objects.filter(Supplier=PO.Supplier).order_by('-OrderDate')
    po_list = list(vendor_pos)
    current_index = po_list.index(PO)
    
    next_po = po_list[current_index - 1] if current_index > 0 else None
    prev_po = po_list[current_index + 1] if current_index < len(po_list) - 1 else None
    
    if form.is_valid():
        form.save()
        form = PTForm(initial={'PO':id})
    context = {'PO':PO,'form':form,'accounts':accounts,'next_po':next_po,'prev_po':prev_po}
    return render(request,'purchase/PD.html',context)

@login_required(login_url='/login/')
def newtransaction(request,id):
    PO = PurchaseOrder.objects.get(id=id)
    form = PTForm(request.POST or None,initial={'PO':id})
    if form.is_valid():
        form.save()
        if form.instance.Price != form.instance.Inventory.BuyingPrice:
            if form.instance.Price != 0:
                newprice = Product.objects.get(id=form.instance.Inventory.id)
                newprice.BuyingPrice = form.instance.Price
                newprice.save()
                message = str(form.instance.Inventory) +' price is change to ' + str(form.instance.Price)
            else:
                message = ''
        else:
            message = ''
        form = PTForm(initial={'PO':id})
        redirect('PD',id=id)

    context={'PO':PO,'form':form,'message':message}
    return render(request,'purchase/partials/transactiontable.html',context)

@login_required(login_url='/login/')
def deletetransaction(request,id):
    tr = PO_Transaction.objects.filter(id=id)
    if request.method == 'POST':
        t = PO_Transaction.objects.get(id=id)
        t.delete()
    return HttpResponse('')


@login_required(login_url='/login/')
def geteditform(request,id):
    t = PO_Transaction.objects.get(id=id)
    form = PTForm(request.POST or None,instance= t)
    PO = PurchaseOrder.objects.get(id=t.PO.id)
    if request.method == "POST":
        check = request.POST.get('update')
        if form.is_valid():
            check = request.POST.get('update')
            if check=='on':
                product = Product.objects.get(id=form.instance.Inventory.id)
                if form.instance.Price > 0:
                    product.BuyingPrice = form.instance.Price
                product.save()
            form.save()
            form = PTForm()
        context={'PO':PO,'form':form}
        return render(request,'purchase/partials/transactiontable.html',context)
    else:
        context={'PO':PO,'form':form}
        return render(request,'purchase/partials/transaction_edit.html',context)

@login_required(login_url='/login/')
def getsearchresult(request,id):
    PO = PurchaseOrder.objects.get(id=id)
    search_text = request.GET.get('search')
    if len(search_text) > 1:
        results = Product.objects.filter(Q(ProductName__icontains=search_text)|Q(Barcode__iexact=search_text)|Q(Tag__icontains=search_text)).order_by('ProductName')
    else:
        results =[]

    context = {'results':results,'PO':PO}
    return render(request,'purchase/partials/searchresult.html',context)

@login_required(login_url='/login/')
def filtertransaction(request,id,p):
    PL = Product.objects.get(id=p)
    PO = PurchaseOrder.objects.get(id=id)
    form = PTForm(request.POST or None,initial={'PO':id,'Quantity':1,'Inventory':PL,'Price':PL.BuyingPrice})
    context = {'PO':PO,'form':form}
    return render(request,'purchase/partials/newtransactionform.html',context)

@login_required(login_url='/login/')
def newvendor(request):
    form = VendorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('purchaseindex')
    context = {'form':form}
    return render(request,'purchase/vendor.html',context)

@login_required(login_url='/login/')
def newcarry(request):
    form = CarryForm(request.POST or None)
    if form.is_valid():
        form.save()
    context = {'form':form}
    return render(request,'purchase/carry.html',context)

@login_required(login_url='/login/')
def ImportFromJob(request,pid):
    jid = request.POST.get('JobID')
    form = PTForm(request.POST or None,initial={'PO':pid})
    tr = Transaction.objects.filter(JobId = jid)
    P = PurchaseOrder.objects.get(id=pid)

    for t in tr:
        entry = PO_Transaction(
            PO = P,
            Inventory = t.Inventory,
            Quantity = t.Qty,
            Price = t.Inventory.BuyingPrice
        )
        entry.save()
    PO = PurchaseOrder.objects.get(id=pid)
    context={'PO':PO,'form':form}
    return render(request,'purchase/partials/transactiontable.html',context)

@login_required(login_url='/login/')
def UpdateBuyingPrice(request,id): 
    p = request.GET.get('Price')
    product = Product.objects.get(id=id)
    #product.update(BuyingPrice=p)
    return HttpResponse("<p class='text-success'>Price successfully update</p>")

@login_required(login_url='/login/')
def upload(request,id):
    PO = PurchaseOrder.objects.get(id=id)
    if request.method == "POST":
        images = request.FILES.getlist('images')
    for image in images:
        HardCopy.objects.create(Photo=image,PO=PO)
    return redirect('PD',id=id)

@login_required(login_url='/login/')
def PurchaseInvoice(request,id,p):
    PO = PurchaseOrder.objects.get(id=id)
    context = {'PO' : PO,'p':p}
    return render(request,'purchase/P_Invoice.html',context)

@login_required(login_url='/login/')
def ShopReceive(request):
    jobs = Job.objects.filter(Warehouse='S').order_by('-id')[:30]
    context={'jobs': jobs}
    return render(request,'purchase/shopreceive.html',context)

@login_required(login_url='/login/')
def GetAccount(request):
    form = AccountForm(request.POST or None,request.FILES)
    account = Account.objects.all().order_by('id')
    v = Vendor.objects.all().order_by('Name')
    if form.is_valid():
        vendor = form.instance.Vendor
        form.save()
        form = AccountForm()
        account = Account.objects.filter(Vendor=vendor).order_by('id')
    context = {'form':form,'Vendors':v,'accounts':account}
    return render(request,'purchase/account.html',context)

@login_required(login_url='/login/')
def Account_List_Filter(request):
    v = request.GET.get('vendor')
    account = Account.objects.filter(Vendor=v).order_by('id')
    context = {'accounts':account}
    return render(request,'purchase/partials/accountlist.html',context)

@login_required(login_url='/login/')
def PostAccount(request,id):
    Order = PurchaseOrder.objects.get(id=id)
    Order.Status='C'
    Order.save()
    
    a = Account(
        AccountDate = Order.OrderDate,
        Vendor = Order.Supplier,
        Amount = Order.Subtotal,
        Note = 'PO-' + str(Order.id),
        Type = 'C'
    )
    a.save()
    return redirect('PD',Order.id)

def purchasehistory(request,id):
    p = Product.objects.get(id=id)
    transactions = PO_Transaction.objects.filter(Inventory = p).order_by('-id')[:50]
    context = {'product':p,'transactions':transactions}
    return render(request,'purchase/partials/purchasehistory.html',context)
