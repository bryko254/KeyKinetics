from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Vehicle, Key, KeyCheckout
from accounts.models import CustomUser
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.db import transaction

def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

def assign_sales_person(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    number_plate = request.GET.get('plate')
    
    # Verify the number plate matches
    if vehicle.number_plate != number_plate:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR code'})
    
    if request.method == 'POST':
        sales_person_id = request.POST.get('sales_person')
        if sales_person_id:
            sales_person = get_object_or_404(CustomUser, id=sales_person_id)
            
            # Assign sales person to vehicle
            vehicle.assigned_sales_person = sales_person
            vehicle.save()
            
            # Find and checkout the main key for the vehicle
            try:
                key = Key.objects.get(vehicle=vehicle, key_type='main')
                # Create checkout with explicit timezone-aware times
                now = localtime()
                expected_return = now + timedelta(hours=24)
                
                checkout = KeyCheckout.objects.create(
                    key=key,
                    checked_out_by=sales_person,
                    checkout_yard=vehicle.current_yard,
                    checked_out_time=now,
                    expected_return_time=expected_return,
                    purpose='Vehicle showing/test drive',
                    status='active'
                )
                
                # Update key availability
                key.is_available = False
                key.save()
                
                message = f'Vehicle and key assigned to {sales_person.get_full_name()}'
            except Key.DoesNotExist:
                message = f'Vehicle assigned to {sales_person.get_full_name()} (No main key found)'
            
            return JsonResponse({
                'status': 'success', 
                'message': message
            })
        return JsonResponse({'status': 'error', 'message': 'Please select a sales person'})
    
    # Get all users with sales role who are active
    sales_persons = CustomUser.objects.filter(role='sales', is_active_employee=True).order_by('first_name')
    
    context = {
        'vehicle': vehicle,
        'sales_persons': sales_persons,
    }
    return render(request, 'keys/assign_sales_person.html', context)

@login_required
@user_passes_test(is_manager)
def key_tracking(request):
    # Get filter parameters
    status = request.GET.get('status', 'all')
    days = request.GET.get('days', '7')  # Default to last 7 days
    search = request.GET.get('search', '')
    
    # Base queryset with all related fields to avoid N+1 queries
    checkouts = KeyCheckout.objects.select_related(
        'key', 
        'key__vehicle', 
        'checked_out_by', 
        'checkout_yard'
    ).order_by('-checked_out_time')
    
    # Apply filters
    if status != 'all':
        checkouts = checkouts.filter(status=status)
    
    if days != 'all':
        try:
            days = int(days)
            start_date = localtime() - timedelta(days=days)
            checkouts = checkouts.filter(checked_out_time__gte=start_date)
        except ValueError:
            pass
    
    if search:
        checkouts = checkouts.filter(
            Q(key__vehicle__make__icontains=search) |
            Q(key__vehicle__model__icontains=search) |
            Q(key__vehicle__number_plate__icontains=search) |
            Q(checked_out_by__first_name__icontains=search) |
            Q(checked_out_by__last_name__icontains=search)
        )
    
    # Update overdue status for active checkouts using localtime
    now = localtime()
    active_checkouts = checkouts.filter(status='active', expected_return_time__lt=now)
    active_checkouts.update(status='overdue')
    
    # Get summary statistics
    total_active = checkouts.filter(status='active').count()
    total_overdue = checkouts.filter(status='overdue').count()
    total_returned = checkouts.filter(status='returned').count()
    
    context = {
        'checkouts': checkouts,
        'status_filter': status,
        'days_filter': days,
        'search_query': search,
        'total_active': total_active,
        'total_overdue': total_overdue,
        'total_returned': total_returned,
        'current_time': localtime(),  # Add current time to context for reference
    }
    return render(request, 'keys/key_tracking.html', context)

@login_required
@user_passes_test(is_manager)
@require_http_methods(["POST"])
def mark_key_returned(request, checkout_id):
    try:
        with transaction.atomic():
            checkout = get_object_or_404(KeyCheckout.objects.select_related('key'), id=checkout_id)
            
            if checkout.status == 'returned':
                return JsonResponse({
                    'status': 'error',
                    'message': 'This key has already been returned'
                })
            
            # Update checkout record with localtime
            checkout.status = 'returned'
            checkout.actual_return_time = localtime()
            checkout.return_yard = checkout.checkout_yard
            checkout.save()
            
            # Update key availability
            key = checkout.key
            key.is_available = True
            key.save()
            
            vehicle = key.vehicle
            if vehicle.assigned_sales_person and vehicle.assigned_sales_person == checkout.checked_out_by:
                vehicle.assigned_sales_person = None
                vehicle.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Key for {vehicle.make} {vehicle.model} has been marked as returned'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing the return'
        })
