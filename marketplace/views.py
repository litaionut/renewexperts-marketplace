from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, ContactForm
from django.contrib import messages
from threading import Thread
import logging

logger = logging.getLogger(__name__)

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

def send_email_async(subject, message, recipient_email):
    """Funcție helper pentru trimiterea email-urilor în background"""
    try:
        # Verifică dacă credențialele sunt configurate
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.error("Email credentials not configured! Set EMAIL_USER and EMAIL_PASSWORD environment variables.")
            return False
        
        # Verifică dacă backend-ul este configurat corect
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
            logger.error(f"Email backend is not SMTP: {settings.EMAIL_BACKEND}")
            return False
            
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        # Log detalii despre configurație pentru debugging
        logger.error(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER is not None}")
        logger.error(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        logger.error(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
        return False

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
            email_message = f"""New message from {name} ({email})

Subject: {subject}

Message:
{message}

---
This email was sent from the RenewExperts Marketplace contact form."""
            
            # Adresa unde vei primi emailurile
            recipient_email = 'litaionutm9@gmail.com'
            
            # Verifică dacă emailul este configurat înainte de a trimite
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                messages.warning(request, "Email service is not configured. Please contact the administrator.")
                logger.warning("Email not sent: EMAIL_USER or EMAIL_PASSWORD not set")
                return render(request, 'marketplace/contact.html', {'form': form})
            
            # Trimite email-ul în background pentru a nu bloca request-ul
            try:
                email_thread = Thread(target=send_email_async, args=(email_subject, email_message, recipient_email))
                email_thread.daemon = True
                email_thread.start()
                
                messages.success(request, "Thank you! Your message has been sent successfully.")
                return redirect('contact')
            except Exception as e:
                logger.error(f"Error creating email thread: {str(e)}")
                messages.error(request, "Sorry, there was an error sending your message. Please try again later.")
                if settings.DEBUG:
                    messages.error(request, f"Error: {str(e)}")
    else:
        form = ContactForm()
    
    return render(request, 'marketplace/contact.html', {'form': form})
