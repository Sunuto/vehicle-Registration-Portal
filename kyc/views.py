from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import KycDocument
from .forms import KycUploadForm
from .ocr import extract_text, parse_citizenship
from .phash import compute_phash, check_duplicate
from users.models import Profile

@login_required
def upload_kyc(request):
    if request.user.role == 'staff' or request.user.is_superuser:
        messages.error(request, 'Staff members do not need to submit KYC.')
        return redirect('staff_dashboard')

    existing_docs = KycDocument.objects.filter(user=request.user)
    has_pending = existing_docs.filter(status='pending').exists()
    uploaded_types = list(
        existing_docs.exclude(status='rejected').values_list('document_type', flat=True)
    )
    all_types = ['citizenship', 'driving_license', 'national_id']
    all_uploaded = all(t in uploaded_types for t in all_types)
    ocr_data = None

    if request.method == 'POST':
        if has_pending:
            messages.error(request, 'You have a pending document. Please wait for staff to review it.')
            return redirect('upload_kyc')

        form = KycUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()

            # ── Run pHash fraud detection ──
            try:
                new_hash = compute_phash(doc.document_image.path)
                doc.phash_value = new_hash

                # Compare against ALL other documents in system
                all_other_docs = KycDocument.objects.exclude(id=doc.id)
                is_duplicate, reason, matching_doc = check_duplicate(new_hash, all_other_docs)

                if is_duplicate:
                    doc.is_flagged = True
                    doc.flag_reason = reason
                    messages.warning(request, f'⚠ Document flagged: {reason}')
                else:
                    doc.is_flagged = False

            except Exception as e:
                messages.warning(request, f'pHash check failed: {str(e)}')

            # ── Run OCR if citizenship or national id ──
            if doc.document_type in ['citizenship', 'national_id']:
                try:
                    text = extract_text(doc.document_image.path)
                    ocr_data = parse_citizenship(text)
                    doc.ocr_raw_text = text
                    messages.success(request, 'Document uploaded! OCR extracted your details.')
                except Exception as e:
                    messages.warning(request, f'OCR failed: {str(e)}')
            else:
                messages.success(request, 'Document uploaded successfully!')

            doc.save()

            # Update profile KYC status
            profile = request.user.profile
            profile.kyc_status = 'submitted'
            profile.save()

            existing_docs = KycDocument.objects.filter(user=request.user)
            has_pending = existing_docs.filter(status='pending').exists()
            uploaded_types = list(
                existing_docs.exclude(status='rejected').values_list('document_type', flat=True)
            )
            all_uploaded = all(t in uploaded_types for t in all_types)

            return render(request, 'kyc/upload.html', {
                'form': KycUploadForm(user=request.user),
                'existing_docs': existing_docs,
                'ocr_data': ocr_data,
                'all_uploaded': all_uploaded,
                'uploaded_types': uploaded_types,
                'has_pending': has_pending,
            })
    else:
        form = KycUploadForm(user=request.user)

    return render(request, 'kyc/upload.html', {
        'form': form,
        'existing_docs': existing_docs,
        'ocr_data': ocr_data,
        'all_uploaded': all_uploaded,
        'uploaded_types': uploaded_types,
        'has_pending': has_pending,
    })