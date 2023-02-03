from django.contrib import admin

# Register your models here.
from .models import TmpUser

class TmpUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'LoginUser', 'MBTI', 'ennea_res', 'prefer_movie_id']

admin.site.register(TmpUser, TmpUserAdmin)