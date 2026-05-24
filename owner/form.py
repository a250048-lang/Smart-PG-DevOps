from django import forms
from .models import PGProperty, Room,PGPropertyImage
from django.forms.widgets import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True



class PGPropertyForm(forms.ModelForm):
    class Meta:
        model = PGProperty
        exclude = ['owner', 'is_active', 'is_verified', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'area_road': forms.TextInput(attrs={'class': 'form-control'}),
            'village': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender_availability': forms.Select(attrs={'class': 'form-control'}),
            'rules': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter rules and regulations for the PG'}),
            'title_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'has_wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_food': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_laundry': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_power_backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PGPropertyImageForm(forms.ModelForm):
    image = forms.ImageField(
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = PGPropertyImage
        fields = ('image',)



class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['pg_property']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_beds': forms.NumberInput(attrs={'class': 'form-control'}),
        }

