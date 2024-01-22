from django.contrib import admin

from Apps.users.models import Profile

class UserAdmin(admin.ModelAdmin):
  list_display = ('user', 'name', 'last_name', 'picture', 'email', 'role')
  ordering = ('picture', 'email',)

admin.site.register(Profile, UserAdmin)