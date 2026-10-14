# JoYed'S ClearBG

Application de bureau pour supprimer l'arrière-plan d'images par glisser-déposer, basée sur [rembg](https://github.com/danielgatis/rembg).

## Fonctionnalités
- Glisser-déposer d'images (PNG, JPG, WebP, BMP), traitement par lot
- Redimensionnement optionnel (proportions conservées)
- Traitement en arrière-plan avec barre de progression
- Historique des conversions, thème clair/sombre

## Installation
```bash
pip install -r requirements.txt
python main.py
```

Les images traitées sont enregistrées en `<nom>_clear.png` dans le dossier de sortie choisi (par défaut `~/Pictures`).
L'historique est stocké dans `~/Library/Application Support/JoYedsClearBG/logs.json` (macOS).

## Créer l'app macOS
```bash
pip install py2app
python setup.py py2app
```

© 2025 JoYed'S. Tous droits réservés.
