from django.contrib import admin
from .models import Yard, Vehicle, KeyStorage, Key, KeyCheckout

@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'manager', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'vin', 'current_yard', 'status', 'parking_spot')
    list_filter = ('status', 'current_yard', 'make')
    search_fields = ('make', 'model', 'vin')
    date_hierarchy = 'arrival_date'

@admin.register(KeyStorage)
class KeyStorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'yard', 'location', 'is_secure')
    list_filter = ('yard', 'is_secure')
    search_fields = ('name', 'location')
    filter_horizontal = ('responsible_staff',)

@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key_number', 'vehicle', 'key_type', 'current_storage', 'is_available')
    list_filter = ('key_type', 'is_available')
    search_fields = ('key_number', 'vehicle__vin')
    date_hierarchy = 'last_inventory_check'

@admin.register(KeyCheckout)
class KeyCheckoutAdmin(admin.ModelAdmin):
    list_display = ('key', 'checked_out_by', 'checkout_yard', 'checked_out_time', 'status')
    list_filter = ('status', 'checkout_yard')
    search_fields = ('key__key_number', 'checked_out_by__username', 'purpose')
    date_hierarchy = 'checked_out_time'
    readonly_fields = ('checked_out_time',)
