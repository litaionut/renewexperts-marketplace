from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, ContactForm
from django.contrib import messages

def home(request):
    return render(request, 'marketplace/home.html')

@login_required
def dashboard(request):
    return render(request, 'marketplace/dashboard.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'marketplace/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extrage datele din formular
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Creează conținutul emailului
            email_subject = f"Contact Form: {subject}"
            email_message = f"""
New message from {name} ({email})

Subject: {subject}

Message:
{message}

---
This email was sent from the RenewExperts Marketplace contact form.
            """
            
            # Adresa unde vei primi emailurile (poți schimba asta)
            recipient_email = 'litaionutm9@gmail.com'
            
            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    fail_silently=False,
                )
                messages.success(request, "Thank you! Your message has been sent successfully.")
                return redirect('contact')
            except Exception as e:
                messages.error(request, f"Sorry, there was an error sending your message. Please try again later.")
                # În dezvoltare, poți afișa eroarea pentru debugging
                if settings.DEBUG:
                    messages.error(request, f"Error: {str(e)}")
    else:
        form = ContactForm()
    
    return render(request, 'marketplace/contact.html', {'form': form})
