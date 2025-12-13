# Changelog

Toate modificările notabile ale acestui proiect vor fi documentate în acest fișier.

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

