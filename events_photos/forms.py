from allauth.account.forms import SignupForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Photo

class SchoolSignupForm(SignupForm):
    SCHOOL_EMAIL_DOMAIN = 'kld.edu.ph'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[-1]
        if domain != self.SCHOOL_EMAIL_DOMAIN:
            raise ValidationError(
                f"You must use an email address from {self.SCHOOL_EMAIL_DOMAIN} to sign up."
            )
        return email
    
class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description of the photo (Optional)'}),
        }
        
class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description of the photo (Optional)'}),
        }
