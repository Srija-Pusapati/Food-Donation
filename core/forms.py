from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Donation, Feedback

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[
        ('donor', 'Donor'),
        ('ngo', 'NGO / Volunteer'),
        ('needy', 'Needy Person')
    ], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # NGOs require admin approval
        user.is_approved = True if user.role != 'ngo' else False
        if commit:
            user.save()
        return user


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['food_name', 'quantity', 'location', 'expiry_time', 'food_image']
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5 Boxes of Pizza'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 20 servings'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pickup Address'}),
            'expiry_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'food_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
