from django.shortcuts import render, get_object_or_404, redirect
from itertools import chain
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from owner.models import PGProperty, Hostel, Room,Booking
from .models import ContactMessage
# Create your views here.

def index(request):
    pgs = PGProperty.objects.filter(is_active=True, is_verified=True)
    hostels = Hostel.objects.filter(is_active=True, is_verified=True)

    combined_list = []

    # normalize PGs
    for pg in pgs:
        combined_list.append({
            "type": "pg",
            "id": pg.id,
            "name": pg.name,
            "gender": pg.gender_availability,
            "city": pg.city,
            "area": pg.area_road,
            "image": pg.title_image,  
            "wifi": pg.has_wifi,
            "food": pg.has_food,
            "url": reverse("core_urls:detailView", args=[pg.id]),
        })

    # normalize Hostels
    for hostel in hostels:
        combined_list.append({
            "type": "hostel",
            "id": hostel.id,
            "name": hostel.name,
            "gender":hostel.gender,
            "city": hostel.city,
            "area":hostel.area,
            "image": hostel.title_image,
            "wifi": hostel.wifi,
            "food": hostel.food,
            "url": reverse("core_urls:hostel_detail", args=[hostel.id]),
        })

    return render(request, "core/index.html",{
        "properties": combined_list
    })

def home(request):
    feedbacks = ContactMessage.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, "core/Home.html", {'feedbacks': feedbacks})


def detailView(request, id):
    pg = get_object_or_404(PGProperty, id=id)

    rooms = pg.rooms.all()   # because of related_name='rooms'
    
    pending_room_ids = []
    if request.user.is_authenticated:
        pending_room_ids = Booking.objects.filter(
            user=request.user,
            room__pg_property=pg,
            status='pending'
        ).values_list('room_id', flat=True)

    context = {
        "pg": pg,
        "rooms": rooms,
        "pending_room_ids": list(pending_room_ids)
    }
    return render(request, 'core/detailView.html', context)

def hostel_detail(request, id):
    hostel = get_object_or_404(Hostel, id=id)

    rules = hostel.rules.all()  

    context = {
        "hostel": hostel,
        "rules": rules
    }
    return render(request, "core/hostel_detail.html", context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        rating = request.POST.get('rating', 0)

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
            rating=rating
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('core:contact')

    return render(request, 'core/contact.html')

def search_pgs(request):
    city = request.GET.get('city', '').strip()
    area = request.GET.get('area', '').strip()
   

    # Initial Querysets
    pg_qs = PGProperty.objects.filter(is_verified=True, is_active=True)
    hostel_qs = Hostel.objects.filter(is_verified=True, is_active=True)

    # Apply City Filter
    if city:
        pg_qs = pg_qs.filter(city__icontains=city)
        hostel_qs = hostel_qs.filter(city__icontains=city)

    # Split into Area and City results
    area_pgs = pg_qs.none()
    city_pgs = pg_qs
    area_hostels = hostel_qs.none()
    city_hostels = hostel_qs

    if area:
        area_pgs = pg_qs.filter(
            Q(area_road__icontains=area) | 
            Q(village__icontains=area) | 
            Q(street__icontains=area)
        )
        city_pgs = pg_qs.exclude(id__in=area_pgs.values_list('id', flat=True))

        area_hostels = hostel_qs.filter(
            Q(area__icontains=area) | 
            Q(village__icontains=area) | 
            Q(street__icontains=area)
        )
        city_hostels = hostel_qs.exclude(id__in=area_hostels.values_list('id', flat=True))


    # Helper function to format results
    def format_results(pg_list, hostel_list):
        results = []
        for pg in pg_list:
            results.append({
                'property': {
                    'id': pg.id,
                    'name': pg.name,
                    'city': pg.city,
                    'area': pg.area_road or pg.village or pg.street,
                    'image': pg.title_image,
                    'has_wifi': pg.has_wifi,
                    'has_food': pg.has_food,
                },
                'type': 'pg',
                'gender': pg.gender_availability
            })
        for h in hostel_list:
            results.append({
                'property': {
                    'id': h.id,
                    'name': h.name,
                    'city': h.city,
                    'area': h.area or h.village or h.street,
                    'image': h.title_image,
                    'has_wifi': h.wifi,
                    'has_food': h.food,
                },
                'type': 'hostel',
                'gender': h.gender 
            })
        return results

    formatted_area_data = format_results(area_pgs, area_hostels)
    formatted_city_data = format_results(city_pgs, city_hostels)

    return render(request, 'core/search_result.html', {
        'area_data': formatted_area_data,
        'city_data': formatted_city_data,
        'city_name': city,
        'area_name': area
    })

def help_center(request):
    return render(request, 'core/help_center.html')

def terms(request):
    return render(request, 'core/terms.html')

def privacy(request):
    return render(request, 'core/privacy.html')
