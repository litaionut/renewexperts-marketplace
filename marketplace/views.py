from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm, ContactForm
from .models import Profile
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
            # Creează utilizatorul dar îl setează inactiv
            user = form.save(commit=False)
            user.is_active = False  # Utilizatorul nu poate loga până verifică email-ul
            user.save()
            
            # Generează codul de verificare
            code = user.profile.generate_verification_code()
            
            # Trimite email de verificare prin Resend
            try:
                if not settings.RESEND_API_KEY:
                    messages.error(request, "Email service is not configured. Please contact administrator.")
                    user.delete()  # Șterge utilizatorul dacă nu putem trimite email
                    return render(request, 'marketplace/register.html', {'form': form})
                
                resend.api_key = settings.RESEND_API_KEY
                
                email_subject = "Verify your RenewExperts account"
                email_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #27ae60;">Welcome to RenewExperts!</h2>
                            <p>Hi {user.username},</p>
                            <p>Thank you for registering. Please verify your email address by entering this code:</p>
                            <div style="text-align: center; margin: 30px 0;">
                                <h1 style="color: #27ae60; font-size: 36px; letter-spacing: 8px; margin: 20px 0; font-weight: bold;">{code}</h1>
                            </div>
                            <p>This code will expire in 24 hours.</p>
                            <p>If you didn't create this account, please ignore this email.</p>
                            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                            <p style="color: #999; font-size: 12px;">This is an automated message, please do not reply.</p>
                        </div>
                    </body>
                </html>
                """
                
                resend.Emails.send({
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [user.email],
                    "subject": email_subject,
                    "html": email_html,
                })
                
                # Salvează user_id în sesiune pentru pagina de verificare
                request.session['verification_user_id'] = user.id
                
                messages.success(request, "Registration successful! Please check your email for verification code.")
                return redirect('verify_email')
                
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                messages.error(request, "Account creation failed. Please try again or contact support.")
                user.delete()  # Șterge utilizatorul dacă nu putem trimite email
                if settings.DEBUG:
                    messages.error(request, f"Error: {str(e)}")
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
                # Verifică dacă utilizatorul a verificat email-ul
                if not user.is_active:
                    messages.warning(request, "Please verify your email address before logging in. Check your inbox for the verification code.")
                    request.session['verification_user_id'] = user.id
                    return redirect('verify_email')
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

def verify_email_view(request):
    """View pentru verificarea codului de email"""
    user_id = request.session.get('verification_user_id')
    
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')
    
    # Dacă utilizatorul este deja verificat, redirecționează
    if user.is_active and user.profile.is_email_verified:
        messages.info(request, "Email already verified!")
        return redirect('login')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if user.profile.verification_code == code:
            # Codul este corect - activează utilizatorul
            user.is_active = True
            user.profile.is_email_verified = True
            user.profile.verification_code = ''  # Șterge codul
            user.profile.save()
            user.save()
            
            # Șterge user_id din sesiune
            del request.session['verification_user_id']
            
            # Loghează utilizatorul automat
            login(request, user)
            
            messages.success(request, "Email verified successfully! Welcome to RenewExperts!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
    
    return render(request, 'marketplace/verify_email.html', {'user': user})

def resend_verification_view(request):
    """View pentru retrimiterea codului de verificare"""
    user_id = request.session.get('verification_user_id')
    
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id, is_active=False)
        
        # Generează un cod nou
        code = user.profile.generate_verification_code()
        
        # Trimite email nou
        try:
            if not settings.RESEND_API_KEY:
                messages.error(request, "Email service is not configured.")
                return redirect('verify_email')
            
            resend.api_key = settings.RESEND_API_KEY
            
            email_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #27ae60;">Your RenewExperts Verification Code</h2>
                        <p>Hi {user.username},</p>
                        <p>Your new verification code is:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <h1 style="color: #27ae60; font-size: 36px; letter-spacing: 8px; margin: 20px 0; font-weight: bold;">{code}</h1>
                        </div>
                        <p>This code will expire in 24 hours.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #999; font-size: 12px;">This is an automated message, please do not reply.</p>
                    </div>
                </body>
            </html>
            """
            
            resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": [user.email],
                "subject": "Your RenewExperts Verification Code",
                "html": email_html,
            })
            
            messages.success(request, "Verification code resent! Please check your email.")
            return redirect('verify_email')
            
        except Exception as e:
            logger.error(f"Failed to resend verification email: {str(e)}")
            messages.error(request, "Failed to resend code. Please try again later.")
            if settings.DEBUG:
                messages.error(request, f"Error: {str(e)}")
            return redirect('verify_email')
            
    except User.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect('register')

def password_reset_request_view(request):
    """View pentru solicitarea resetării parolei"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, 'marketplace/password_reset_request.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Generează token pentru resetare parolă
            token = default_token_generator.make_token(user)
            
            # Construiește URL-ul pentru resetare
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Trimite email cu link-ul de resetare
            try:
                if not settings.RESEND_API_KEY:
                    messages.error(request, "Email service is not configured. Please contact administrator.")
                    return render(request, 'marketplace/password_reset_request.html')
                
                resend.api_key = settings.RESEND_API_KEY
                
                email_subject = "Reset your RenewExperts password"
                email_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #27ae60;">Password Reset Request</h2>
                            <p>Hi {user.username},</p>
                            <p>You requested to reset your password. Click the button below to reset it:</p>
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{reset_url}" style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Reset Password</a>
                            </div>
                            <p>Or copy and paste this link into your browser:</p>
                            <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_url}</p>
                            <p style="color: #999; font-size: 12px; margin-top: 30px;">This link will expire in 1 hour.</p>
                            <p style="color: #999; font-size: 12px;">If you didn't request a password reset, please ignore this email.</p>
                            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                            <p style="color: #999; font-size: 12px;">This is an automated message, please do not reply.</p>
                        </div>
                    </body>
                </html>
                """
                
                resend.Emails.send({
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [user.email],
                    "subject": email_subject,
                    "html": email_html,
                })
                
                messages.success(request, "Password reset link has been sent to your email. Please check your inbox.")
                return redirect('password_reset')
                
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")
                messages.error(request, "Failed to send password reset email. Please try again later.")
                if settings.DEBUG:
                    messages.error(request, f"Error: {str(e)}")
                    
        except User.DoesNotExist:
            # Nu dezvăluim că emailul nu există (securitate)
            messages.success(request, "If an account exists with that email, a password reset link has been sent.")
            return redirect('password_reset')
    
    return render(request, 'marketplace/password_reset_request.html')

def password_reset_confirm_view(request, uidb64, token):
    """View pentru confirmarea și resetarea parolei"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is None:
        messages.error(request, "Invalid password reset link.")
        return redirect('password_reset')
    
    # Verifică token-ul
    if not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired password reset link. Please request a new one.")
        return redirect('password_reset')
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been reset successfully. Please log in with your new password.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SetPasswordForm(user)
    
    return render(request, 'marketplace/password_reset_confirm.html', {'form': form})
