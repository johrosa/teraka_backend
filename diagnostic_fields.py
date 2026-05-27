import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
print("Model:", User)
print("Fields:", [f.name for f in User._meta.fields])
print("DB Columns:", [f.db_column or f.name for f in User._meta.fields])
