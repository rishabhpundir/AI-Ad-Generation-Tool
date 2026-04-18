from django.contrib import admin
from scriptdata.models import *

# Register your models here.
@admin.register(AdScript)
class AdScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'platform', 'ad_type', 'industry', 'created_at')
    search_fields = ('filename', 'ad_file')

