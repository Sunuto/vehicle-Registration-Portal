from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Profile
from .forms import RegisterForm, ProfileEditForm
from vehicles.models import Vehicle

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    vehicles = Vehicle.objects.filter(owner=request.user) if request.user.role == 'end_user' else []

    # Build timeline events
    timeline = []
    if request.user.role == 'end_user':
        # Account created
        timeline.append({
            'icon': '👤',
            'title': 'Account Created',
            'description': f'Registered as {request.user.username}',
            'date': request.user.date_joined,
            'status': 'done',
        })

        # KYC documents
        from kyc.models import KycDocument
        kyc_docs = KycDocument.objects.filter(user=request.user).order_by('uploaded_at')
        for doc in kyc_docs:
            timeline.append({
                'icon': '📄',
                'title': f'{doc.get_document_type_display()} Uploaded',
                'description': 'Submitted for verification',
                'date': doc.uploaded_at,
                'status': 'done',
            })
            if doc.status == 'approved':
                timeline.append({
                    'icon': '✅',
                    'title': f'{doc.get_document_type_display()} Approved',
                    'description': doc.remarks or 'Verified by staff',
                    'date': doc.reviewed_at,
                    'status': 'done',
                })
            elif doc.status == 'rejected':
                timeline.append({
                    'icon': '❌',
                    'title': f'{doc.get_document_type_display()} Rejected',
                    'description': doc.remarks or 'Did not pass verification',
                    'date': doc.reviewed_at,
                    'status': 'rejected',
                })
            elif doc.status == 'pending':
                timeline.append({
                    'icon': '⏳',
                    'title': f'{doc.get_document_type_display()} Pending Review',
                    'description': 'Waiting for staff approval',
                    'date': None,
                    'status': 'pending',
                })

        # Vehicles
        for vehicle in vehicles:
            timeline.append({
                'icon': '🚗',
                'title': f'{vehicle.make} {vehicle.model} Registered',
                'description': f'Application submitted for {vehicle.year} {vehicle.color} {vehicle.get_vehicle_type_display()}',
                'date': vehicle.submitted_at,
                'status': 'done',
            })
            if vehicle.status == 'approved':
                timeline.append({
                    'icon': '🏁',
                    'title': f'{vehicle.make} {vehicle.model} Approved',
                    'description': vehicle.remarks or 'Registration complete',
                    'date': vehicle.reviewed_at,
                    'status': 'done',
                })
            elif vehicle.status == 'rejected':
                timeline.append({
                    'icon': '❌',
                    'title': f'{vehicle.make} {vehicle.model} Rejected',
                    'description': vehicle.remarks or 'Application rejected',
                    'date': vehicle.reviewed_at,
                    'status': 'rejected',
                })
            elif vehicle.status == 'pending':
                timeline.append({
                    'icon': '⏳',
                    'title': f'{vehicle.make} {vehicle.model} Pending Review',
                    'description': 'Waiting for staff approval',
                    'date': None,
                    'status': 'pending',
                })

        # Sort by date (None dates go last)
        timeline.sort(key=lambda x: x['date'] or request.user.date_joined, reverse=True)

    return render(request, 'users/dashboard.html', {
        'user': request.user,
        'profile': profile,
        'vehicles': vehicles,
        'timeline': timeline,
    })

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})