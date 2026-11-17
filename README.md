# FinTrack
# FinTrack API — Gestion de Budget Personnel & Détection d'Anomalies

API REST moderne et sécurisée conçue avec **FastAPI**, **SQLAlchemy** et **JWT**, permettant de gérer ses finances personnelles, convertir des devises en temps réel et détecter automatiquement les pics de dépenses inhabituels.

## Fonctionnalités Clés
* **Authentification & Sécurité :** Inscription et connexion via badges **JWT (OAuth2)** et hachage des mots de passe avec **Argon2**. Isolation stricte des données par utilisateur.
* **Gestion Financière (CRUD) :** Création, consultation, modification et suppression de revenus et dépenses.
* **Détection Intelligente d'Anomalies :** Analyse statistique en temps réel alertant l'utilisateur lorsqu'une dépense dépasse 2x sa moyenne habituelle dans une catégorie.
* **Conversion Multi-Devises Asynchrone :** Conversion automatique des dépenses étrangères (USD, GBP, CAD...) vers l'Euro via une API externe (`httpx` + `async/await`).
* **Tableaux de Bord & Bilans :** Calcul automatique du solde net et répartition des dépenses par catégorie.
* **Qualité & Tests :** Suite de tests automatisés avec **Pytest** et base de données de test isolée.

## Stack Technique
* **Langage :** Python 3.11+ (Typage statique)
* **Framework Web :** FastAPI
* **Base de données & ORM :** SQLite / SQLAlchemy 2.0
* **Validation :** Pydantic v2
* **Sécurité :** PyJWT & Pwdlib (Argon2)
* **Client HTTP Asynchrone :** HTTPX
* **Tests :** Pytest

## Installation et Lancement

1. **Cloner le dépôt et activer l'environnement virtuel :**
   ```bash
   python -m venv .venv
   # Windows :
   .venv\Scripts\activate
   # Mac / Linux :
   source .venv/bin/activate
   ```
2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer le serveur de développement :**
   ```bash
   fastapi dev app/main.py
   ```
4. **Accéder à la documentation interactive :** Ouvrez `http://127.0.0` dans votre navigateur.

## Lancer les Tests Automatisés
```bash
python -m pytest -v
```

