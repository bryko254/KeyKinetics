from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime
from accounts.models import CustomUser
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.urls import reverse
from django.conf import settings
from datetime import timedelta

class Yard(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    manager = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_yards'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):  
    current_yard = models.ForeignKey(  
        Yard,   
        on_delete=models.CASCADE,   
        related_name='current_vehicles'  
    )  
    make = models.CharField(max_length=100)  
    model = models.CharField(max_length=100)  
    year = models.IntegerField()  
    number_plate = models.CharField(max_length=20, unique=True)  
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True)  
    status = models.CharField(max_length=20, choices=[  
        ('available', 'Available'),  
        ('sold', 'Sold'),  
        ('maintenance', 'In Maintenance'),  
        ('transit', 'In Transit'),  
        ('reserved', 'Reserved')  
    ])  
    parking_spot = models.CharField(max_length=50, help_text="Location within the yard (e.g., 'A-12', 'Back Lot 5')", blank=True, null=True)  
    arrival_date = models.DateField()  
    last_moved = models.DateTimeField(auto_now=True)  
    assigned_sales_person = models.ForeignKey(  
        CustomUser,  
        on_delete=models.SET_NULL,  
        null=True,  
        blank=True,  
        related_name='assigned_vehicles'  
    )
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):  
        return f"{self.year} {self.make} {self.model} ({self.current_yard.name})"

    def get_assignment_url(self):
        """Get the URL for assigning a sales person to this vehicle"""
        if self.id:
            return reverse('keys:assign-sales-person', kwargs={'vehicle_id': self.id})
        return ''

    def generate_qr_code(self):
        """Generate QR code for this vehicle"""
        if not self.id:
            return
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Get the base URL from settings or use a default
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        # Create the full URL including the base URL
        assignment_url = self.get_assignment_url()
        if assignment_url:
            full_url = f"{base_url}{assignment_url}?plate={self.number_plate}"
            
            qr.add_data(full_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f'qr_code_{self.id}.png'
            
            self.qr_code.save(filename, File(buffer), save=False)
        
    def save(self, *args, **kwargs):
        # First save to ensure we have an ID
        super().save(*args, **kwargs)
        
        # Generate QR code if it doesn't exist
        if not self.qr_code:
            self.generate_qr_code()
            if self.qr_code:
                super().save(update_fields=['qr_code'])

class KeyStorage(models.Model):  
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE)  
    name = models.CharField(max_length=100)  
    location = models.CharField(max_length=200)  
    is_secure = models.BooleanField(default=True)  
    responsible_staff = models.ManyToManyField(CustomUser)
    
    def __str__(self):
        return f"{self.name} at {self.yard.name}"

class Key(models.Model):
    key_number = models.CharField(max_length=50, unique=True)  
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)  
    current_storage = models.ForeignKey(  
        KeyStorage,   
        on_delete=models.SET_NULL,   
        null=True  
    )  
    key_type = models.CharField(max_length=20, choices=[  
        ('main', 'Main Key'),  
        ('spare', 'Spare Key'),  
        ('valet', 'Valet Key')  
    ])  
    is_available = models.BooleanField(default=True)  
    notes = models.TextField(blank=True)  
    last_inventory_check = models.DateTimeField(null=True)
    
    def __str__(self):
        return f"{self.key_type} - {self.vehicle} ({self.key_number})"

    def create_checkout(self, checked_out_by, expected_return_time=None):
        """Create a key checkout record when a sales person is assigned"""
        # Get the yard from the vehicle
        checkout_yard = self.vehicle.current_yard
        
        # Create checkout record with current time in correct timezone
        now = localtime()
        if expected_return_time is None:
            expected_return_time = now + timedelta(hours=24)
        
        # Create checkout record
        checkout = KeyCheckout.objects.create(
            key=self,
            checked_out_by=checked_out_by,
            checkout_yard=checkout_yard,
            checked_out_time=now,
            expected_return_time=expected_return_time,
            purpose='Vehicle showing/test drive',
            status='active'
        )
        
        # Update key status
        self.is_available = False
        self.save()
        
        return checkout

    class Meta:
        verbose_name = 'Key'
        verbose_name_plural = 'Keys'

class KeyCheckout(models.Model):  
    key = models.ForeignKey(Key, on_delete=models.CASCADE)  
    checked_out_by = models.ForeignKey(  
        CustomUser,   
        on_delete=models.CASCADE,   
        related_name='key_checkouts'  
    )  
    authorized_by = models.ForeignKey(  
        CustomUser,   
        on_delete=models.SET_NULL,   
        null=True,
        blank=True,
        related_name='key_authorizations'  
    )  
    checkout_yard = models.ForeignKey(  
        Yard,  
        on_delete=models.CASCADE,  
        related_name='key_checkouts'  
    )  
    checked_out_time = models.DateTimeField()
    expected_return_time = models.DateTimeField()  
    actual_return_time = models.DateTimeField(null=True, blank=True)  
    return_yard = models.ForeignKey(  
        Yard,  
        on_delete=models.CASCADE,  
        related_name='key_returns',  
        null=True,
        blank=True
    )  
    purpose = models.CharField(max_length=200)  
    status = models.CharField(max_length=20, choices=[  
        ('active', 'Active'),  
        ('returned', 'Returned'),  
        ('overdue', 'Overdue'),  
        ('lost', 'Lost')  
    ], default='active')
    
    def __str__(self):
        return f"{self.key} - {self.checked_out_by} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new records
            if not self.checked_out_time:
                self.checked_out_time = localtime()
            if not self.expected_return_time:
                self.expected_return_time = self.checked_out_time + timedelta(hours=24)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-checked_out_time']
        verbose_name = 'Key Checkout'
        verbose_name_plural = 'Key Checkouts'