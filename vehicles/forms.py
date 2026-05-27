from django import forms
from django.core.exceptions import ValidationError
from .models import Vehicle, VehicleDocument
import datetime
import re

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'make', 'model',
            'year', 'color', 'engine_number', 'chassis_number'
        ]

    def clean_vehicle_type(self):
        vehicle_type = self.cleaned_data.get('vehicle_type')
        if not vehicle_type:
            raise ValidationError('⚠ Please select a vehicle type.')
        return vehicle_type

    def clean_make(self):
        make = self.cleaned_data.get('make', '').strip()
        if not make:
            raise ValidationError('⚠ Vehicle make/brand is required.')
        if len(make) < 2:
            raise ValidationError('⚠ Make must be at least 2 characters.')
        if len(make) > 100:
            raise ValidationError('⚠ Make cannot exceed 100 characters.')
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', make):
            raise ValidationError('⚠ Make can only contain letters, numbers, spaces and hyphens.')
        return make.title()

    def clean_model(self):
        model = self.cleaned_data.get('model', '').strip()
        if not model:
            raise ValidationError('⚠ Vehicle model is required.')
        if len(model) < 1:
            raise ValidationError('⚠ Model must be at least 1 character.')
        if len(model) > 100:
            raise ValidationError('⚠ Model cannot exceed 100 characters.')
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', model):
            raise ValidationError('⚠ Model can only contain letters, numbers, spaces and hyphens.')
        return model.title()

    def clean_year(self):
        year = self.cleaned_data.get('year')
        current_year = datetime.datetime.now().year
        if not year:
            raise ValidationError('⚠ Vehicle year is required.')
        if year < 1990:
            raise ValidationError('⚠ Year cannot be before 1990.')
        if year > current_year:
            raise ValidationError(f'⚠ Year cannot be in the future. Maximum is {current_year}.')
        return year

    def clean_color(self):
        color = self.cleaned_data.get('color', '').strip()
        if not color:
            raise ValidationError('⚠ Vehicle color is required.')
        if len(color) < 2:
            raise ValidationError('⚠ Color must be at least 2 characters.')
        if len(color) > 50:
            raise ValidationError('⚠ Color cannot exceed 50 characters.')
        if not re.match(r'^[a-zA-Z\s]+$', color):
            raise ValidationError('⚠ Color can only contain letters and spaces.')
        return color.title()

def clean_engine_number(self):
    engine_number = self.cleaned_data.get('engine_number', '').strip().upper()
    if not engine_number:
        raise ValidationError('⚠ Engine number is required.')
    if len(engine_number) < 5:
        raise ValidationError('⚠ Engine number must be at least 5 characters.')
    if len(engine_number) > 20:
        raise ValidationError('⚠ Engine number cannot exceed 20 characters.')
    if not re.match(r'^[A-Z0-9\-]+$', engine_number):
        raise ValidationError('⚠ Engine number can only contain uppercase letters, numbers and hyphens.')

    # Check uniqueness
    existing = Vehicle.objects.filter(engine_number=engine_number)
    if self.instance.pk:
        existing = existing.exclude(pk=self.instance.pk)
    if existing.exists():
        raise ValidationError('⚠ A vehicle with this engine number is already registered.')

    return engine_number

def clean_chassis_number(self):
    chassis_number = self.cleaned_data.get('chassis_number', '').strip().upper()
    if not chassis_number:
        raise ValidationError('⚠ Chassis number is required.')
    if len(chassis_number) < 5:
        raise ValidationError('⚠ Chassis number must be at least 5 characters.')
    if len(chassis_number) > 17:
        raise ValidationError('⚠ Chassis/VIN number cannot exceed 17 characters.')
    if not re.match(r'^[A-Z0-9\-]+$', chassis_number):
        raise ValidationError('⚠ Chassis number can only contain uppercase letters, numbers and hyphens.')

    # Check uniqueness
    existing = Vehicle.objects.filter(chassis_number=chassis_number)
    if self.instance.pk:
        existing = existing.exclude(pk=self.instance.pk)
    if existing.exists():
        raise ValidationError('⚠ A vehicle with this chassis number is already registered.')

    return chassis_number

    def clean(self):
        cleaned_data = super().clean()
        engine_number = cleaned_data.get('engine_number', '')
        chassis_number = cleaned_data.get('chassis_number', '')

        # Engine and chassis numbers must be different
        if engine_number and chassis_number:
            if engine_number == chassis_number:
                raise ValidationError('⚠ Engine number and chassis number cannot be the same.')

        return cleaned_data


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'document_file']