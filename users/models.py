from django.db import models
from django.contrib.auth.models import User


class TenantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} (Tenant)"


class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=10, unique=True, null=True, blank=True)

    identity_proof = models.FileField(upload_to='media/kyc/', null=True, blank=True)
    ownership_proof = models.FileField(upload_to='media/kyc/', null=True, blank=True)

    kyc_status = models.CharField(
        max_length=10,
        choices=(
            ('Pending','Pending'),
            ('Approved','Approved'),
            ('Rejected','Rejected')
        ),
        default='Pending'
    )
    kyc_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} (Owner)"
