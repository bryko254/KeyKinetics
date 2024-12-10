from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Q, F, Max, Min
from django.utils.timezone import localtime, timedelta
from keys.models import KeyCheckout, Vehicle, Key, KeyStorage
from accounts.models import CustomUser
from django.db.models.functions import TruncDate, TruncMonth

def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

@login_required
@user_passes_test(is_manager)
def dashboard(request):
    # Get date range for filtering
    end_date = localtime()
    start_date = end_date - timedelta(days=30)  # Last 30 days by default
    
    # Key Statistics
    total_keys = Key.objects.count()
    available_keys = Key.objects.filter(is_available=True).count()
    checked_out_keys = Key.objects.filter(is_available=False).count()
    
    # Vehicle Statistics
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status='available').count()
    assigned_vehicles = Vehicle.objects.exclude(assigned_sales_person=None).count()
    
    # Key Checkout Statistics
    checkouts_by_date = KeyCheckout.objects.filter(
        checked_out_time__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('checked_out_time')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Top Sales People - Convert to list of dicts
    top_sales_people = list(CustomUser.objects.filter(
        role='sales'
    ).annotate(
        checkout_count=Count('key_checkouts')
    ).values('id', 'first_name', 'last_name', 'checkout_count')
    .order_by('-checkout_count')[:5])
    
    # Key Status Distribution
    key_status = KeyCheckout.objects.filter(
        checked_out_time__range=(start_date, end_date)
    ).values('status').annotate(
        count=Count('id')
    )
    
    # Average Checkout Duration
    avg_checkout_duration = KeyCheckout.objects.filter(
        status='returned',
        checked_out_time__range=(start_date, end_date),
        actual_return_time__isnull=False
    ).annotate(
        duration=F('actual_return_time') - F('checked_out_time')
    ).aggregate(
        avg_duration=Avg('duration')
    )['avg_duration']
    
    # Monthly Trends - Convert datetime to string format
    monthly_checkouts = list(KeyCheckout.objects.annotate(
        month=TruncMonth('checked_out_time')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month'))
    
    # Convert datetime objects to strings
    for item in monthly_checkouts:
        if item['month']:
            item['month'] = item['month'].strftime('%Y-%m-%d')
    
    context = {
        'total_keys': total_keys,
        'available_keys': available_keys,
        'checked_out_keys': checked_out_keys,
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'assigned_vehicles': assigned_vehicles,
        'checkouts_by_date': list(checkouts_by_date),
        'top_sales_people': top_sales_people,
        'key_status': list(key_status),
        'avg_checkout_duration': str(avg_checkout_duration) if avg_checkout_duration else None,
        'monthly_checkouts': monthly_checkouts,
    }
    return render(request, 'reports/dashboard.html', context)

@login_required
@user_passes_test(is_manager)
def sales_performance(request):
    end_date = localtime()
    start_date = end_date - timedelta(days=30)
    
    # Convert QuerySet to list of dictionaries with serializable data
    sales_performance = list(CustomUser.objects.filter(
        role='sales',
        key_checkouts__checked_out_time__range=(start_date, end_date)
    ).annotate(
        total_checkouts=Count('key_checkouts'),
        active_checkouts=Count('key_checkouts', filter=Q(key_checkouts__status='active')),
        overdue_checkouts=Count('key_checkouts', filter=Q(key_checkouts__status='overdue')),
        returned_checkouts=Count('key_checkouts', filter=Q(key_checkouts__status='returned'))
    ).values(
        'id', 'first_name', 'last_name', 
        'total_checkouts', 'active_checkouts', 
        'overdue_checkouts', 'returned_checkouts'
    ).order_by('-total_checkouts'))
    
    context = {
        'sales_performance': sales_performance,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'reports/sales_performance.html', context)

@login_required
@user_passes_test(is_manager)
def vehicle_analytics(request):
    # Convert QuerySets to lists of dictionaries
    vehicle_status = list(Vehicle.objects.values('status').annotate(
        count=Count('id')
    ))
    
    yard_distribution = list(Vehicle.objects.values(
        'current_yard__name'
    ).annotate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        assigned=Count('id', filter=~Q(assigned_sales_person=None))
    ).exclude(current_yard__name__isnull=True))  # Exclude null yard names
    
    context = {
        'vehicle_status': vehicle_status,
        'yard_distribution': yard_distribution,
    }
    return render(request, 'reports/vehicle_analytics.html', context)

@login_required
@user_passes_test(is_manager)
def key_analytics(request):
    end_date = localtime()
    start_date = end_date - timedelta(days=30)

    # Convert QuerySets to lists
    key_types = list(Key.objects.values('key_type').annotate(
        count=Count('id')
    ))
    
    # Handle KeyStorage stats
    try:
        storage_stats = list(KeyStorage.objects.annotate(
            total_keys=Count('key'),
            available_keys=Count('key', filter=Q(key__is_available=True))
        ).values('name', 'total_keys', 'available_keys'))
    except KeyStorage.DoesNotExist:
        storage_stats = []
    
    # Duration statistics
    duration_stats = KeyCheckout.objects.filter(
        status='returned',
        actual_return_time__isnull=False,
        checked_out_time__range=(start_date, end_date)
    ).annotate(
        duration=F('actual_return_time') - F('checked_out_time')
    ).aggregate(
        avg_duration=Avg('duration'),
        max_duration=Max('duration'),
        min_duration=Min('duration')
    )
    
    # Convert timedelta objects to strings
    for key, value in duration_stats.items():
        if value is not None:
            duration_stats[key] = str(value)
    
    context = {
        'key_types': key_types,
        'storage_stats': storage_stats,
        'duration_stats': duration_stats,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'reports/key_analytics.html', context)
