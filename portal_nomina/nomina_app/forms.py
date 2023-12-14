from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    organization = forms.CharField(max_length=100)
    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get('organization')
        # Perform additional validation or logic here
        return cleaned_data