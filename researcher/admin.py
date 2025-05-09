from django.contrib import admin
from .models import Workspace, CompanyProfile, CompanyDocument

# Register your models here.
admin.site.register(Workspace)
admin.site.register(CompanyProfile)
admin.site.register(CompanyDocument)
