from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow)
