import re
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .forms import PasswordResetRequestForm, SetNewPasswordForm
from datetime import datetime, timedelta
from django.utils.timezone import now
from .models import TenantProfile, OwnerProfile
from owner.models import Booking
ALLOWED_FILE_TYPES = ["application/pdf", "image/jpeg", "image/png"]
MAX_FILE_SIZE = 3 * 1024 * 1024  # 3MB
USERNAME_REGEX = r'^[A-Za-z][A-Za-z0-9_.]{3,19}$'

def validate_uploaded_file(file):
    if not file:
        return False

    if file.content_type not in ALLOWED_FILE_TYPES:
        return False

    if file.size > MAX_FILE_SIZE:
        return False

    return True

def owner_register(request):
    if request.method == 'POST':

        role = "Owner" 

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        mobile_number = request.POST['mobile_number']

        identity_proof = request.FILES.get('identity_proof')
        ownership_proof = request.FILES.get('ownership_proof')
        declaration = request.POST.get('declaration')

        if not declaration:
            messages.error(request, "You must accept the declaration")
            return redirect('user:owner_register')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('user:owner_register')

        if len(first_name) < 2:
            messages.error(request, 'First name must be at least 2 characters long')
            return redirect('user:owner_register')

        if len(username) < 2:
            messages.error(request, 'Username must be at least 2 characters long')
            return redirect('user:owner_register')

        if len(last_name) < 2:
            messages.error(request, 'Last name must be at least 2 characters long')
            return redirect('user:owner_register')

        if not email.endswith('@gmail.com'):
            messages.error(request, 'Only Gmail accounts are allowed')
            return redirect('user:owner_register')

        if len(mobile_number) != 10 or not mobile_number.isdigit():
            messages.error(request, 'Mobile number must be exactly 10 digits')
            return redirect('user:owner_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('user:owner_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('user:owner_register')

        if OwnerProfile.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, 'Mobile number already registered')
            return redirect('user:owner_register')
        
        BLOCKED_USERNAMES = ['admin', 'administrator', 'root', 'support']

        if username.lower() in BLOCKED_USERNAMES:
            messages.error(request, "This username is not allowed")
            return redirect('user:owner_register')
        # Username validation

        if not re.match(USERNAME_REGEX, username):
            messages.error(request, "Username must start with a letter and can contain letters, numbers, _ or . (4–20 characters)")
            return redirect('user:owner_register')

        if not validate_uploaded_file(identity_proof):
            messages.error(request, "Invalid identity document. Only PDF/JPG/PNG max 3MB.")
            return redirect('user:owner_register')

        if not validate_uploaded_file(ownership_proof):
            messages.error(request, "Invalid ownership document. Only PDF/JPG/PNG max 3MB.")
            return redirect('user:owner_register')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password1
        )

        OwnerProfile.objects.create(
            user=user,
            mobile_number=mobile_number,
            identity_proof=identity_proof,
            ownership_proof=ownership_proof,
            kyc_status="Pending"
        )

        messages.success(request, 'Owner account created. Awaiting verification.')
        return redirect('user:user_login')
    
    return render(request, 'users/owner_register.html')

