from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Vehicle
from .forms import VehicleRegistrationForm
from django.http import HttpResponse
from .pdf import generate_vehicle_registration_slip


@login_required
def register_vehicle(request):

    # STAFF BLOCK
    if request.user.role == "staff" or request.user.is_superuser:
        messages.error(request, "Staff cannot register vehicles.")
        return redirect("staff_dashboard")

    # SAFE KYC CHECK
    profile = getattr(request.user, "profile", None)
    if not profile or profile.kyc_status != "approved":
        messages.error(request, "KYC must be approved first.")
        return redirect("dashboard")

    # BLOCK PENDING VEHICLE
    if Vehicle.objects.filter(owner=request.user, status="pending").exists():
        messages.warning(request, "You already have a pending vehicle.")
        return redirect("my_vehicles")

    if request.method == "POST":
        form = VehicleRegistrationForm(
        request.POST,
        request.FILES
        )
        if form.is_valid():

            with transaction.atomic():
                vehicle = form.save(commit=False)
                vehicle.owner = request.user
                vehicle.status = "pending"
                vehicle.save()

            messages.success(request, "Vehicle submitted for approval.")
            return redirect("my_vehicles")

    else:
        form = VehicleRegistrationForm()

    return render(request, "vehicles/register.html", {"form": form})


@login_required
def my_vehicles(request):

    if request.user.role == "staff" or request.user.is_superuser:
        return redirect("staff_dashboard")

    vehicles = Vehicle.objects.filter(owner=request.user).order_by("-submitted_at")

    return render(request, "vehicles/my_vehicles.html", {
        "vehicles": vehicles,
        "pending_vehicle": vehicles.filter(status="pending").first(),
    })
    
@login_required
def download_registration_slip(request, vehicle_id):
    from django.shortcuts import get_object_or_404
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)

    # Only allow download if approved
    if vehicle.status != 'approved':
        messages.error(request, 'Registration slip is only available for approved vehicles.')
        return redirect('my_vehicles')

    buffer = generate_vehicle_registration_slip(vehicle)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="VEH-{vehicle.id:06d}-registration-slip.pdf"'
    return response