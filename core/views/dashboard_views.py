from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from core.models import Donation, FoodRequest, Delivery, User, Feedback
from core.forms import DonationForm

@login_required
def donor_dashboard(request):
    donations = request.user.donations.all().order_by('-created_at')
    return render(request, 'dashboards/donor.html', {'donations': donations})

@login_required
def ngo_dashboard(request):
    available_donations = Donation.objects.filter(status='pending').order_by('-created_at')
    my_deliveries = request.user.deliveries.all().order_by('-donation__created_at')
    return render(request, 'dashboards/ngo.html', {
        'available_donations': available_donations,
        'my_deliveries': my_deliveries
    })

@login_required
def needy_dashboard(request):
    available_donations = Donation.objects.filter(status='pending').exclude(requests__needy_person=request.user).order_by('-created_at')
    my_requests = request.user.food_requests.all().order_by('-requested_at')
    return render(request, 'dashboards/needy.html', {
        'available_donations': available_donations,
        'my_requests': my_requests
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return render(request, 'home.html') # Or raise 403
    
    pending_ngos = User.objects.filter(role='ngo', is_approved=False)
    stats = {
        'total_donations': Donation.objects.count(),
        'total_users': User.objects.count(),
        'food_delivered': Donation.objects.filter(status='delivered').count(),
    }
    return render(request, 'dashboards/admin.html', {
        'pending_ngos': pending_ngos,
        'stats': stats
    })

@login_required
def post_donation(request):
    if request.user.role != 'donor':
        return redirect('home')
        
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            messages.success(request, 'Food donation posted successfully!')
            return redirect('donor_dashboard')
    else:
        form = DonationForm()
        
    return render(request, 'dashboards/post_donation.html', {'form': form})

@login_required
@transaction.atomic
def accept_donation(request, donation_id):
    if request.user.role != 'ngo': return redirect('home')
    
    donation = get_object_or_404(Donation, id=donation_id, status='pending')
    donation.status = 'accepted'
    donation.save()
    
    # Create Delivery record
    Delivery.objects.create(donation=donation, volunteer=request.user)
    messages.success(request, f'You have accepted to pick up: {donation.food_name}')
    return redirect('ngo_dashboard')

@login_required
@transaction.atomic
def update_delivery(request, delivery_id, status):
    if request.user.role != 'ngo': return redirect('home')
    
    delivery = get_object_or_404(Delivery, id=delivery_id, volunteer=request.user)
    
    if status == 'picked_up':
        delivery.donation.status = 'picked_up'
        delivery.picked_up_at = timezone.now()
        msg = "Marked as Picked Up."
    elif status == 'delivered':
        delivery.donation.status = 'delivered'
        delivery.delivered_at = timezone.now()
        msg = "Marked as Delivered! Thank you."
        
        # Mark any approved FoodRequest for this donation as delivered
        for req in delivery.donation.requests.filter(status='approved'):
            req.status = 'delivered'
            req.save()
        
    delivery.save()
    delivery.donation.save()
    messages.success(request, msg)
    return redirect('ngo_dashboard')

@login_required
def request_food(request, donation_id):
    if request.user.role != 'needy': return redirect('home')
    
    donation = get_object_or_404(Donation, id=donation_id)
    # Check if already requested
    if FoodRequest.objects.filter(needy_person=request.user, donation=donation).exists():
        messages.warning(request, 'You have already requested this food.')
    else:
        FoodRequest.objects.create(
            needy_person=request.user,
            donation=donation,
            status='requested'
        )
        messages.success(request, f'Successfully requested {donation.food_name}. Please wait for updates.')
        
    return redirect('needy_dashboard')

@login_required
def approve_ngo(request, user_id):
    if request.user.role != 'admin' and not request.user.is_superuser: return redirect('home')
    ngo = get_object_or_404(User, id=user_id, role='ngo')
    ngo.is_approved = True
    ngo.save()
    messages.success(request, f'Approved NGO: {ngo.username}')
    return redirect('admin_dashboard')

@login_required
def reject_ngo(request, user_id):
    if request.user.role != 'admin' and not request.user.is_superuser: return redirect('home')
    ngo = get_object_or_404(User, id=user_id, role='ngo')
    ngo.delete()
    messages.success(request, f'Rejected and removed NGO: {ngo.username}')
    return redirect('admin_dashboard')

@login_required
def submit_feedback(request, donation_id):
    if request.method == 'POST' and request.user.role == 'needy':
        donation = get_object_or_404(Donation, id=donation_id)
        rating = request.POST.get('rating')
        if rating:
            Feedback.objects.create(donation=donation, user=request.user, rating=int(rating))
            messages.success(request, 'Thank you for your feedback!')
    return redirect('needy_dashboard')

@login_required
def delete_donation(request, donation_id):
    if request.user.role != 'donor':
        return redirect('home')
    
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user, status='pending')
    donation_name = donation.food_name
    donation.delete()
    
    messages.success(request, f"Successfully deleted donation: {donation_name}")
    return redirect('donor_dashboard')

@login_required
def approve_request(request, request_id):
    if request.user.role != 'donor':
        return redirect('home')
    
    food_request = get_object_or_404(FoodRequest, id=request_id, donation__donor=request.user)
    food_request.status = 'approved'
    food_request.save()
    
    messages.success(request, f"Approved request from {food_request.needy_person.username}!")
    return redirect('donor_dashboard')
