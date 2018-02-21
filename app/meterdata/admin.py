from django.contrib import admin

from .models import MeterInput

class MeterAdmin(admin.ModelAdmin):
    list_display = ('title', 'directory')

admin.site.register(MeterInput, MeterAdmin)