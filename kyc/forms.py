from django import forms
from .models import KycDocument

class KycUploadForm(forms.ModelForm):
    class Meta:
        model = KycDocument
        fields = ['document_type', 'document_image']