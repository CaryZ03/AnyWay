import os
import django
from django.conf import settings
from django.db import connections, connection
from django.core.management import call_command

# Ensure Django settings are loaded for pytest collection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiagent.settings')

# Prefer sqlite in-memory DB for tests
os.environ.setdefault('DB_ENGINE', 'django.db.backends.sqlite3')
os.environ.setdefault('DB_NAME', ':memory:')

# Initialize Django
django.setup()

# Force sqlite database settings for tests (remove MySQL-specific OPTIONS)
sqlite_db = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
    'OPTIONS': {},
    'ATOMIC_REQUESTS': False,
}
settings.DATABASES['default'] = sqlite_db
connections.databases['default'] = sqlite_db

# Reset existing default connection wrapper if already created
try:
    connection.close()
    connection.settings_dict.update(sqlite_db)
except Exception:
    pass

# Apply migrations to create test schema
call_command('migrate', run_syncdb=True, verbosity=0)
