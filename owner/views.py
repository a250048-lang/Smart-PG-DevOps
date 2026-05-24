from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from .form import PGPropertyForm, RoomForm,PGPropertyImageForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
import re
from .models import PGProperty, Room, Hostel, HostelRule, Booking,PGPropertyImage,HostelImage


def owner_dashboard(request):
    owner_properties = PGProperty.objects.filter(owner=request.user)
    total_properties = owner_properties.count()
    verified_properties = owner_properties.filter(is_verified=True).count()
    total_rooms = Room.objects.filter(pg_property__owner=request.user).count()

    total_bookings = Booking.objects.filter(
        Q(room__pg_property__owner=request.user) |
        Q(hostel__owner=request.user)
    ).count()

    pending_bookings = Booking.objects.filter(
        Q(room__pg_property__owner=request.user) |
        Q(hostel__owner=request.user),
        status='pending'
    ).count()

    context = {
        'total_properties': total_properties,
        'verified_properties': verified_properties,
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings
    }
    return render(request, 'owner/owner_dashboard.html',context)

def manage_properties(request):
    pg_properties = PGProperty.objects.filter(owner=request.user).order_by('-created_at')
    hostels = Hostel.objects.filter(owner=request.user).order_by('-created_at')

    # Handle PG actions
    if request.method == 'POST':
        action = request.POST.get('action')
        property_type = request.POST.get('property_type')
        property_id = request.POST.get('property_id')

        # ⭐ For PG
        if property_type == "pg":
            property_obj = get_object_or_404(PGProperty, id=property_id, owner=request.user)

        # ⭐ For Hostel
        elif property_type == "hostel":
            property_obj = get_object_or_404(Hostel, id=property_id, owner=request.user)

        # Delete
        if action == 'delete':
            property_obj.delete()
            messages.success(request, 'Property deleted successfully!')

        # Activate / Deactivate
        elif action == 'toggle_active':
            property_obj.is_active = not property_obj.is_active
            property_obj.save()
            messages.success(request, f'Property {"activated" if property_obj.is_active else "deactivated"} successfully!')

        return redirect('owner:manage_properties')

    return render(request, 'owner/manage_properties.html', {
        'pg_properties': pg_properties,
        'hostels': hostels
    })

@login_required
def select_property_type(request):
    if request.method == 'POST':
        property_type = request.POST.get('property_type')
        if property_type == 'pg':
            return redirect('owner:add_pg')
        elif property_type == 'hostel':
            return redirect('owner:add_hostel')
        elif property_type == 'room':
            messages.info(request, 'Room registration feature coming soon!')
            return redirect('core:manage_properties')
        else:
            messages.error(request, 'Please select a property type.')
    return render(request, 'owner/select_property_type.html')

@login_required
def add_pg_property(request):
    if request.method == 'POST':
        form = PGPropertyForm(request.POST, request.FILES)
        img_form = PGPropertyImageForm(request.POST, request.FILES)

        if form.is_valid():
            pg = form.save(commit=False)
            pg.owner = request.user
            pg.save()

            # Save multiple gallery images
            images = request.FILES.getlist('image')
            for img in images:
                PGPropertyImage.objects.create(pg_property=pg, image=img)

            messages.success(
                request,
                f'PG "{pg.name}" added successfully! Now add rooms to your property.'
            )
            return redirect('owner:add_rooms', pg_id=pg.id)

    else:
        form = PGPropertyForm()
        img_form = PGPropertyImageForm()

    return render(request, 'owner/add_pg.html', {
        'form': form,
        'img_form': img_form
    })


@login_required
def add_rooms(request, pg_id):
    pg_property = get_object_or_404(PGProperty, id=pg_id, owner=request.user)

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.pg_property = pg_property
            room.save()
            messages.success(request, f'Room {room.room_number} added successfully!')
            return redirect('owner:add_rooms', pg_id=pg_id)
    else:
        form = RoomForm()

    # Get existing rooms for this PG
    existing_rooms = Room.objects.filter(pg_property=pg_property)

    context = {
        'form': form,
        'pg_property': pg_property,
        'existing_rooms': existing_rooms,
    }

    return render(request, 'owner/add_rooms.html', context)

