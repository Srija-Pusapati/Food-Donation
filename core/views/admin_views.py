from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from core.models import Donation, FoodRequest, Delivery
from core.decorators import role_required

User = get_user_model()

@role_required(allowed_roles=['admin'])
def admin_dashboard(request):
    pending_ngos = User.objects.filter(role='ngo', is_approved=False)
    
    stats = {
        'total_users': User.objects.count(),
        'total_donations': Donation.objects.count(),
        'total_requests': FoodRequest.objects.count(),
        'total_deliveries': Delivery.objects.count(),
    }
    
    return render(request, 'dashboards/admin.html', {
        'pending_ngos': pending_ngos,
        'stats': stats
    })

@role_required(allowed_roles=['admin'])
def admin_manage_users(request):
    donors = User.objects.filter(role='donor')
    needy = User.objects.filter(role='needy_person')
    ngos = User.objects.filter(role='ngo')
    
    return render(request, 'dashboards/admin_users.html', {
        'donors': donors,
        'needy': needy,
        'ngos': ngos
    })

@role_required(allowed_roles=['admin'])
def admin_user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Don't let admins deactivate themselves easily this way
    if user == request.user:
        messages.error(request, "You cannot deactivate yourself.")
        return redirect('admin_manage_users')
        
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_manage_users')

@role_required(allowed_roles=['admin'])
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('admin_manage_users')
        
    username = user.username
    user.delete()
    messages.success(request, f'User {username} has been deleted.')
    return redirect('admin_manage_users')

@role_required(allowed_roles=['admin'])
def admin_monitor_donations(request):
    donations = Donation.objects.all().order_by('-created_at')
    return render(request, 'dashboards/admin_donations.html', {'donations': donations})

@role_required(allowed_roles=['admin'])
def admin_monitor_requests(request):
    requests = FoodRequest.objects.all().order_by('-requested_at')
    return render(request, 'dashboards/admin_requests.html', {'requests': requests})

@role_required(allowed_roles=['admin'])
def admin_monitor_deliveries(request):
    deliveries = Delivery.objects.all().order_by('-donation__created_at')
    return render(request, 'dashboards/admin_deliveries.html', {'deliveries': deliveries})

@role_required(allowed_roles=['admin'])
def approve_ngo(request, user_id):
    ngo = get_object_or_404(User, id=user_id, role='ngo')
    ngo.is_approved = True
    ngo.save()
    messages.success(request, f'Approved NGO: {ngo.username}')
    return redirect('admin_dashboard')

@role_required(allowed_roles=['admin'])
def reject_ngo(request, user_id):
    ngo = get_object_or_404(User, id=user_id, role='ngo')
    ngo.delete()
    messages.success(request, f'Rejected and removed NGO: {ngo.username}')
    return redirect('admin_dashboard')
