from django.db import models
from django.contrib.auth.models import User

class PGProperty(models.Model):
    GENDER_CHOICES = (
        ('Boys', 'Boys PG'),
        ('Girls', 'Girls PG'),
        ('Both Girls & Boys', 'Both Girls & Boys PG '),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_properties')
    name = models.CharField(max_length=200)
    street = models.CharField(max_length=200, blank=True)
    area_road = models.CharField(max_length=200, blank=True)
    village = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    description = models.TextField()
    gender_availability = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Both')
    rules = models.TextField(blank=True, help_text='Rules and regulations for the PG')
    title_image = models.ImageField(upload_to='media/pg_images/title/')
    has_wifi = models.BooleanField(default=False)
    has_food = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_laundry = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_power_backup = models.BooleanField(default=False)
    has_security = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def full_address(self):
        return f"{self.street}, {self.area_road},{self.village}, {self.city}, {self.district}, {self.state} - {self.pincode}"
    
    def __str__(self):
        return self.name    

class PGPropertyImage(models.Model):
    pg_property = models.ForeignKey(
        PGProperty,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to='media/pg_images/gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.pg_property.name}"


class Room(models.Model):
    pg_property = models.ForeignKey(PGProperty, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(help_text="Total beds in this room")
    available_beds = models.IntegerField()
    is_ac = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.room_number} - {self.pg_property.name}"
    
class Booking(models.Model):
    STATUS_CHOICES = (('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'))
    GENDER_CHOICES = (
        ('Male','Male'),
        ('Female','Female'),
        ('Other','Other'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE)
    hostel = models.ForeignKey('Hostel', null=True, blank=True, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    full_name = models.CharField(max_length=150, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    identity_proof = models.ImageField(upload_to='media/identity_proofs/', null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Booking.objects.get(pk=self.pk).status
        else:
            old_status = None

        super().save(*args, **kwargs)
        # ONLY apply bed logic for PG rooms
        if self.room:
            # Restore bed on cancel
            if self.status == 'cancelled' and old_status != 'cancelled':
                self.room.available_beds += 1
                self.room.save()
            # Reduce bed when confirmed
            if self.status == 'confirmed' and old_status != 'confirmed':
                if self.room.available_beds > 0:
                    self.room.available_beds -= 1
                    self.room.save()

    def __str__(self):
        if self.room:
            return f"{self.user.username} - {self.room.pg_property.name} - {self.status}"
        else:
            return f"{self.user.username} - {self.hostel.name} - {self.status}"

class Hostel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_hostels',null=True,
    blank=True)
    GENDER_CHOICES = (
        ('Boys', 'Boys Hostel'),
        ('Girls', 'Girls Hostel'),
        ('Both Girls & Boys', 'Both Girls & Boys Hostel'),
    )

    name = models.CharField(max_length=200)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    village = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    wifi = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    housekeeping = models.BooleanField(default=False)
    ro_water = models.BooleanField(default=False)
    games = models.BooleanField(default=False)
    hotwater = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    wardrobe = models.BooleanField(default=False)
    studytable = models.BooleanField(default=False)
    description = models.TextField()
    title_image = models.ImageField(upload_to="media/hostel_images/title/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class HostelRule(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="rules")
    rule = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.hostel.name} - {self.rule}"
    
class HostelImage(models.Model):
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to="media/hostel_images/gallery/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.hostel.name}"


