from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import KycDocument
from .forms import KycUploadForm
from users.models import Profile

@login_required
def upload_kyc(request):
    # Block staff from accessing KYC upload
    if request.user.role == 'staff' or request.user.is_superuser:
        messages.error(request, 'Staff members do not need to submit KYC.')
        return redirect('staff_dashboard')

    existing_docs = KycDocument.objects.filter(user=request.user)

    if request.method == 'POST':
        form = KycUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()

            profile = request.user.profile
            profile.kyc_status = 'submitted'
            profile.save()

            messages.success(request, 'Document uploaded successfully!')
            return redirect('upload_kyc')
    else:
        form = KycUploadForm()

    return render(request, 'kyc/upload.html', {
        'form': form,
        'existing_docs': existing_docs,
    })