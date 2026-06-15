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

        if self.user:
            # Block if ANY document is already approved
            if KycDocument.objects.filter(user=self.user, status='approved').exists():
                raise ValidationError('⚠ Your KYC is already approved. No further uploads needed.')

            # Block same type if pending or approved
            existing = KycDocument.objects.filter(
                user=self.user,
                document_type=document_type,
                status__in=['pending', 'approved']
            )
            if existing.exists():
                type_label = dict(KycDocument.DOCUMENT_TYPE)[document_type]
                raise ValidationError(f'⚠ You already have a {type_label} that is pending or approved.')

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