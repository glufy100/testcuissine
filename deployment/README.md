# Déployer sur PythonAnywhere gratuitement

L’archive `oups-la-cuisine.zip` contient les articles, les photos et les comptes existants avec leurs mots de passe hachés. Elle est privée : ne pas l’envoyer sur un dépôt public. Les sessions, les secrets, l’environnement virtuel et les journaux d’accès sont exclus. Pour la recréer : `.venv/bin/python deployment/package.py`.

1. Créer un compte gratuit sur https://eu.pythonanywhere.com/pricing/ et se connecter. L’acceptation des conditions et le choix du mot de passe de l’hébergeur sont effectués par le propriétaire.
2. Dans Files, téléverser l’archive dans le répertoire personnel. Dans une console Bash, lancer :

```bash
mkdir -p ~/oups-la-cuisine
unzip -n ~/oups-la-cuisine.zip -d ~/oups-la-cuisine
cd ~/oups-la-cuisine
python3.12 -m venv ~/.virtualenvs/oups
source ~/.virtualenvs/oups/bin/activate
pip install -r requirements.txt
python deployment/setup_pythonanywhere.py TON_PSEUDO.eu.pythonanywhere.com
```

Remplacer `TON_PSEUDO` par le nom exact du compte. Choisir Python 3.12 dans l’onglet Web ; si cette version n’est pas proposée, choisir une version compatible (3.10 ou plus récente) et utiliser la même pour l’environnement virtuel.

3. Dans Web, créer une application **Manual configuration**, renseigner `~/.virtualenvs/oups` comme virtualenv. Dans le fichier WSGI fourni par PythonAnywhere, remplacer le contenu par celui généré dans `~/oups-la-cuisine/deployment/pythonanywhere_wsgi.py`.
4. Dans Static files, ajouter les deux mappings affichés par le script : `/static/` vers `~/oups-la-cuisine/staticfiles` et `/media/` vers `~/oups-la-cuisine/media` (utiliser les chemins absolus `/home/TON_PSEUDO/...`). Ne jamais mapper le répertoire du projet entier.
5. Activer **Force HTTPS**, puis **Reload**.
6. Vérifier l’accueil, les six photos, la redirection de `/admin/` vers la connexion et une connexion admin en HTTPS. Dans l’atelier, utiliser « Changer mon mot de passe » pour choisir un mot de passe personnel d’au moins 14 caractères. Le compte existant est `louis`. Si le mot de passe a été perdu, utiliser `python manage.py changepassword louis` dans la console, sans partager le nouveau mot de passe.

Le `.env` de production est créé sur le serveur avec une nouvelle clé secrète. Il est chargé par Django pour les consoles comme pour WSGI. Ne pas réutiliser `.local-secret` et ne pas activer DEBUG en ligne.

Après 5 échecs, la connexion est bloquée pendant 15 minutes. Pour débloquer un compte légitime depuis la console : `python manage.py axes_reset_username louis`. Les sessions admin expirent à la fermeture du navigateur ou après deux heures. Le blog reste accessible publiquement ; la rédaction et la gestion des comptes nécessitent un compte administrateur actif (équipe et superutilisateur).

Sauvegarder régulièrement `db.sqlite3` et `media/`. Ne jamais réextraire une ancienne base par-dessus les articles en production. L’offre gratuite a des limites de stockage et une activation à renouveler depuis le tableau de bord.
