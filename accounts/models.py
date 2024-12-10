from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('sales', 'Sales Person'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLES, default='staff')
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_active_employee = models.BooleanField(default=True)
    last_login_yard = models.ForeignKey(
        'keys.Yard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_last_logins'
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
