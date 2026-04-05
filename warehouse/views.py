from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from . models import Job, Related, Transaction,StockCount,CashBook
from django.db.models import Q,Sum,Count
from . forms import ProductForm, RelatedForm,StockCountForm,JobCompleteForm,NewJobForm,NewTransactionForm,CashBookForm
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .resources import ProductResource
from Product.models import Product
from sales.models import SO_Transaction
from openpyxl import Workbook


# Create your views here.
@login_required(login_url='/login/')
def index(request):
    job_list = Job.objects.filter(Warehouse='W').order_by('-id')
    page = request.GET.get('page',1)
    paginator = Paginator(job_list,30)
    last = paginator.num_pages
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)
    context={'jobs': jobs,'last':last}
    return render(request,'warehouse/index.html',context)


@login_required(login_url='/login/')
def jobdetail(request,id):
    J = Job.objects.get(id=id)
    product = Product.objects.all()
    form = NewTransactionForm(request.POST or None,initial={'JobId':id})
    if form.is_valid():
        form.save()
        redirect('jobdetail',id=id)
    context={'J':J,'form':form,'product':product}
    return render(request,'warehouse/JobDetail.html',context)

@login_required(login_url='/login/')
def jobprint(request,id):
    job = Job.objects.filter(id=id)
    J = Job.objects.get(id=id)
    J.Status = 'C'
    J.OperateBy = request.user
    J.save()
    tran = Transaction.objects.filter(JobId=id)
    context={'J':J,'job':job,'trans':tran}
    return render(request,'warehouse/JobPrint.html',context)

@login_required(login_url='/login/')
def completejob(request,id):
    job = Job.objects.get(id=id)
    if request.method == 'POST':
        form = JobCompleteForm(request.POST or None,request.FILES,instance=job)
    else:
        form = JobCompleteForm(request.POST or None,instance=job)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.Status = 'C'
        temp.OperateBy = request.user
        temp.save()
        return redirect('index')
    context = {'form' : form}
    return render(request,'warehouse/completejob.html',context)
        
@login_required(login_url='/login/')
def newProduct(request):
    form = ProductForm(request.POST or None,request.FILES)
    if form.is_valid():
        form.save()
        return redirect('index')
    context={'form':form}
    return render(request,'warehouse/newproduct.html',context)

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

    transactions = Transaction.objects.filter(Inventory = id).filter(id__gt=lt).filter(JobId__Warehouse='W').order_by('JobId')
    if request.method == 'POST':
        form = ProductForm(request.POST or None,request.FILES,instance=p)
    else:
        form = ProductForm(request.POST or None,instance=p)
    if form.is_valid():
        form.save()
        return redirect('mainindex')
    context={'form':form,'CountDate':CountDate,'lastCount':lastCount,'transactions':transactions}
    return render(request,'warehouse/editproduct.html',context)

@login_required(login_url='/login/')
def stocktable(request,id):
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
    wh = request.GET.get('wh')
    if wh == None:
        wh='W'
    transactions = Transaction.objects.filter(Inventory = id).filter(id__gt=lt).filter(JobId__Warehouse=wh).order_by('JobId').order_by('-id')
    context={'CountDate':CountDate,'lastCount':lastCount,'transactions':transactions,'product':p}
    return render(request,'warehouse/partials/stocktable.html',context)

@login_required(login_url='/login/')
def search(request):
    kw = request.GET.get('kw')
    product = Product.objects.filter(Q(ProductName__icontains=kw)|Q(Tag__icontains=kw)|Q(Barcode__icontains=kw)).exclude(Status='N')
    customer = Related.objects.filter(RelatedName__icontains=kw)
    context={'product':product,'customer':customer}
    if kw.startswith('J-'):
        j = kw[2:]
        job = Job.objects.filter(id = j)
        context={'product':product,'customer':customer,'job':job}
    return render(request,'warehouse/result.html',context)

@login_required(login_url='/login/')
def productlist(request):
    kw = (request.GET.get('kw') or '').strip()
    page = request.GET.get('page', 1)

    products = Product.objects.all().order_by('ProductName')
    if kw:
        products = products.filter(
            Q(ProductName__icontains=kw) |
            Q(Tag__icontains=kw) |
            Q(Barcode__icontains=kw)
        )

    paginator = Paginator(products, 300)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {'products': products, 'kw': kw}
    return render(request,'warehouse/productlist.html',context)

