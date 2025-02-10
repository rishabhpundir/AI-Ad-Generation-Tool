from django.contrib import admin
from main.models import *

@admin.register(TrafficSource)
class TrafficSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    search_fields = ('name', 'external_id')

@admin.register(AdSource)
class AdSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad_source_id', 'ad_account_id', 'platform')
    search_fields = ('ad_source_id', 'ad_account_id', 'platform')

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tag', 'disregarded', 'organic', 'ad_source', 'traffic_source', 'creation_date')
    list_filter = ('disregarded', 'organic', 'traffic_source', 'ad_source')
    search_fields = ('name', 'tag')

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'source', 'creation_date')
    list_filter = ('source',)
    search_fields = ('name',)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'external_id', 'creation_date', 'first_name', 'last_name', 'first_source', 'last_source')
    list_filter = ('first_source', 'last_source')
    search_fields = ('email', 'external_id', 'first_name', 'last_name')
