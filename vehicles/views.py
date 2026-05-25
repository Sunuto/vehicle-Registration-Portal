from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, VehicleDocument
from .forms import VehicleRegistrationForm, VehicleDocumentForm

@login_required
def register_vehicle(request):
    # Block staff from registering vehicles
    if request.user.role == 'staff' or request.user.is_superuser:
        messages.error(request, 'Staff members cannot register vehicles.')
        return redirect('staff_dashboard')

    # Block if KYC not approved
    if request.user.profile.kyc_status != 'approved':
        messages.error(request, 'You must complete KYC verification before registering a vehicle.')
        return redirect('dashboard')

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
    return render(request, 'vehicles/my_vehicles.html', {'vehicles': vehicles})