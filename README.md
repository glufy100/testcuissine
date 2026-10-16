# Oups, la cuisine !

Blog de ratés culinaires en Python / Django 5.2, avec SQLite et un espace de rédaction personnalisé en français.

## Lancer en local

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

- Blog : http://127.0.0.1:8000/
- Atelier : http://127.0.0.1:8000/admin/
- Gestion avancée des comptes : http://127.0.0.1:8000/gestion-django/

L’atelier est réservé aux comptes administrateurs actifs (`is_staff` et `is_superuser`). Il permet de créer, modifier et supprimer des articles, charger une photo (8 Mo maximum), enregistrer un brouillon et publier. Les brouillons sont cachés aux visiteurs, y compris sur leur URL directe. Le contenu est du texte brut, avec paragraphes automatiques et HTML échappé.

## Démonstration

`python manage.py demo` ajoute six exemples et crée le compte local `louis` s’il n’existe pas. Son mot de passe aléatoire est affiché une seule fois. Les textes sont fictifs et les photos Unsplash sont illustratives. Supprime ou remplace ces articles dans l’atelier avant une vraie publication. La commande est réexécutable sans duplication et ne change pas les mots de passe existants.

Pour changer un mot de passe : `python manage.py changepassword louis`.

## Vérification

```sh
python manage.py check
python manage.py test
```

## Mise en production

Le site est publié sur https://louis10.eu.pythonanywhere.com/ avec PythonAnywhere Europe (compte gratuit `louis10`). L’espace de rédaction est https://louis10.eu.pythonanywhere.com/admin/. Sites ne fournit pas l’hébergement Python/Django nécessaire. Choisir un hébergeur Python avec stockage persistant, puis définir `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` et `DJANGO_ALLOWED_HOSTS`. Utiliser un serveur WSGI (par exemple Gunicorn), HTTPS et un serveur pour les fichiers statiques (`collectstatic`) et médias. Sauvegarder SQLite et les photos, ou configurer PostgreSQL pour un usage plus important. Exécuter `python manage.py check --deploy`. Le serveur `runserver` sert uniquement au développement.

Les polices Google Fonts et les photos de démonstration demandent une connexion Internet ; les polices système et les articles restent disponibles sans elles. La base, les photos chargées et la clé locale sont ignorées par Git. La connexion est protégée par django-axes : blocage de 15 minutes après 5 échecs. Les mots de passe choisis via l’interface doivent comporter au moins 14 caractères.

## Publication préparée

Le guide détaillé est dans `deployment/README.md`. Le script `deployment/package.py` prépare une archive privée avec les articles, photos et comptes, sans clés secrètes ni sessions. La configuration de production active HTTPS, des cookies sécurisés et HSTS. Depuis l’atelier, « Changer mon mot de passe » permet de choisir un mot de passe personnel. Les contrôles de déploiement et onze tests automatisés vérifient les protections. Publication effectuée le 16 octobre 2026. HTTPS obligatoire, connexion admin et affichage des six photos vérifiés en ligne. Dans PythonAnywhere → Web, renouveler l’activation gratuite avant le 16 novembre 2026, puis chaque mois. La base et les photos en production évoluent indépendamment de la copie locale ; ne pas les écraser avec une ancienne archive.
