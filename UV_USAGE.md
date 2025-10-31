# uv Installation and Usage

## Installation de uv

```powershell
# Installer uv
pip install uv

# Ou avec winget (Windows)
winget install astral-sh.uv

# Ou avec scoop
scoop install uv
```

## Installation des dépendances

```powershell
# Synchroniser les dépendances depuis pyproject.toml
# PyTorch avec CUDA 13.0 est installé automatiquement
uv sync

# Note : Si l'installation automatique de PyTorch CUDA échoue, installer manuellement :
# uv pip install torch --index-url https://download.pytorch.org/whl/cu130
```

## Utilisation quotidienne

```powershell
# Exécuter l'application (uv gère automatiquement l'environnement)
uv run speech_to_text.py --guipyside6
uv run speech_to_text.py audio.mp3
uv run speech_to_text.py --diagnose

# Exécuter avec Python directement
uv run python speech_to_text.py --gui

# Mettre à jour les dépendances
uv sync --upgrade
```

## Environnement virtuel (optionnel)

Si vous préférez activer manuellement l'environnement :

```powershell
# L'environnement est créé automatiquement par uv sync dans .venv/
.venv\Scripts\activate

# Puis utiliser Python normalement
python speech_to_text.py --guipyside6

# Désactiver
deactivate
```

## Commandes utiles

```powershell
# Lister les dépendances installées
uv pip list

# Afficher les informations d'un package
uv pip show package-name

# Vérifier les dépendances
uv tree

# Nettoyer le cache
uv cache clean

# Mettre à jour uv lui-même
uv self update
```

## Générer requirements.txt (si nécessaire)

Si vous avez besoin d'un fichier requirements.txt pour la compatibilité :

```powershell
# Depuis l'environnement actuel
uv pip freeze > requirements.txt

# Depuis uv.lock (plus précis et recommandé)
uv export --format requirements-txt > requirements.txt
```

### Workflow complet

```powershell
# 1. Cloner le projet
git clone <repo>
cd speech-to-text

# 2. Installer les dépendances (inclut PyTorch CUDA automatiquement)
uv sync

# 3. Lancer l'application
uv run speech_to_text.py --guipyside6
```
