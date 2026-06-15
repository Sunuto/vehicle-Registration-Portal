from django import forms
from django.core.exceptions import ValidationError
from .models import Vehicle, VehicleDocument
import datetime
import re


class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type',
            'make',
            'model',
            'year',
            'color',
            'engine_number',
            'chassis_number'
        ]

    def clean_vehicle_type(self):
        value = self.cleaned_data.get('vehicle_type')
        if not value:
            raise ValidationError("Vehicle type is required.")
        return value

    def clean_make(self):
        make = self.cleaned_data.get('make', '').strip()
        if len(make) < 2:
            raise ValidationError("Make too short.")
        if not re.match(r'^[A-Za-z0-9\s\-]+$', make):
            raise ValidationError("Invalid make format.")
        return make.title()

    def clean_model(self):
        model = self.cleaned_data.get('model', '').strip()
        if len(model) < 1:
            raise ValidationError("Model required.")
        if not re.match(r'^[A-Za-z0-9\s\-]+$', model):
            raise ValidationError("Invalid model format.")
        return model.title()

    def clean_year(self):
        year = self.cleaned_data.get('year')
        current_year = datetime.datetime.now().year

        if year < 1990 or year > current_year:
            raise ValidationError("Invalid vehicle year for Nepal context.")
        return year

    def clean_color(self):
        color = self.cleaned_data.get('color', '').strip()
        if not re.match(r'^[A-Za-z\s]+$', color):
            raise ValidationError("Invalid color.")
        return color.title()

    def clean_engine_number(self):
        engine = self.cleaned_data.get('engine_number', '').strip().upper()

        if not re.match(r'^[A-Z0-9\-]{5,20}$', engine):
            raise ValidationError("Invalid engine format.")

        qs = Vehicle.objects.filter(engine_number=engine)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Engine number already exists.")

        return engine

    def clean_chassis_number(self):
        chassis = self.cleaned_data.get('chassis_number', '').strip().upper()

        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', chassis):
            raise ValidationError("Invalid VIN (Nepal follows VIN 17-char format).")

        qs = Vehicle.objects.filter(chassis_number=chassis)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Chassis number already exists.")

        return chassis

    def clean(self):
        cleaned = super().clean()
        engine = cleaned.get("engine_number")
        chassis = cleaned.get("chassis_number")

        if engine and chassis and engine == chassis:
            raise ValidationError("Engine and chassis cannot be same.")

        return cleaned


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'document_file']