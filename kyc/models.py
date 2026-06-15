from django.db import models
from users.models import CustomUser

class KycDocument(models.Model):
    DOCUMENT_TYPE = (
        ('citizenship', 'Citizenship Card'),
        ('driving_license', 'Driving License'),
        ('national_id', 'National ID'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE)
    document_image = models.ImageField(upload_to='kyc_docs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, null=True)
    ocr_raw_text = models.TextField(blank=True, null=True)
    phash_value = models.CharField(max_length=64, blank=True, null=True) 
    is_flagged = models.BooleanField(default=False)                       
    flag_reason = models.TextField(blank=True, null=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_docs'
    )

    def __str__(self):
        return f"{self.user.username} - {self.document_type}"