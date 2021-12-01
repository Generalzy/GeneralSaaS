import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GeneralSaaS.settings")
django.setup()
from web import models

p=models.Project.objects.filter(pk=10).first()
print(p.delete())