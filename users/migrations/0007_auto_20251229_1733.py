from django.db import migrations


def move_profiles(apps, schema_editor):
    UserProfile = apps.get_model("users", "UserProfile")
    TenantProfile = apps.get_model("users", "TenantProfile")
    OwnerProfile = apps.get_model("users", "OwnerProfile")

    for p in UserProfile.objects.all():
        if p.role == "Tenant":
            TenantProfile.objects.get_or_create(
                user=p.user,
                defaults={"mobile_number": p.mobile_number},
            )
        else:
            OwnerProfile.objects.get_or_create(
                user=p.user,
                defaults={
                    "mobile_number": p.mobile_number,
                    "identity_proof": p.identity_proof,
                    "ownership_proof": p.ownership_proof,
                    "kyc_status": p.kyc_status,
                    "kyc_notes": p.kyc_notes,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_ownerprofile_tenantprofile_delete_userprofile"),
    ]

    operations = [
        migrations.RunPython(move_profiles, migrations.RunPython.noop),
    ]
