"""Run once on PythonAnywhere with its actual assigned hostname."""
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if len(sys.argv) != 2 or not re.fullmatch(r'[a-zA-Z0-9_-]+\.(?:eu\.)?pythonanywhere\.com', sys.argv[1]):
    raise SystemExit('Usage: python deployment/setup_pythonanywhere.py TON_PSEUDO.eu.pythonanywhere.com')
hostname = sys.argv[1].lower()
env_file = root / '.env'
if not env_file.exists():
    contents = '\n'.join([
        'DJANGO_DEBUG=0',
        f'DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}',
        f'DJANGO_ALLOWED_HOSTS={hostname}',
        'DJANGO_HOSTING=pythonanywhere',
        '',
    ])
    fd = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(contents)

for args in [('migrate', '--noinput'), ('collectstatic', '--noinput'), ('check', '--deploy')]:
    subprocess.run([sys.executable, str(root / 'manage.py'), *args], cwd=root, check=True)

wsgi_path = root / 'deployment' / 'pythonanywhere_wsgi.py'
wsgi_path.write_text(
    'import sys\n'
    f'sys.path.insert(0, {str(root)!r})\n'
    'from config.wsgi import application\n'
)
print(f'Configuration prête pour https://{hostname}/')
print(f'Copier le contenu de {wsgi_path} dans le fichier WSGI de l’onglet Web.')
print(f'Mapping /static/ : {root / "staticfiles"}')
print(f'Mapping /media/ : {root / "media"}')
print('Activer Force HTTPS dans l’onglet Web, puis Reload.')
print('Le compte admin importé conserve son mot de passe. Changement possible dans l’atelier.')
