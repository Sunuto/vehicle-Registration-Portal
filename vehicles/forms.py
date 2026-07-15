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
            'chassis_number',
            'plate_number',

            'vehicle_front_image',
            'vehicle_back_image',
            'number_plate_image',
            'bluebook_image',
        ]

        widgets = {

            "vehicle_type": forms.Select(attrs={
                "class": "form-input",
            }),

            "make": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. Toyota",
            }),

            "model": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. Corolla",
            }),

            "year": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. 2020",
                "min": "1990",
                "max": str(datetime.datetime.now().year),
            }),

            "color": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. Red",
            }),

            "engine_number": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. 2NZ-1234567",
            }),

            "chassis_number": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. MA3FJEB1S00123456",
            }),

            "plate_number": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. BA 2 CHA 1234",
            }),

            # Hide the actual file inputs because your custom upload cards will trigger them
            "vehicle_front_image": forms.FileInput(attrs={
                "class": "hidden",
                "accept": "image/*",
            }),

            "vehicle_back_image": forms.FileInput(attrs={
                "class": "hidden",
                "accept": "image/*",
            }),

            "number_plate_image": forms.FileInput(attrs={
                "class": "hidden",
                "accept": "image/*",
            }),

            "bluebook_image": forms.FileInput(attrs={
                "class": "hidden",
                "accept": "image/*",
            }),
        }

class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'document_file']