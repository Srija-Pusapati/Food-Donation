from django.shortcuts import render
from core.models import Donation, FoodRequest


def home(request):
    # Get latest donations
    recent_donations = Donation.objects.filter(status='pending').order_by('-created_at')[:3]

    # Statistics data
    stats = {
        "total_donations": Donation.objects.count(),
        "delivered": Donation.objects.filter(status="delivered").count(),
        "requests": FoodRequest.objects.count(),
    }

    # Context dictionary
    context = {
        "recent_donations": recent_donations,
        "stats": stats
    }

    return render(request, "home.html", context)