@login_required(login_url='/login/')
def productlist_export(request):
    kw = (request.GET.get('kw') or '').strip()

    products = Product.objects.all().order_by('ProductName')
    if kw:
        products = products.filter(
            Q(ProductName__icontains=kw) |
            Q(Tag__icontains=kw) |
            Q(Barcode__icontains=kw)
        )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Product List'
    sheet.append(['Name', 'Code', 'Buying', 'Kyat', 'Baht'])

    for product in products:
        sheet.append([
            product.ProductName,
            product.Barcode or '',
            float(product.BuyingPrice or 0),
            float(product.RetailKyat or 0),
            float(product.RetailBaht or 0),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="product_list.xlsx"'
    workbook.save(response)
    return response

@login_required(login_url='/login/')
def stockcount(request,id):
    try:
        inventory = StockCount.objects.get(Inventory = id)
        form = StockCountForm(request.POST or None,instance = inventory)
    except ObjectDoesNotExist:
        form = StockCountForm(request.POST or None,initial={'Inventory':id})

    if form.is_valid():
        temp = form.save(commit=False)
        lt = Transaction.objects.last()
        temp.LastTransaction = lt.id
        #temp.LastTransaction = 0
        temp.save()
        return HttpResponse('<h1>stock count updated</h1>')
    inventory = Product.objects.get(id=id)
    productname = inventory.ProductName
    context={'form':form,'productname':productname}
    return render(request,'warehouse/stockcount.html',context)

@login_required(login_url='/login/')
def NewJob(request):
    form = NewJobForm(request.POST or None)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.CreateBy = request.user

        temp.save()
        #need to find new solution on future
        job = Job.objects.last()
        i = job.id
        return redirect('jobdetail',id=i)
    context = {'form' : form}
    return render(request,'warehouse/newjob.html',context)

@login_required(login_url='/login/')
def EditJob(request,id):
    J = Job.objects.get(id=id)
    form = NewJobForm(request.POST or None,instance = J)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.CreateBy = request.user

        temp.save()
        return redirect('jobdetail',id=id)
    context = {'form' : form }
    return render(request,'warehouse/newjob.html',context)

@login_required(login_url='/login/')
def DeleteJob(request,id):
    J = Job.objects.get(id=id)
    if request.method == 'POST':
        J.delete()
        jobs = Job.objects.all().order_by('-id')[:30]
        return render(request,'warehouse/index.html',context)

@login_required(login_url='/login/')
def check(request,id):
    kw = request.GET.get('k')
    t = Transaction.objects.filter(JobId = id)
    if Transaction.objects.filter(JobId = id,Inventory__Barcode=kw):
        list = Transaction.objects.filter(JobId = id,Inventory__Barcode=kw).aggregate(q= Sum('Qty'))
        #context = {'result':list}
        #data = dict()
        #data['html'] = render_to_string('warehouse/partial_result.html',context,request=request)
        return HttpResponse("<p>Product Exist_" + str(list['q']) +'</p>')
        return HttpResponse('Exist_(' + str(list[0].Qty)+')')
        #return JsonResponse(a)

    else:
        return HttpResponse('Not Exist')

@login_required(login_url='/login/')
def searchproduct(request):
    search_text = request.GET.get('search')

    if len(search_text) > 1:
        results = Product.objects.filter(Q(ProductName__icontains=search_text)|Q(Barcode__iexact=search_text)|Q(Tag__icontains=search_text)|Q(Status='Available')).order_by('ProductName')
    else:
        results =[]

    context = {"results": results}
    return render(request, 'warehouse/partials/select.html', context)

@login_required(login_url='/login/')
def newtransaction(request,id):
    J = Job.objects.get(id=id)
    form = NewTransactionForm(request.POST or None,initial={'JobId':id})
    if form.is_valid():
        form.save()
        form = NewTransactionForm(initial={'JobId':id})
        redirect('jobdetail',id=id)
    context={'J':J,'form':form}
    return render(request,'warehouse/partials/transactiontable.html',context)

@login_required(login_url='/login/')
def getproductid(request,id):
    product = Product.objects.get(id=id)
    
    return HttpResponse("<option value='" + str(product.id) + "'>"+ product.ProductName +"</option>")

@login_required(login_url='/login/')
def geteditform(request,id):
    tr = Transaction.objects.get(id=id)
    form = NewTransactionForm(request.POST or None,instance=tr)
    if form.is_valid():
        form.save()
    if request.method == 'POST':
        J = Job.objects.get(id=tr.JobId.id)
        form=NewTransactionForm(initial={'JobId':tr.JobId.id})
        context = {'J':J,'form':form}
        return render(request,'warehouse/partials/transactiontable.html',context)
    else:
        context = {'trans':tr,'form':form}
        return render(request,'warehouse/partials/transaction_edit.html',context)


@login_required(login_url='/login/')
def deletetransaction(request,id):
    if request.method == 'POST':
        t = Transaction.objects.get(id=id)
        t.delete()
    return HttpResponse('')


@login_required(login_url='/login/')
def newRelated(request):
    form = RelatedForm(request.POST or None,request.FILES)
    if form.is_valid():
        form.save()
        return redirect('index')
    context={'form':form}
    return render(request,'warehouse/newcustomer.html',context)

@login_required(login_url='/login/')
def CustomerList(request):
    customers = Related.objects.all()
    context = {'customers' : customers }
    return render(request,'warehouse/customerlist.html',context)

@login_required(login_url='/login/')
def CustomerDetail(request,id):
    customer = Related.objects.get(id=id)
    jobs = Job.objects.filter(CustomerOrVendor=customer)
    transactions = Transaction.objects.filter(JobId__CustomerOrVendor=customer)
    context = {'customer' : customer,'jobs':jobs}
    return render(request,'warehouse/customerdetail.html',context)

@login_required(login_url='/login/')
def ProductExport(request):
    Product_Resource = ProductResource()
    queryset = Product.objects.all()
    dataset = Product_Resource.export(queryset)
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="export.xls"'
    return response

@login_required(login_url='/login/')
def refreshjoblist(request):
    wh = request.GET.get('wh')
    if wh == None:
        wh='W'
    job_list = Job.objects.filter(Warehouse=wh).order_by('-id')
    page = request.GET.get('page',1)

    paginator = Paginator(job_list,30)
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)
    context = {'jobs':jobs}
    return render(request,'warehouse/partials/joblist.html',context)

@login_required(login_url='/login')
def refreshjobdetail(request,id):
    J = Job.objects.get(id=id)
    product = Product.objects.all()
    form = NewTransactionForm(request.POST or None,initial={'JobId':id})

    context={'J':J,'form':form,'product':product}
    return render(request,'warehouse/partials/transactiontable.html',context)

@login_required(login_url='/login/')
def similarproduct(request):
    search_text = request.GET.get('ProductName')
    if len(search_text) > 1:
        results = Product.objects.filter(Q(ProductName__icontains=search_text)|Q(Tag__icontains=search_text))
    else:
        results =[]

    context = {"results": results}

    return render(request, 'warehouse/partials/similar.html', context)

@login_required(login_url='/login/')
def NewProduct(request):
    form = ProductForm(request.POST or None,request.FILES)
    if form.is_valid():
        form.save()
        return HttpResponse('<h1>New product added successfully</h1>')
    context={'form':form}
    return render(request,'warehouse/partials/newproduct.html',context)

@login_required(login_url='/login/')
def gettransaction(request,id):
    tran = Transaction.objects.filter(JobId = id)
    job = Job.objects.get(id=id)
    context = {'transactions':tran,'job':job}
    return render(request,'warehouse/partials/transaction.html',context)

@login_required(login_url='/login/')
def ImportFromSales(request,id):
    sid = request.POST.get('SalesID')
    form = NewTransactionForm(request.POST or None,initial={'JobId':id})
    tr = SO_Transaction.objects.filter(SO = sid)
    P = Job.objects.get(id=id)

    for t in tr:
        if t.Inventory.wh_stock>0:
            entry = Transaction(
                JobId = P,
                Inventory = t.Inventory,
                Qty = t.Quantity,
            )
            entry.save()

    J = Job.objects.get(id=id)
    context={'J':J,'form':form}
    return render(request,'warehouse/partials/transactiontable.html',context)

@login_required(login_url='/login/')
def CompleteAllJob(request):
    if request.method == 'POST':
        Job.objects.filter(Status = 'W').update(Status='C')
        return HttpResponse('<p>All Job updated</p>')

@login_required(login_url='/login/')
def Cash_Book(request):
    cashbook = CashBook.objects.all().order_by('-id')
    form = CashBookForm(request.POST or None)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.CreateBy = request.user

        temp.save() 
        form = CashBookForm()
    context = {
        'CashBook' : cashbook,
        'form' : form
    }
    return render(request,'warehouse/cashbook.html',context)