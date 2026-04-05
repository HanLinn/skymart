from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from sales.models import SalesOrder, SO_Transaction
from dateutil.relativedelta import relativedelta

# Get current date and ensure it's timezone aware
today = timezone.now().date()

# Calculate sales for last 6 months
for i in range(6):
    # Calculate start and end date for each month
    end_date = (today.replace(day=1) - timedelta(days=1) - relativedelta(months=i))
    start_date = end_date.replace(day=1)
    
    # Convert dates to timezone-aware datetime for database query
    start_datetime = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
    end_datetime = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
    
    # Filter SalesOrders for the month
    sales_orders = SalesOrder.objects.filter(
        CreateDate__range=(start_datetime, end_datetime)
    )
    
    # Calculate total quantity for the month
    monthly_quantity = SO_Transaction.objects.filter(
        SO__in=sales_orders
    ).aggregate(total=Sum('Quantity'))['total'] or 0
    
    # Format and print the month and its total
    month_name = start_date.strftime('%B %Y')