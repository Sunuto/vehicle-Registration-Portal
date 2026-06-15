from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from users.models import CustomUser, Profile
from kyc.models import KycDocument
from vehicles.models import Vehicle
from kyc.emails import send_kyc_status_email
from vehicles.emails import send_vehicle_status_email

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'staff' and not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    wrapper.__wrapped__ = view_func
    return wrapper

@login_required
@staff_required
def staff_dashboard(request):
    total_users = CustomUser.objects.filter(role='end_user').count()
    pending_kyc = Profile.objects.filter(kyc_status='pending', user__role='end_user').count()
    submitted_kyc = Profile.objects.filter(kyc_status='submitted', user__role='end_user').count()
    approved_kyc = Profile.objects.filter(kyc_status='approved', user__role='end_user').count()
    rejected_kyc = Profile.objects.filter(kyc_status='rejected', user__role='end_user').count()
    recent_users = CustomUser.objects.filter(role='end_user').order_by('-date_joined')[:5]

    return render(request, 'staff/dashboard.html', {
        'total_users': total_users,
        'pending_kyc': pending_kyc,
        'submitted_kyc': submitted_kyc,
        'approved_kyc': approved_kyc,
        'rejected_kyc': rejected_kyc,
        'recent_users': recent_users,
    })

@login_required
@staff_required
def kyc_review_list(request):
    documents = KycDocument.objects.all().order_by('-uploaded_at')
    status_filter = request.GET.get('status', '')
    user_filter = request.GET.get('user', '')

    if status_filter:
        documents = documents.filter(status=status_filter)
    if user_filter:
        documents = documents.filter(user__username=user_filter)

    # Show only latest document per user per type
    seen = set()
    latest_docs = []
    for doc in documents:
        key = (doc.user_id, doc.document_type)
        if key not in seen:
            seen.add(key)
            latest_docs.append(doc)

    return render(request, 'staff/kyc_review.html', {
        'documents': latest_docs,
        'status_filter': status_filter,
        'user_filter': user_filter,
    })

@login_required
@staff_required
def kyc_review_detail(request, doc_id):
    doc = get_object_or_404(KycDocument, id=doc_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')

        if action == 'approve':
            doc.status = 'approved'
            doc.remarks = remarks
            doc.reviewed_by = request.user
            doc.reviewed_at = timezone.now()
            doc.save()

            # Get latest doc per document type
            user_docs = KycDocument.objects.filter(user=doc.user)
            seen_types = set()
            latest_docs = []
            for d in user_docs.order_by('-uploaded_at'):
                if d.document_type not in seen_types:
                    seen_types.add(d.document_type)
                    latest_docs.append(d)

            # If any latest doc is approved → grant KYC
            has_approved = any(d.status == 'approved' for d in latest_docs)
            if has_approved:
                doc.user.profile.kyc_status = 'approved'
                doc.user.profile.save()

            send_kyc_status_email(doc, 'approved')
            messages.success(request, f'Document approved for {doc.user.username}!')

        elif action == 'reject':
            doc.status = 'rejected'
            doc.remarks = remarks
            doc.reviewed_by = request.user
            doc.reviewed_at = timezone.now()
            doc.save()

            # Check if user still has any approved latest docs
            user_docs = KycDocument.objects.filter(user=doc.user)
            seen_types = set()
            latest_docs = []
            for d in user_docs.order_by('-uploaded_at'):
                if d.document_type not in seen_types:
                    seen_types.add(d.document_type)
                    latest_docs.append(d)

            has_approved = any(d.status == 'approved' for d in latest_docs)
            if has_approved:
                doc.user.profile.kyc_status = 'approved'
            else:
                doc.user.profile.kyc_status = 'rejected'
            doc.user.profile.save()

            send_kyc_status_email(doc, 'rejected')
            messages.error(request, f'Document rejected for {doc.user.username}.')

        return redirect('kyc_review_list')

    return render(request, 'staff/kyc_review_detail.html', {'doc': doc})

@login_required
@staff_required
def users_list(request):
    users = CustomUser.objects.filter(role='end_user').order_by('-date_joined')
    return render(request, 'staff/users_list.html', {'users': users})

@login_required
@staff_required
def vehicles_list(request):
    vehicles = Vehicle.objects.all().order_by('-submitted_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    return render(request, 'staff/vehicles_list.html', {
        'vehicles': vehicles,
        'status_filter': status_filter,
    })

@login_required
@staff_required
def vehicle_review(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')

        if action == 'approve':
            vehicle.status = 'approved'
            vehicle.remarks = remarks
            vehicle.reviewed_by = request.user
            vehicle.reviewed_at = timezone.now()
            vehicle.save()
            send_vehicle_status_email(vehicle, 'approved')
            messages.success(request, f'Vehicle approved for {vehicle.owner.username}!')

        elif action == 'reject':
            vehicle.status = 'rejected'
            vehicle.remarks = remarks
            vehicle.reviewed_by = request.user
            vehicle.reviewed_at = timezone.now()
            vehicle.save()
            send_vehicle_status_email(vehicle, 'rejected')
            messages.error(request, f'Vehicle rejected for {vehicle.owner.username}.')

        return redirect('staff_vehicles_list')

    return render(request, 'staff/vehicle_review.html', {'vehicle': vehicle})