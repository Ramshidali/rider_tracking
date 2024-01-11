from django.contrib import admin

from locations.models import Location

# Register your models here.
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id','location','short_name','latitude','longitude']
admin.site.register(Location,LocationAdmin)