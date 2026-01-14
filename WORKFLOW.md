# Git Workflow - RenewExperts Marketplace

Acest document descrie workflow-ul profesional de lucru cu Git pentru acest proiect.

## Structura Branch-urilor

- **`main`** - Codul de producție (mereu stabil și funcțional)
- **`develop`** - Branch principal de dezvoltare
- **`feature/nume-feature`** - Branch-uri pentru funcționalități noi
- **`hotfix/nume-fix`** - Branch-uri pentru fix-uri urgente în producție

## Versiuni (Tags)

- **`v1.0.0`** - Versiune stabilă inițială (autentificare, dashboard, Bootstrap)

## Cum să lucrezi pe o funcționalitate nouă

### 1. Asigură-te că ești pe develop și ai ultimele modificări
```bash
git checkout develop
git pull origin develop
```

### 2. Creează un branch nou pentru funcționalitatea ta
```bash
git checkout -b feature/google-auth
# sau
git checkout -b feature/email-verification
```

### 3. Lucrează pe branch-ul tău
```bash
# Fă modificările necesare
# Apoi commit frecvent cu mesaje descriptive
git add .
git commit -m "Add Google OAuth login button"
git commit -m "Configure Google OAuth settings"
```

### 4. Push branch-ul pe GitHub
```bash
git push origin feature/google-auth
```

### 5. Când funcționalitatea e gata și testată, merge în develop
```bash
git checkout develop
git merge feature/google-auth
git push origin develop

# Șterge branch-ul local dacă nu mai ai nevoie
git branch -d feature/google-auth
```

### 6. Când develop e stabil, merge în main pentru release
```bash
git checkout main
git merge develop
git tag -a v1.1.0 -m "Release v1.1.0 - Add Google authentication"
git push origin main
git push origin v1.1.0
```

## Revenirea la o versiune anterioară

### Pentru a vedea toate versiunile (tags)
```bash
git tag -l
```

### Pentru a reveni la o versiune specifică
```bash
# Doar pentru a vizualiza (read-only)
git checkout v1.0.0

# Pentru a crea un branch nou de la o versiune
git checkout -b hotfix/critical-bug v1.0.0
```

### Pentru a vedea diferențele între versiuni
```bash
git diff v1.0.0..v1.1.0
```

## Best Practices

1. **Nu lucra direct pe `main`** - folosește întotdeauna branch-uri
2. **Commit-uri mici și frecvente** - cu mesaje clare și descriptive
3. **Testează înainte de merge** - asigură-te că totul funcționează
4. **Folosește Pull Requests** pe GitHub pentru code review (opțional, dar recomandat)
5. **Tag versiunile importante** - pentru release-uri majore

## Unde ești acum?

- Ești pe branch-ul **`develop`** (branch principal de dezvoltare)
- Versiunea curentă marcată: **`v1.0.0`** (pe branch-ul `main`)

## Comenzi rapide

```bash
# Vezi pe ce branch ești
git branch

# Vezi toate branch-urile
git branch -a

# Vezi toate tag-urile
git tag -l

# Vezi statusul modificărilor
git status

# Vezi istoricul commit-urilor
git log --oneline --graph --all
```








