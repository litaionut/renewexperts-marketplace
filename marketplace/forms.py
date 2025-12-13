from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    subject = forms.CharField(
        max_length=200, 
        label="Subject",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What is this about?'})
    )
    message = forms.CharField(
        label="Your Message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message here...'})
    )








