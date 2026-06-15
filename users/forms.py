from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, Profile
import re

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['phone', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            if not re.match(r'^9[678]\d{8}$', phone):
                raise ValidationError('⚠ Enter a valid Nepali phone number (e.g. 98XXXXXXXX).')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and self.user:
            existing = CustomUser.objects.filter(email=email).exclude(pk=self.user.pk)
            if existing.exists():
                raise ValidationError('⚠ This email is already in use by another account.')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile