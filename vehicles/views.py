from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, VehicleDocument
from .forms import VehicleRegistrationForm, VehicleDocumentForm

@login_required
def register_vehicle(request):
    # Block staff
    if request.user.role == 'staff' or request.user.is_superuser:
        messages.error(request, 'Staff members cannot register vehicles.')
        return redirect('staff_dashboard')

    # Block if KYC not approved
    if request.user.profile.kyc_status != 'approved':
        messages.error(request, 'You must complete KYC verification before registering a vehicle.')
        return redirect('dashboard')

    # Only block if there is a PENDING vehicle
    pending_vehicle = Vehicle.objects.filter(
        owner=request.user,
        status='pending'
    ).first()

    if pending_vehicle:
        messages.warning(request, 'You have a vehicle registration pending approval. Please wait for staff to review it.')
        return redirect('my_vehicles')

    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, 'Vehicle registered successfully! Awaiting staff approval.')
            return redirect('my_vehicles')
    else:
        form = VehicleRegistrationForm()

    return render(request, 'vehicles/register.html', {'form': form})

@login_required
def my_vehicles(request):
    if request.user.role == 'staff' or request.user.is_superuser:
        return redirect('staff_dashboard')
    vehicles = Vehicle.objects.filter(owner=request.user).order_by('-submitted_at')
    pending_vehicle = vehicles.filter(status='pending').first()
    return render(request, 'vehicles/my_vehicles.html', {
        'vehicles': vehicles,
        'pending_vehicle': pending_vehicle,
    })