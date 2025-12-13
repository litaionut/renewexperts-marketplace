from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserRegistrationForm, ContactForm
from django.contrib import messages
from threading import Thread
import logging
import resend

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
    """Funcție helper pentru trimiterea email-urilor în background folosind Resend"""
    try:
        # Verifică dacă API key-ul Resend este configurat
        if not settings.RESEND_API_KEY:
            logger.error("Resend API key not configured! Set RESEND_API_KEY environment variable.")
            return False
        
        # Configurează Resend API
        resend.api_key = settings.RESEND_API_KEY
        
        # Trimite email-ul prin Resend
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "text": message,
        }
        
        email = resend.Emails.send(params)
        logger.info(f"Email sent successfully to {recipient_email}. Resend ID: {email.get('id', 'N/A')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {str(e)}")
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
            if not settings.RESEND_API_KEY:
                messages.warning(request, "Email service is not configured. Please contact the administrator.")
                logger.warning("Email not sent: RESEND_API_KEY not set")
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
