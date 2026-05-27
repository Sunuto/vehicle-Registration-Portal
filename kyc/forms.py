from django import forms
from django.core.exceptions import ValidationError
from .models import KycDocument

class KycUploadForm(forms.ModelForm):
    class Meta:
        model = KycDocument
        fields = ['document_type', 'document_image']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_document_type(self):
        document_type = self.cleaned_data.get('document_type')
        valid_types = ['citizenship', 'driving_license', 'national_id']

        if not document_type:
            raise ValidationError('⚠ Please select a document type.')

        if document_type not in valid_types:
            raise ValidationError('⚠ Invalid document type. Only Citizenship Card, Driving License or National ID allowed.')

        # Check if user already uploaded this document type
        if self.user:
            existing = KycDocument.objects.filter(
                user=self.user,
                document_type=document_type
            ).exclude(status='rejected')
            if existing.exists():
                raise ValidationError(f'⚠ You have already uploaded a {dict(KycDocument.DOCUMENT_TYPE)[document_type]}. Please wait for review or upload a different document type.')

        return document_type

    def clean_document_image(self):
        image = self.cleaned_data.get('document_image')

        if not image:
            raise ValidationError('⚠ Please upload a document image.')

        # Check file size (max 5MB)
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('⚠ File size cannot exceed 5MB.')

        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if image.content_type not in allowed_types:
            raise ValidationError('⚠ Only JPG and PNG images are allowed.')

        return image