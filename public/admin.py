from django.contrib import admin
from public.models import UserProfile
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from public.models import WordUse


class UserProfileInline(admin.TabularInline):
    model = UserProfile


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(WordUse)
