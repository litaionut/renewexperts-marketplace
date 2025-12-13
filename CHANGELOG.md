# Changelog

Toate modificările notabile ale acestui proiect vor fi documentate în acest fișier.

## [1.2.0] - 2025-12-13

### Added
- **Verificare Email la Înregistrare**: Sistem complet de verificare email pentru protecție împotriva robotilor
  - Generare automată cod de verificare de 6 cifre
  - Model `Profile` cu `verification_code` și `is_email_verified`
  - Trimitere email de verificare prin Resend la înregistrare
  - Pagină de verificare email la `/verify-email/`
  - Funcționalitate "Resend Code" pentru retrimitere cod
  - Blocare login pentru utilizatori neverificați
  - Activare automată cont și autentificare după verificare
  - Signal handlers Django pentru creare automată Profile la creare User

### Changed
- Utilizatorii noi sunt creați cu `is_active=False` până la verificarea emailului
- Login view verifică dacă utilizatorul a verificat email-ul înainte de autentificare
- Signal handler îmbunătățit pentru gestionare automată profile utilizatori existenți

### Security
- Previne înregistrarea conturilor cu email-uri false/nevalide
- Protecție împotriva robotilor și spam-ului
- Verificare obligatorie înainte de activare cont

### Technical Details
- Model nou: `marketplace.models.Profile` cu relație OneToOne cu User
- Migrare nouă: `0001_initial.py` pentru model Profile
- View-uri noi: `verify_email_view`, `resend_verification_view`
- Template nou: `verify_email.html` pentru introducerea codului
- Integrare cu Resend pentru trimitere coduri de verificare
- Session management pentru stocare temporară `verification_user_id`

### User Flow
1. Utilizatorul completează formularul de înregistrare
2. Contul este creat cu `is_active=False`
3. Cod de 6 cifre este generat și trimis pe email
4. Utilizatorul este redirecționat la pagina de verificare
5. Utilizatorul introduce codul primit pe email
6. La verificare corectă, contul este activat și utilizatorul este logat automat
7. Redirect către dashboard

---

## [1.1.0] - 2025-12-13

### Added
- **Contact Form cu integrare email Resend**: Formular de contact funcțional care trimite emailuri prin serviciul Resend
  - Pagină de contact la `/contact/`
  - Formular cu câmpuri: Nume, Email, Subiect, Mesaj
  - Integrare cu Resend API pentru trimiterea emailurilor
  - Trimitere asincronă de emailuri pentru performanță optimă
  - Link "Contact" în navbar

### Changed
- Migrat de la Gmail SMTP la Resend pentru fiabilitate și compatibilitate cu cloud providers
- Îmbunătățit error handling pentru email-uri

### Technical Details
- Adăugat `resend==2.19.0` în requirements.txt
- Configurare variabile de mediu: `RESEND_API_KEY` și `RESEND_FROM_EMAIL`
- Email-urile sunt trimise către: `litaionutm9@gmail.com`

### Configuration Required
Pentru a funcționa, adaugă următoarele variabile de mediu:
- `RESEND_API_KEY` - API key-ul de la Resend
- `RESEND_FROM_EMAIL` - Adresa de email expeditor (ex: `onboarding@resend.dev`)

---

## [1.0.0] - 2025-12-01

### Added
- Configurare inițială proiect Django
- Autentificare utilizatori (Register, Login, Logout)
- Dashboard personalizat pentru utilizatori
- Integrare Bootstrap 5 pentru UI modern
- Deployment pe Railway cu PostgreSQL
- Documentație completă de deployment (GHID_DEPLOY.md)
- Git workflow profesional (WORKFLOW.md)

### Technical Stack
- Django 5.2.8
- PostgreSQL (Railway)
- Gunicorn + WhiteNoise
- Bootstrap 5

