import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Donation

@login_required
def map_view(request):
    donations = Donation.objects.filter(status='pending')
    
    donations_data = []
    default_lat, default_lng = 40.7128, -74.0060 # NY fallback
    
    for don in donations:
        donations_data.append({
            'id': don.id,
            'food_name': don.food_name,
            'quantity': don.quantity,
            'location': don.location,
            'latitude': don.latitude or default_lat, # If no lat/lng provided, use default for demo
            'longitude': don.longitude or default_lng,
            'expiry_time': don.expiry_time.strftime("%b %d, %Y %I:%M %p"),
            'role': request.user.role
        })
        # Slightly offset default markers for demo purposes if they have no lat/lng
        if not don.latitude:
            default_lat += 0.01
            default_lng += 0.01
            
    return render(request, 'map.html', {
        'donations_json': json.dumps(donations_data)
    })
