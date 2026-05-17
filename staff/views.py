from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from users.models import CustomUser, Profile

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
    pending_kyc = Profile.objects.filter(kyc_status='pending').count()
    submitted_kyc = Profile.objects.filter(kyc_status='submitted').count()
    approved_kyc = Profile.objects.filter(kyc_status='approved').count()
    rejected_kyc = Profile.objects.filter(kyc_status='rejected').count()
    recent_users = CustomUser.objects.filter(role='end_user').order_by('-date_joined')[:5]

    return render(request, 'staff/dashboard.html', {
        'total_users': total_users,
        'pending_kyc': pending_kyc,
        'submitted_kyc': submitted_kyc,
        'approved_kyc': approved_kyc,
        'rejected_kyc': rejected_kyc,
        'recent_users': recent_users,
    })