@login_required
def add_hostels(request):
    if request.method == "POST":

        rules = request.POST.getlist("rules[]")

        hostel = Hostel.objects.create(
            owner=request.user,
            name=request.POST.get('hostel_name'),
            street=request.POST.get('street'),
            area=request.POST.get('area'),
            village=request.POST.get('village'),
            city=request.POST.get('city'),
            district=request.POST.get('district'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            gender=request.POST.get('gender'),
            wifi='wifi' in request.POST,
            food='food' in request.POST,
            laundry='laundry' in request.POST,
            gym='gym' in request.POST,
            security='security' in request.POST,
            housekeeping='housekeeping' in request.POST,
            ro_water='ro_water' in request.POST,
            games='games' in request.POST,
            hotwater='hotwater' in request.POST,
            parking='parking' in request.POST,
            wardrobe='wardrobe' in request.POST,
            studytable='studytable' in request.POST,
            description=request.POST.get('description'),
            title_image=request.FILES.get("title_image")
        )

        # Save rules
        for r in rules:
            HostelRule.objects.create(hostel=hostel, rule=r)

        # Save multiple gallery images
        gallery_files = request.FILES.getlist('gallery_images')

        for image in gallery_files:
            HostelImage.objects.create(hostel=hostel, image=image)

        return redirect("owner:add_hostel")

    return render(request, "owner/add_Hostel.html")


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":

        # Check availability
        if room.available_beds <= 0:
            messages.error(request, "Sorry, this room is fully booked.")
            return redirect('core_urls:detailView', id=room.pg_property.id)

        already = Booking.objects.filter(
            user=request.user,
            room=room,
            status='pending'
        ).exists()

        if already:
            messages.warning(request, "You already have a pending booking for this room.")
            return redirect('core_urls:detailView', id=room.pg_property.id)

        # Extraction
        full_name = request.POST.get("full_name", "").strip()
        age_str = request.POST.get("age", "").strip()
        gender = request.POST.get("gender", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        identity_proof = request.FILES.get("identity_proof")

        # Validation Logic
        errors = []
        
        # 1. Full Name
        if not full_name:
            errors.append("Full Name is mandatory.")
        elif not re.match(r"^[A-Za-z\s]+$", full_name):
            errors.append("Full Name should only contain alphabets and spaces.")
        elif len(full_name) < 2:
            errors.append("Full Name must be at least 2 characters long.")

        # 2. Age
        try:
            age = int(age_str)
            if age < 16 or age > 80:
                errors.append("Age must be between 16 and 80.")
        except ValueError:
            errors.append("Age must be a valid number.")

        # 3. Gender
        if gender not in ['Male', 'Female', 'Other']:
            errors.append("Please select a valid gender.")

        # 4. Mobile Number
        if not re.match(r"^[6789]\d{9}$", phone):
            errors.append("Mobile number must be 10 digits and start with 6, 7, 8, or 9.")

        # 5. Email
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            errors.append("Only @gmail.com email addresses are allowed.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('core_urls:detailView', id=room.pg_property.id)

        # Validation for Identity Proof
        identity_proof = request.FILES.get("identity_proof")
        if not identity_proof:
            messages.error(request, "Identity proof is required.")
            return redirect('core_urls:detailView', id=room.pg_property.id)
            
        if not identity_proof.name.lower().endswith(('.jpg', '.jpeg')):
            messages.error(request, "Only JPEG files are allowed for identity proof.")
            return redirect('core_urls:detailView', id=room.pg_property.id)
            
        if identity_proof.size > 3 * 1024 * 1024:
            messages.error(request, "Identity proof file size must be less than 3MB.")
            return redirect('core_urls:detailView', id=room.pg_property.id)

        booking = Booking.objects.create(
            user=request.user,
            room=room,
            status='pending',
            full_name=full_name,
            age=age,
            gender=gender,
            phone=phone,
            email=email,
            message=message,
            amount=room.price_per_month,
            identity_proof=identity_proof
        )

        messages.success(request, "Booking request submitted successfully! ")
        return redirect('core_urls:detailView', id=room.pg_property.id)

    return redirect("core_urls:detailView", id=room.pg_property.id)

@login_required
def book_hostel(request, hostel_id):
    hostel = get_object_or_404(Hostel, id=hostel_id)

    if request.method == "POST":

        # Extraction
        full_name = request.POST.get("full_name", "").strip()
        age_str = request.POST.get("age", "").strip()
        gender = request.POST.get("gender", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        identity_proof = request.FILES.get("identity_proof")

        # Validation Logic
        errors = []
        
        # 1. Full Name
        if not full_name:
            errors.append("Full Name is mandatory.")
        elif not re.match(r"^[A-Za-z\s]+$", full_name):
            errors.append("Full Name should only contain alphabets and spaces.")
        elif len(full_name) < 2:
            errors.append("Full Name must be at least 2 characters long.")

        # 2. Age
        try:
            age = int(age_str)
            if age < 16 or age > 80:
                errors.append("Age must be between 16 and 80.")
        except ValueError:
            errors.append("Age must be a valid number.")

        # 3. Gender
        if gender not in ['Male', 'Female', 'Other']:
            errors.append("Please select a valid gender.")

        # 4. Mobile Number
        if not re.match(r"^[6789]\d{9}$", phone):
            errors.append("Mobile number must be 10 digits and start with 6, 7, 8, or 9.")

        # 5. Email
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            errors.append("Only @gmail.com email addresses are allowed.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('core_urls:hostel_detail', id=hostel.id)

        # Validation for Identity Proof
        identity_proof = request.FILES.get("identity_proof")
        if not identity_proof:
            messages.error(request, "Identity proof is required.")
            return redirect('core_urls:hostel_detail', id=hostel.id)
            
        if not identity_proof.name.lower().endswith(('.jpg', '.jpeg')):
            messages.error(request, "Only JPEG files are allowed for identity proof.")
            return redirect('core_urls:hostel_detail', id=hostel.id)
            
        if identity_proof.size > 3 * 1024 * 1024:
            messages.error(request, "Identity proof file size must be less than 3MB.")
            return redirect('core_urls:hostel_detail', id=hostel.id)

        booking = Booking.objects.create(
            user=request.user,
            hostel=hostel,
            status='pending',
            full_name=full_name,
            age=age,
            gender=gender,
            phone=phone,
            email=email,
            message=message,
            identity_proof=identity_proof
        )

        messages.success(request, "Hostel booking request submitted successfully!")
        return redirect('core_urls:hostel_detail', id=hostel.id)

    return redirect('core_urls:hostel_detail', id=hostel.id)



def manage_bookings(request):
    pg_bookings = Booking.objects.filter(
        room__pg_property__owner=request.user,
        room__isnull=False
    ).select_related("room", "room__pg_property", "user").order_by("-booking_date")

    # Hostel bookings
    hostel_bookings = Booking.objects.filter(
        hostel__isnull=False,
        hostel__owner=request.user
    ).select_related("hostel", "user").order_by("-booking_date")

    # Handle confirm / cancel actions
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        action = request.POST.get("action")

        booking = get_object_or_404(
            Booking,
            id=booking_id
        )

        if action == "confirm":
            booking.status = "confirmed"
            booking.save()
            
            # Send confirmation email
            subject = 'Booking Confirmed - Smart PG/Hostel System'
            message = f'Hello {booking.full_name or booking.user.username},\n\nYour booking for {booking.room or booking.hostel} has been CONFIRMED by the owner.\n\nThank you for choosing us!'
            recipient_list = [booking.email] if booking.email else [booking.user.email]
            
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                messages.success(request, f"Booking verified and confirmation email sent to {recipient_list[0]}")
            except Exception as e:
                messages.warning(request, f"Booking verified but failed to send email: {e}")

        elif action == "cancel":
            booking.status = "cancelled"
            booking.save()

            # Send cancellation email
            subject = 'Booking Warning/Rejected - Smart PG/Hostel System'
            message = f'Hello {booking.full_name or booking.user.username},\n\nYour booking for {booking.room or booking.hostel} has been CANCELLED/REJECTED by the owner.\n\nPlease contact the owner for more details or try booking another property.'
            recipient_list = [booking.email] if booking.email else [booking.user.email]
            
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                messages.success(request, f"Booking cancelled and rejection email sent to {recipient_list[0]}")
            except Exception as e:
                messages.warning(request, f"Booking cancelled but failed to send email: {e}")

        return redirect("owner:manage_bookings")

    return render(request, "owner/manage_bookings.html", {
        "pg_bookings": pg_bookings,
        "hostel_bookings": hostel_bookings,
    })