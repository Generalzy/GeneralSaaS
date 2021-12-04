import os
import random
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GeneralSaaS.settings")
django.setup()
from web import models

obj_list = []
for i in range(10):
    obj_list.append(models.Issues(project_id=11, issues_type_id=random.choice([1, 2, 3]), creator_id=8,
                                  assign_id=8, status=random.choice([1, 2, 3, 4, 5, 6, 7]),
                                  subject=f'出事了{i}'))

models.Issues.objects.bulk_create(obj_list)
print('objk')
