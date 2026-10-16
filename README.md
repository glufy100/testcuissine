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

L’atelier est réservé aux comptes avec le statut « équipe » (`is_staff`). Il permet de créer, modifier et supprimer des articles, charger une photo (8 Mo maximum), enregistrer un brouillon et publier. Les brouillons sont cachés aux visiteurs, y compris sur leur URL directe. Le contenu est du texte brut, avec paragraphes automatiques et HTML échappé.

## Démonstration

`python manage.py demo` ajoute six exemples et crée le compte local `louis` s’il n’existe pas. Son mot de passe aléatoire est affiché une seule fois. Les textes sont fictifs et les photos Unsplash sont illustratives. Supprime ou remplace ces articles dans l’atelier avant une vraie publication. La commande est réexécutable sans duplication et ne change pas les mots de passe existants.

Pour changer un mot de passe : `python manage.py changepassword louis`.

## Vérification

```sh
python manage.py check
python manage.py test
```

## Mise en production

Ce projet est lancé en développement local ; il n’est pas déployé sur Internet. Sites ne fournit pas l’hébergement Python/Django nécessaire. Choisir un hébergeur Python avec stockage persistant, puis définir `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` et `DJANGO_ALLOWED_HOSTS`. Utiliser un serveur WSGI (par exemple Gunicorn), HTTPS et un serveur pour les fichiers statiques (`collectstatic`) et médias. Sauvegarder SQLite et les photos, ou configurer PostgreSQL pour un usage plus important. Exécuter `python manage.py check --deploy`. Le serveur `runserver` sert uniquement au développement.

Les polices Google Fonts et les photos de démonstration demandent une connexion Internet ; les polices système et les articles restent disponibles sans elles. La base, les photos chargées et la clé locale sont ignorées par Git. Pour la connexion exposée sur Internet, prévoir une limitation des tentatives au niveau du proxy ou avec un module dédié.
