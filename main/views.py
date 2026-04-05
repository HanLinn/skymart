from django.shortcuts import render
from django.http.response import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Sum,Count,Func,F,Case,When,DecimalField
from django.db.models.functions import TruncDate
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
from Product.models import Product,CurrencyRate
from sales.models import SO_Transaction,SalesOrder
from warehouse.models import Related,Job
from purchase.models import Vendor

@login_required(login_url='/login/')
def index(request):
    today = datetime.now()
    m = datetime(today.year,today.month,1)
    p=Product.objects.filter().annotate(q = Sum('so_transaction__Quantity')).order_by('-q')[:10]
    thismonth = Product.objects.filter(so_transaction__SO__CreateDate__gte=m).annotate(q = Sum('so_transaction__Quantity')).order_by('-q')[:10]
    customer = Related.objects.filter(job__Type='O',job__CreateDate__gte=m).annotate(q = Sum('job__transaction__Qty')).order_by('-q')[:10]

    sales = SalesOrder.objects.filter(CreateDate__gte=m)
    report = sales.annotate(date=TruncDate('CreateDate')).values('date').annotate(
        baht=Sum(Case(When(Currency='B', then=F('so_transaction__Quantity')*F('so_transaction__Price')), default=0, output_field=DecimalField())),
        kyat=Sum(Case(When(Currency='K', then=F('so_transaction__Quantity')*F('so_transaction__Price')), default=0, output_field=DecimalField()))
    ).values('date', 'baht', 'kyat').order_by('-date')


    context = {'product':p,'thismonth':thismonth,'customer':customer,'report':report}
    return render(request,'main/index.html',context)

@login_required(login_url='/login/')
def unisearch(request):
    kw = request.GET.get('search')
    if len(kw) > 1:
        product = Product.objects.filter(Q(ProductName__icontains=kw)|Q(Tag__icontains=kw)|Q(Barcode__icontains=kw)).exclude(Status='N')
        customer = Related.objects.filter(RelatedName__icontains=kw)
        job = Job.objects.filter(Q(id__icontains=kw)|Q(Agent__icontains=kw)|Q(Vehicle__icontains=kw)|Q(Note__icontains=kw))
        so = SalesOrder.objects.filter(Q(id__icontains=kw)|Q(Note__icontains=kw)|Q(Customer__Customer_Name__icontains=kw))
        vendor = Vendor.objects.filter(Q(Name__icontains=kw))

    else:
        product = []
        customer = []
        job = []
        vendor = []
        so = []
    context={'products':product,'customer':customer,'job':job,'vendor':vendor,'so':so}

    return render(request,'main/partials/universalresult.html',context)


@login_required(login_url='/login/')
def saleschart(request):
    today = date.today()
    rate = CurrencyRate.objects.last().Rate/100
    start = date(today.year,today.month,1)
    start = today - relativedelta(days=7)
    end = today
    labels = []
    data = []
    while start <= end:
        baht = SalesOrder.objects.filter(CreateDate__year = start.year,CreateDate__month=start.month,CreateDate__day = start.day).filter(Currency='B').aggregate(q = Sum(F('so_transaction__Quantity')*F('so_transaction__Price')))
        kyat = SalesOrder.objects.filter(CreateDate__year = start.year,CreateDate__month=start.month,CreateDate__day = start.day).filter(Currency='K').aggregate(q = Sum(F('so_transaction__Quantity')*F('so_transaction__Price')))
        kyat_q = kyat['q'] if kyat['q'] is not None else 0
        baht_q = baht['q'] if baht['q'] is not None else 0
        eqbaht = int(kyat_q * rate)
        total = int(baht_q + eqbaht)
        labels.append(str(start))
        data.append(total)
        start = start + relativedelta(days=1)

    return JsonResponse(data={
        'labels': labels,
        'data': data
    })