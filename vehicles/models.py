import datetime
import uuid
from django.db import models
from users.models import CustomUser


class Vehicle(models.Model):
    VEHICLE_TYPE = (
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
        ('jeep', 'Jeep'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vehicles')

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)

    engine_number = models.CharField(max_length=100, unique=True)
    chassis_number = models.CharField(max_length=100, unique=True)

    registration_number = models.CharField(max_length=30, unique=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    remarks = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_vehicles'
    )

    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.registration_number = self.generate_registration_number()
        super().save(*args, **kwargs)

    def generate_registration_number(self):
        year = datetime.datetime.now().year
        return f"NEP-{year}-{uuid.uuid4().hex[:6].upper()}"

    def __str__(self):
        return f"{self.make} {self.model} ({self.owner.username})"


class VehicleDocument(models.Model):
    DOCUMENT_TYPE = (
        ('insurance', 'Insurance'),
        ('tax_clearance', 'Tax Clearance'),
        ('vehicle_photo', 'Vehicle Photo'),
        ('other', 'Other'),
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE)
    document_file = models.FileField(upload_to='vehicle_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_verified = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.document_type}"