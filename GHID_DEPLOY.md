# Ghid de Configurare și Deployment: Django + GitHub + Railway + PostgreSQL

Acest ghid explică pașii completi pentru a crea un proiect Django, a-l urca pe GitHub, a-l conecta la Railway și a configura baza de date PostgreSQL.

---

## 1. Inițializare Proiect Local

### Creare și activare mediu virtual
```powershell
# În folderul proiectului
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Instalare Django și dependențe
```bash
pip install django gunicorn whitenoise psycopg2-binary dj-database-url
django-admin startproject renewexperts .
```

### Configurare pentru Deployment
1. Creați fișierul `Procfile` (fără extensie) în rădăcina proiectului:
   ```
   web: python manage.py migrate && gunicorn renewexperts.wsgi --log-file -
   ```
2. Creați fișierul `runtime.txt`:
   ```
   python-3.12.8
   ```
3. Generați `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

### Modificări în `settings.py`
- Setați `DEBUG = False` (sau folosiți variabile de mediu).
- Configurați `ALLOWED_HOSTS = ['*', '.railway.app']`.
- Adăugați `whitenoise` în `MIDDLEWARE` (după SecurityMiddleware).
- Configurați baza de date pentru a folosi `DATABASE_URL`:
  ```python
  import dj_database_url
  import os
  
  if 'DATABASE_URL' in os.environ:
      DATABASES = {
          'default': dj_database_url.config(conn_max_age=600)
      }
  ```

---

## 2. Git și GitHub

### Creare `.gitignore`
Asigurați-vă că aveți un fișier `.gitignore` care exclude `venv/`, `__pycache__/`, `db.sqlite3` etc.

### Inițializare și Push
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
# Înlocuiți cu URL-ul repository-ului dvs.
git remote add origin https://github.com/UTILIZATOR/NUME-REPO.git
git push -u origin main
```

---

## 3. Deployment pe Railway

### Conectare Proiect
1. Intrați pe [Railway Dashboard](https://railway.app/).
2. Creați un proiect nou ("New Project") -> "Deploy from GitHub repo".
3. Selectați repository-ul creat.

### Adăugare PostgreSQL
1. În dashboard-ul proiectului, apăsați "New" -> "Database" -> "PostgreSQL".
2. Așteptați inițializarea bazei de date.

### Conectare Django la PostgreSQL
1. Dați click pe serviciul **PostgreSQL** -> tab-ul **Connect**.
2. Copiați `Postgres Connection URL` (începe cu `postgresql://...`).
3. Dați click pe serviciul **Django** (aplicația dvs.) -> tab-ul **Variables**.
4. Adăugați o variabilă nouă:
   - **Nume:** `DATABASE_URL`
   - **Valoare:** (URL-ul copiat anterior).
5. Railway va redeploya automat aplicația.

---

## 4. Creare Superuser (Admin) pe Railway

Deoarece baza de date este pe server, nu putem folosi `createsuperuser` interactiv standard. Avem două opțiuni:

### Opțiunea A: Folosind Railway CLI (Recomandat)
Dacă aveți CLI instalat și sunteți autentificat (`railway login`):

1. Linkați proiectul local:
   ```bash
   railway link
   # Selectați proiectul corect
   ```

2. Rulați scriptul de creare (non-interactiv):
   ```bash
   railway run python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@email.com', 'parola123') if not User.objects.filter(username='admin').exists() else print('User exists')"
   ```

### Opțiunea B: Din interfața Railway (Dacă CLI nu e disponibil)
Aceasta este mai complicată deoarece consola Railway nu suportă input interactiv ușor pentru comandă. Recomandăm Opțiunea A.

---

## Verificare
Accesați `https://Nume-Proiect.up.railway.app/admin/` și logați-vă cu credențialele create.

---

## 5. Configurare Formular de Contact cu Email (Resend)

### Instalare Resend
```bash
pip install resend
pip freeze > requirements.txt  # Actualizează requirements.txt
```

### Configurare în `settings.py`
```python
# Email Configuration - Resend
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
DEFAULT_FROM_EMAIL = RESEND_FROM_EMAIL

if not RESEND_API_KEY:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Creare Formular (în `forms.py`)
```python
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)
```

### View pentru Formular (în `views.py`)
```python
import resend

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Procesează formularul și trimite email prin Resend
            resend.api_key = settings.RESEND_API_KEY
            resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": ["your-email@example.com"],
                "subject": f"Contact: {form.cleaned_data['subject']}",
                "text": form.cleaned_data['message']
            })
    # ... rest of view
```

### Variabile de Mediu pe Railway
1. Creați cont pe [Resend.com](https://resend.com)
2. Obțineți API key din dashboard
3. În Railway Dashboard -> Variables, adăugați:
   - `RESEND_API_KEY` = (API key-ul de la Resend)
   - `RESEND_FROM_EMAIL` = `onboarding@resend.dev` (sau domeniu verificat)

### Pentru Dezvoltare Locală
Creați fișierul `.env` în rădăcina proiectului:
```
RESEND_API_KEY=your_api_key_here
RESEND_FROM_EMAIL=onboarding@resend.dev
```

**Notă:** Fișierul `.env` este deja în `.gitignore`, deci nu va fi commitat.

