from django.shortcuts import render,redirect
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from . models import SalesOrder,SO_Transaction,buyer
from Product.models import Product,CurrencyRate
from . forms import SalesOrderForm,STForm,CurrencyRateForm,CustomerForm
from django.db.models import Q,Sum,Count,F,Prefetch,ExpressionWrapper,IntegerField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.db import transaction
from warehouse.models import Transaction
from datetime import datetime
import io
import openpyxl

# Create your views here.
def sales_order_list_queryset(queryset):
    """Return list-ready orders without loading hidden transaction rows."""
    line_amount = ExpressionWrapper(
        F('so_transaction__Price') * F('so_transaction__Quantity'),
        output_field=IntegerField(),
    )
    return queryset.select_related('Customer').annotate(
        list_subtotal=Coalesce(Sum(line_amount), 0),
        list_total_quantity=Coalesce(Sum('so_transaction__Quantity'), 0),
    )


def is_legacy_layout(request):
    referer = request.headers.get('Referer', '')
    return '/SD/' in referer and '/POS/' not in referer


def transaction_table_template(request):
    """Keep HTMX updates in the layout from which they were requested."""
    return 'sales/partials/transactiontable_legacy.html' if is_legacy_layout(request) else 'sales/partials/transactiontable.html'


def sales_detail_destination(request):
    return 'POS' if '/POS/' in request.headers.get('Referer', '') else 'SD'


@login_required(login_url='/login/')
def SalesIndex(request):
    customer = buyer.objects.all().order_by('Customer_Name')
    SO_list = sales_order_list_queryset(SalesOrder.objects.all()).order_by('-id')
    page = request.GET.get('page',1)
    paginator = Paginator(SO_list,30)
    last = paginator.num_pages
    td = datetime.today()
    today = datetime(td.year, td.month, td.day)

    try:
        SO = paginator.page(page)
    except PageNotAnInteger:
        SO = paginator.page(1)
    except EmptyPage:
        SO = paginator.page(paginator.num_pages)
    sot = SO_Transaction.objects.filter(SO__CreateDate__gte=today,SO__Currency='B').aggregate(s=Sum(F('Price')*F('Quantity')))
    sob = SO_Transaction.objects.filter(SO__CreateDate__gte=today,SO__Currency='K').aggregate(s=Sum(F('Price')*F('Quantity')))
    context={'SO': SO,'last':last,'totalbaht':sot['s'],'totalkyat':sob['s'],'customer':customer}
    return render(request,'sales/SO_list.html',context)

@login_required(login_url='/login/')
def NewSalesOrder(request):
    form = SalesOrderForm(request.POST or None,initial={'Currency':'B','Customer':'1'})
    if form.is_valid():
        temp = form.save(commit=False)
        temp.User = request.user
        temp.save()
        return redirect('SD',id=SalesOrder.objects.last().id)
    context = {'form' : form}
    return render(request,'sales/SO.html',context)

@login_required(login_url='/login/')
def EditSalesOrder(request,id):
    order = SalesOrder.objects.get(id=id)
    form = SalesOrderForm(request.POST or None,instance = order)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.Status = 'C'
        temp.save()
        msg = "<h1>Refund :{}</h1>".format(temp.Refund())
        # msg = '<p>Refund :' + refund + '</p>'
        return HttpResponse(msg)
    context = {'form' : form}
    return render(request,'sales/partials/SE.html',context)

