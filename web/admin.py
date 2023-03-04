from django.contrib import admin
from web.models import UserInfo, Project, PricePolicy

admin.site.register(Project)
admin.site.register(UserInfo)
admin.site.register(PricePolicy)
