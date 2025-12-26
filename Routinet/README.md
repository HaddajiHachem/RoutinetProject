# Routinet – Plateforme E‑Learning

Ce projet est une plateforme E‑Learning permettant aux **étudiants**, **enseignants** et **administrateurs** de gérer des cours, devoirs, soumissions et messagerie interne.

Ce document décrit uniquement la partie **backend** (Django) afin de faciliter l’installation et l’évaluation.

---

## 1. Prérequis Backend

- **Système** : Windows 10/11 (testé) – fonctionne aussi sous Linux/macOS.
- **Python** : version **3.12** recommandée.
- **pip** : gestionnaire de paquets Python.
- **Git** : optionnel, pour cloner le dépôt.
- **Base de données** : SQLite (fichier `db.sqlite3` créé automatiquement).

Aucune installation Node.js n’est nécessaire pour le backend.

---

## 2. Récupération du projet

Cloner le dépôt (ou télécharger le zip) puis se placer dans le dossier Django (celui qui contient `manage.py`). Par exemple :

```powershell
cd "C:\Users\Lenovo\RoutinetProject\RoutinetProject\Routinet"
```

Toutes les commandes suivantes supposent que vous êtes dans ce dossier.

---

## 3. Environnement virtuel Python

Le projet utilise un environnement virtuel nommé **`.venv312`**.

### 3.1. Création de l’environnement (si nécessaire)

```powershell
python -m venv .venv312
```

### 3.2. Activation de l’environnement (Windows / PowerShell)

```powershell
.\.venv312\Scripts\Activate.ps1
```

Après activation, le prompt doit commencer par `(.venv312)`.

### 3.3. Installation des dépendances

Si un fichier `requirements.txt` est fourni :

```powershell
pip install -r requirements.txt
```

Sinon, les paquets principaux sont au minimum :

- `Django` (version 5.x)

---

## 4. Initialisation de la base de données

Exécuter les migrations pour créer les tables :

```powershell
python manage.py migrate
```

### 4.1. Création d’un superutilisateur (administrateur)

```powershell
python manage.py createsuperuser
```

Puis suivre les instructions (nom d’utilisateur, e‑mail, mot de passe).

---

## 5. Lancer le serveur backend

Toujours depuis le dossier du projet, avec l’environnement activé :

```powershell
python manage.py runserver
```

Le backend Django sera alors disponible à l’adresse :

```text
http://127.0.0.1:8000/
```

### 5.1. Changer de port (optionnel)

Vous pouvez lancer le serveur sur un autre port, par exemple 8080 :

```powershell
python manage.py runserver 8080
```

L’URL devient alors : `http://127.0.0.1:8080/`.

---

## 6. Résumé des informations demandées (livrable backend)

- **Prérequis** :
  - Python 3.12
  - pip
  - (Optionnel) Git
  - Base de données SQLite intégrée
- **Commandes principales** :
  - Activation de l’environnement :
    - `python -m venv .venv312` (une seule fois)
    - `.\.venv312\\Scripts\\Activate.ps1`
  - Migrations :
    - `python manage.py migrate`
  - Création admin :
    - `python manage.py createsuperuser`
  - Lancement du serveur :
    - `python manage.py runserver`
- **Port utilisé** :
  - Port par défaut **8000** (`http://127.0.0.1:8000/`)

Ces informations suffisent pour qu’un évaluateur puisse :

1. Installer l’environnement backend.
2. Initialiser la base de données.
3. Lancer le serveur et tester l’application.

---

## 7. Aperçu rapide des fonctionnalités backend

- Gestion des **comptes** (étudiants, enseignants, administrateurs) via l’app `comptes`.
- Gestion des **cours** (`Cours`) : création, modification, suppression, image de couverture, fichiers associés.
- Gestion des **modules** et **ressources** au sein des cours.
- Gestion des **devoirs** (`Devoir`) :
  - Création depuis la page d’un cours.
  - Création globale depuis "Mes devoirs" avec sélection du cours.
  - Soumission de devoirs par les étudiants (`Soumission`).
- Gestion de la **messagerie interne** (`Message`) :
  - Envoi de messages entre utilisateurs connectés.
  - Affichage des messages reçus / envoyés.
- **Notifications** internes (`Notification`) pour certaines actions (inscriptions, etc.).

Pour plus de détails fonctionnels, voir les templates dans `e_learning/templates/e_learning/` et les vues dans `e_learning/views.py`.
