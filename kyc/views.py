from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import KycDocument
from .forms import KycUploadForm
from .ocr import extract_text, parse_citizenship
from users.models import Profile

@login_required
def upload_kyc(request):
    if request.user.role == 'staff' or request.user.is_superuser:
        messages.error(request, 'Staff members do not need to submit KYC.')
        return redirect('staff_dashboard')

    existing_docs = KycDocument.objects.filter(user=request.user)
    ocr_data = None

    if request.method == 'POST':
        form = KycUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()

            # Run OCR if citizenship card
            if doc.document_type == 'citizenship':
                try:
                    text = extract_text(doc.document_image.path)
                    ocr_data = parse_citizenship(text)
                    doc.ocr_raw_text = text
                    doc.save()
                    messages.success(request, 'Document uploaded! OCR extracted your details.')
                except Exception as e:
                    messages.warning(request, f'Document uploaded but OCR failed: {str(e)}')
            else:
                messages.success(request, 'Document uploaded successfully!')

            # Update profile KYC status
            profile = request.user.profile
            profile.kyc_status = 'submitted'
            profile.save()

            return render(request, 'kyc/upload.html', {
                'form': KycUploadForm(),
                'existing_docs': KycDocument.objects.filter(user=request.user),
                'ocr_data': ocr_data,
            })
    else:
        form = KycUploadForm()

    return render(request, 'kyc/upload.html', {
        'form': form,
        'existing_docs': existing_docs,
        'ocr_data': ocr_data,
    })