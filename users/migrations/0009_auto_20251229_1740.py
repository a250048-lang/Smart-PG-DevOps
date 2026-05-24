from django.db import migrations


def forward(apps, schema_editor):
    User = apps.get_model("auth", "User")
    OwnerProfile = apps.get_model("users", "OwnerProfile")
    TenantProfile = apps.get_model("users", "TenantProfile")

    # Try reading role from any surviving field / default Tenant
    for user in User.objects.all():

        role = "Tenant"  # default
        mobile = None

        # if tenant already exists skip
        if TenantProfile.objects.filter(user=user).exists():
            continue

        # if owner already exists skip
        if OwnerProfile.objects.filter(user=user).exists():
            continue

        # SIMPLE RULE:
        # if user uploaded KYC → owner, else tenant
        # (you can improve later if needed)

        if hasattr(user, "ownerprofile"):
            continue

        if hasattr(user, "tenantprofile"):
            continue

        # fallback create tenant
        TenantProfile.objects.create(
            user=user,
            mobile_number=mobile
        )


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_delete_userprofile"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
