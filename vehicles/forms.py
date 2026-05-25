from django import forms
from .models import Vehicle, VehicleDocument

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'make', 'model',
            'year', 'color', 'engine_number', 'chassis_number'
        ]

class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'document_file']