@login_required(login_url='/login/')
def SalesDetail(request,id):
    if request.COOKIES.get('sales_ui_mode') == 'pos':
        return redirect('POS', id=id)

    form = STForm(request.POST or None,initial={'SO':id})
    if form.is_valid():
        form.save()
        form = STForm(initial={'SO':id})

    SO = SalesOrder.objects.select_related('Customer', 'User').prefetch_related(
        Prefetch(
            'so_transaction_set',
            queryset=SO_Transaction.objects.select_related('Inventory__Unit'),
        )
    ).get(id=id)

    # Profit is displayed for every line. Fetch the current rate once instead
    # of allowing each line's Profit method to issue the same query.
    currency_rate = CurrencyRate.objects.last()
    if currency_rate:
        for line in SO.so_transaction_set.all():
            line._currency_rate = currency_rate.Rate / 100

    next_order = SalesOrder.objects.filter(Customer_id=SO.Customer_id, id__gt=SO.id).only('id').first()
    previous_order = SalesOrder.objects.filter(Customer_id=SO.Customer_id, id__lt=SO.id).only('id').last()
    context = {'SO':SO, 'form':form, 'next_order':next_order, 'previous_order':previous_order}
    return render(request,'sales/SD_legacy.html',context)


@login_required(login_url='/login/')
@require_POST
def set_sales_ui(request, mode, id):
    if mode not in {'legacy', 'pos'}:
        return HttpResponseBadRequest('Unknown sales UI mode.')

    destination = 'POS' if mode == 'pos' else 'SD'
    response = redirect(destination, id=id)
    response.set_cookie('sales_ui_mode', mode, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response


@login_required(login_url='/login/')
@require_POST
def switchcurrency(request, id):
    """Toggle an open sales order and reprice all of its line items."""
    with transaction.atomic():
        sales_order = SalesOrder.objects.select_for_update().get(id=id)

        # Closed orders are historical records and must not be repriced.
        if sales_order.Status != 'O':
            return redirect(sales_detail_destination(request), id=id)

        sales_order.Currency = 'K' if sales_order.Currency == 'B' else 'B'
        sales_order.save(update_fields=['Currency'])

        is_retail = sales_order.Customer.Pricelist == '1'
        for line in sales_order.so_transaction_set.select_related('Inventory'):
            product = line.Inventory
            if sales_order.Currency == 'B':
                line.Price = product.RetailBaht if is_retail else product.MemberBaht
            else:
                line.Price = product.RetailKyat if is_retail else product.MemberKyat
            line.save(update_fields=['Price'])

    return redirect(sales_detail_destination(request), id=id)

@login_required(login_url='/login/')
def SO_List_Filter(request):
    c = request.GET.get('customer')
    SO_list = sales_order_list_queryset(SalesOrder.objects.filter(Customer=c)).order_by('-id')[:40]
    context = {'SO' : SO_list}
    return render(request,'sales/partials/SOlist.html',context)


@login_required(login_url='/login/')
def salesorderlines(request, id):
    sales_order = SalesOrder.objects.select_related('User').prefetch_related(
        Prefetch(
            'so_transaction_set',
            queryset=SO_Transaction.objects.select_related('Inventory__Unit'),
        )
    ).get(id=id)
    sales_order.total_quantity = sum(line.Quantity for line in sales_order.so_transaction_set.all())
    context = {'SO': sales_order}
    return render(request, 'sales/partials/salesorderlines.html', context)

@login_required(login_url='/login/')
def newtransaction(request,id):
    SO = SalesOrder.objects.get(id=id)
    form = STForm(request.POST or None,initial={'SO':id})
    highlight_line_id = None
    if form.is_valid():
        entry = form.save()
        highlight_line_id = entry.id
        form = STForm(initial={'SO':id})
        redirect('SD',id=id)
    context={'SO':SO, 'form':form, 'highlight_line_id':highlight_line_id, 'highlight_kind':'new'}
    return render(request, transaction_table_template(request), context)

@login_required(login_url='/login/')
def deletetransaction(request,id):
    tr = SO_Transaction.objects.filter(id=id)
    if request.method == 'POST':
        t = SO_Transaction.objects.get(id=id)
        t.delete()

    return HttpResponse('')

@login_required(login_url='/login/')
def geteditform(request,id):
    t = SO_Transaction.objects.get(id=id)
    form = STForm(request.POST or None,instance= t)
    SO = SalesOrder.objects.get(id=t.SO.id)
    if request.method == "POST":
        entry = None
        if form.is_valid():
            entry = form.save()
            form = STForm()
        context={'SO':SO, 'form':form, 'highlight_line_id':entry.id if entry else None, 'highlight_kind':'updated'}
        return render(request, transaction_table_template(request), context)
    else:
        context={'SO':SO,'form':form}
        return render(request,'sales/partials/transaction_edit.html',context)

@login_required(login_url='/login/')
def getsearchresult(request,id):
    SO = SalesOrder.objects.get(id=id)
    search_text = request.GET.get('search')
    if len(search_text) > 1:
        results = Product.objects.filter(Q(ProductName__icontains=search_text)|Q(Barcode__iexact=search_text)|Q(Tag__icontains=search_text)).exclude(Status='N').order_by('ProductName')
    else:
        results =[]

    context = {'results':results, 'SO':SO, 'search_text':search_text}
    template = 'sales/partials/searchresult_legacy.html' if is_legacy_layout(request) else 'sales/partials/searchresult_pos.html'
    return render(request, template, context)

@login_required(login_url='/login/')
def getPayment(request,id):
    SO = SalesOrder.objects.get(id=id)
    payment = request.GET.get('payment')
    if payment is None:
        payment = 0
    else:
        payment = int(payment)
    SO.Pay = payment
    SO.Status = 'C'
    SO.save()
    form = STForm(request.POST or None,initial={'SO':id})

    context = {'form':form,'SO':SO}
    return render(request, transaction_table_template(request), context)

@login_required(login_url='/login/')
def filtertransaction(request,id,p):
    PL = Product.objects.get(id=p)
    SO = SalesOrder.objects.get(id=id)
    if SO.Currency == 'B':
        if SO.Customer.Pricelist == '1':
            price = PL.RetailBaht
        else:
            price = PL.MemberBaht
    else:
        if SO.Customer.Pricelist == '1':
            price = PL.RetailKyat
        else:
            price = PL.MemberKyat
    form = STForm(request.POST or None,initial={'SO':id,'Price':price,'Inventory':PL,'Quantity':1})
    context = {'SO':SO, 'form':form, 'manual_mode':request.GET.get('entry') == 'manual'}
    template = 'sales/partials/newtransactionform_legacy.html' if is_legacy_layout(request) else 'sales/partials/newtransactionform.html'
    return render(request, template, context)

@login_required(login_url='/login/')
def newcurrencyrate(request):
     rates = CurrencyRate.objects.all().order_by('-id')
     form = CurrencyRateForm(request.POST or None)
     if form.is_valid():
         form.save()
     context = {'form':form,'rates':rates}
     return render(request,'sales/newcurrencyrate.html',context)

@login_required(login_url='/login/')
def newcustomer(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('salesindex')
    context = {'form':form}
    return render(request,'sales/newcustomer.html',context)

@login_required(login_url='/login/')
def editcustomer(request,id):
    cus = buyer.objects.get(id=id)
    form = CustomerForm(request.POST or None,instance=cus)
    if form.is_valid():
        form.save()
        return redirect('salesindex')
    context = {'form':form}
    return render(request,'sales/newcustomer.html',context) 

@login_required(login_url='/login/')
def ImportFromJob(request,sid):
    jid = request.POST.get('JobID')
    form = STForm(request.POST or None,initial={'SO':sid})
    tr = Transaction.objects.filter(JobId = jid)
    S = SalesOrder.objects.get(id=sid)

    
    for t in tr:
        if S.Currency == 'B':
            if S.Customer.Pricelist == '1':
                p = t.Inventory.RetailBaht()
            else:
                p = t.Inventory.MemberBaht()
        else:
            if S.Customer.Pricelist == '1':
                p = t.Inventory.RetailKyat()
            else:
                p = t.Inventory.MemberKyat()

        entry = SO_Transaction(
            SO = S,
            Inventory = t.Inventory,
            Quantity = t.Qty,
            Price = p
        )
        entry.save()
    SO = SalesOrder.objects.get(id=sid)
    context={'SO':SO,'form':form}
    return render(request, transaction_table_template(request), context)

@login_required(login_url='/login/')
def SalesInvoice(request,id,p):
    SO = SalesOrder.objects.get(id=id)
    context = {'SO' : SO,'p':p}
    return render(request,'sales/S_Invoice.html',context)

@login_required(login_url='/login/')
def customerlist(request):
    customers = buyer.objects.all()
    context = {'customers' : customers}
    return render(request,'sales/customerlist.html',context)

@login_required(login_url='/login/')
def saleshistory(request,id):
    p = Product.objects.get(id=id)
    transactions = SO_Transaction.objects.filter(Inventory = p).order_by('-id')[:50]
    context = {'product':p,'transactions':transactions}
    return render(request,'sales/partials/saleshistory.html',context)

@login_required(login_url='/login/')
def POS(request,id):
    SO = SalesOrder.objects.select_related('Customer', 'User').prefetch_related(
        Prefetch(
            'so_transaction_set',
            queryset=SO_Transaction.objects.select_related('Inventory__Unit'),
        )
    ).get(id=id)
    currency_rate = CurrencyRate.objects.last()
    if currency_rate:
        for line in SO.so_transaction_set.all():
            line._currency_rate = currency_rate.Rate / 100

    context = {
        'SO': SO,
        'form': STForm(initial={'SO': id}),
        'next_order': SalesOrder.objects.filter(Customer_id=SO.Customer_id, id__gt=SO.id).only('id').first(),
        'previous_order': SalesOrder.objects.filter(Customer_id=SO.Customer_id, id__lt=SO.id).only('id').last(),
    }
    return render(request, 'sales/SD.html', context)

import json
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseNotFound

@login_required(login_url='/login/')
def Barcode(request, id):
    barcode = (request.GET.get('barcode') or '').strip()
    try:
        quantity = int(request.GET.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    sales = SalesOrder.objects.get(id=id)
    form = STForm(request.POST or None, initial={'SO': id})

    if Product.objects.filter(Barcode__iexact=barcode).exists():
        # normal workflow...
        if Product.objects.filter(Barcode__iexact=barcode).count() == 1:
            inventory = Product.objects.get(Barcode__iexact=barcode)
        else:
            inventory = Product.objects.filter(Barcode__iexact=barcode).last()

        p = inventory.RetailKyat if sales.Currency == 'K' else inventory.RetailBaht

        st, created = SO_Transaction.objects.get_or_create(
            SO=sales, Inventory=inventory,
            defaults={'Quantity': quantity, 'Price': p}
        )
        if not created:
            st.Quantity += quantity
            st.save()

        message = 'successfully added'
        context = {
            'SO': sales,
            'message': message,
            'form': form,
            'highlight_line_id': st.id,
            'highlight_kind': 'new' if created else 'updated',
        }
        return render(request, transaction_table_template(request), context)

    else:
        response = HttpResponse(status=204)  # <-- important!
        response['HX-Trigger'] = json.dumps({
            "noRecordFound": {"barcode": barcode}
        })
        return response

def QuickSales(request,c):
    b = buyer.objects.get(id=1)
    if c == 1:
        SalesOrder.objects.create(
            Customer = b,
            Currency = 'B',
            User = request.user,
            Status = 'O'
        )
    else:
        SalesOrder.objects.create(
            Customer = b,
            Currency = 'K',
            User = request.user,
            Status = 'O'
        )
    last = SalesOrder.objects.last().id
    return redirect('SD',last)

def test(request):
    HttpResponse('<h1>Test</h1>')

def export_to_excel(request):
    # Create a workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Data Export'

    # Add header row
    headers = ['ID', 'Name', 'Email', 'Date Joined']
    sheet.append(headers)

    # Example data (replace with your query)
    data = [
        [1, 'John Doe', 'john.doe@example.com', '2023-01-01'],
        [2, 'Jane Smith', 'jane.smith@example.com', '2023-02-15'],
    ]
    
    # Append data rows
    for row in data:
        sheet.append(row)
    
    # Save workbook to a virtual file
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="data_export.xlsx"'

    return response
