from django.contrib import admin
from .models import UserDetails


class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'gender',
                    'division', 'district', 'phone')
    search_fields = ('user__email', 'user__username',
                     'user__first_name', 'user__last_name', 'district', 'phone')
    list_filter = ('gender', 'division')


admin.site.register(UserDetails, UserDetailsAdmin)
