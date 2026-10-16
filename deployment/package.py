"""Create a private deployment zip with a consistent DB backup and media.

Secrets, session cookies, local virtualenv and Git data are never included.
The DB still contains account password hashes: keep this archive private.
"""
import sqlite3
import tempfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
destination = root / 'deployment' / 'oups-la-cuisine.zip'
folders = ['blog', 'config', 'templates', 'static', 'media', 'deployment']
files = ['manage.py', 'requirements.txt', 'README.md', '.env.example', '.gitignore']
with tempfile.TemporaryDirectory() as temporary:
    backup = Path(temporary) / 'db.sqlite3'
    with sqlite3.connect(root / 'db.sqlite3') as source, sqlite3.connect(backup) as target:
        source.backup(target)
        target.execute('PRAGMA secure_delete = ON')
        target.execute('DELETE FROM django_session')
        for table in ('axes_accessattempt', 'axes_accesslog', 'axes_accessfailurelog'):
            target.execute(f'DELETE FROM {table}')
        target.execute('DELETE FROM django_admin_log')
        target.commit()
        target.execute('VACUUM')
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(backup, 'db.sqlite3')
        for name in files:
            archive.write(root / name, name)
        for folder in folders:
            for path in sorted((root / folder).rglob('*')):
                if not path.is_file() or any(part.startswith('.') or part == '__pycache__' for part in path.relative_to(root).parts):
                    continue
                if path.suffix in ('.pyc', '.zip', '.sqlite3') or path.name == 'pythonanywhere_wsgi.py':
                    continue
                archive.write(path, path.relative_to(root))
destination.chmod(0o600)
print(f'Archive privée : {destination}')
print(f'Taille : {destination.stat().st_size / 1024 / 1024:.1f} Mo')
