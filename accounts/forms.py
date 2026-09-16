from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar_url', 'theme_preference', 'preferred_language', 'bio']
        widgets = {
            'avatar_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://avatars.githubusercontent.com/u/...'}),
            'theme_preference': forms.Select(attrs={'class': 'form-select'}),
            'preferred_language': forms.Select(choices=[
                ('en', 'English'),
                ('es', 'Spanish'),
                ('fr', 'French'),
                ('de', 'German'),
                ('ja', 'Japanese'),
            ], attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself'}),
        }