#@login_required
def user_register(request):
    if request.method=='POST':
        role = "Tenant"
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        username=request.POST['username']
        password1=request.POST['password1']
        password2=request.POST['password2']     
        mobile_number = request.POST['mobile_number']
        
        # Username validation
        if not re.match(USERNAME_REGEX, username):
            messages.error(request, "Username must start with a letter and can contain letters, numbers, _ or . (4–20 characters)")
            return redirect('user:user_register')
        
        BLOCKED_USERNAMES = ['admin', 'administrator', 'root', 'support']

        if username.lower() in BLOCKED_USERNAMES:
            messages.error(request, "This username is not allowed")
            return redirect('user:user_register')


        # Check if passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('users:user_register')
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('user:user_register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return redirect('user:user_register')
        
        if TenantProfile.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, 'Mobile number is already registered')
            return redirect('user:user_register')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password1
        )
        TenantProfile.objects.create(
            user=user,
            mobile_number=mobile_number
        )

        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('user:user_login')
    return render(request, 'users/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password')
            return redirect('user:user_login')

        # ---------- OWNER LOGIN CHECK ----------
        if hasattr(user, 'ownerprofile'):

            owner = user.ownerprofile

            if owner.kyc_status == "Pending":
                messages.error(request, "Your KYC is still under review.")
                return redirect('user:user_login')

            if owner.kyc_status == "Rejected":
                messages.error(request, "Your KYC was rejected. Please contact admin.")
                return redirect('user:user_login')

            # allow login only if Approved
            auth.login(request, user)
            return redirect('owner:owner_dashboard')

        elif hasattr(user, 'tenantprofile'):
            auth.login(request, user)
            return redirect('/')

        else:
            messages.error(request, 'No role assigned')
            return redirect('user:user_login')

    return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('/')

def user_otp(request):
    return render(request, 'users/user_account_details.html')

#forgot Password
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(f"/user/reset/{uidb64}/{token}/")  


                # Send email
                subject = "Password Reset Request"
                message = render_to_string("users/forget_password/password_reset_email.html", {
                    "reset_url": reset_url,
                    "user": user
                })
                send_mail(
                    subject,
                    "",  # Plain text version (leave empty if not needed)
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=message  
                )


                messages.success(request, "Password reset email sent! Check your inbox.")
                return redirect("user:password_reset_done")
            else:
                messages.error(request, "No account found with this email.")
    else:
        form = PasswordResetRequestForm()
    
    return render(request, "users/forget_password/password_reset_request.html", {"form": form})

def password_reset_done(request):
    return render(request, "users/forget_password/password_reset_done.html")


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                messages.success(request, "Password reset successful! You can now log in.")
                return redirect("user:password_reset_complete")
        else:
            form = SetNewPasswordForm()
        return render(request, "users/forget_password/password_reset_confirm.html", {"form": form})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("user:password_reset")

def password_reset_complete(request):
    return render(request, "users/forget_password/password_reset_complete.html")


# import json
# from django.http import JsonResponse
# from firebase_admin import auth

# def send_otp(request):
#     """Send OTP using Firebase"""
#     try:
#         data = json.loads(request.body)
#         phone_number = data.get("phone_number")

#         # Firebase sends OTP automatically
#         return JsonResponse({"message": "OTP sent successfully!", "phone_number": phone_number})

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=400)

# def verify_otp(request):
#     """Verify OTP using Firebase"""
#     try:
#         data = json.loads(request.body)
#         id_token = data.get("id_token")  # OTP verification token from frontend

#         # Verify OTP
#         decoded_token = auth.verify_id_token(id_token)
#         uid = decoded_token["uid"]

#         return JsonResponse({"message": "OTP verified!", "uid": uid})

#     except Exception as e:
#         return JsonResponse({"error": "Invalid OTP"}, status=400)

@login_required
def user_account(request):
    user = request.user

    tenant = getattr(user, 'tenantprofile', None)
    owner = getattr(user, 'ownerprofile', None)

    my_bookings = Booking.objects.none()

    # ONLY tenants should see bookings
    if tenant:
        my_bookings = Booking.objects.filter(user=user).order_by('-booking_date')

    return render(request, "users/user_account_details.html", {
        "user": user,
        "tenant": tenant,
        "owner": owner,
        "my_bookings": my_bookings,
    })


@login_required
def edit_profile(request):

    user = request.user

    tenant = None
    owner = None

    try:
        tenant = user.tenantprofile
    except:
        pass

    try:
        owner = user.ownerprofile
    except:
        pass

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        if tenant:
            tenant.mobile_number = request.POST.get('mobile_number')
            tenant.save()

        if owner:
            owner.mobile_number = request.POST.get('mobile_number')
            owner.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('user:edit_profile')

    return render(request, 'users/edit_profile.html', {
        'user': user,
        'tenant': tenant,
        'owner': owner
    })
