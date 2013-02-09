from django.contrib import admin
from public.models import Poll, Choice, UserProfile
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'pub_date', 'was_published_recently')
    fieldsets = [
        (None,               {'fields': ['question']}),
        ('Date information', {
            'fields': ['pub_date'],
            'classes': ['collapse']
        }),
    ]
    inlines = [ChoiceInline]
    list_filter = ['pub_date']
    search_fields = ['question']
    date_hierarchy = 'pub_date'


#class UserProfileAdmin(admin.ModelAdmin):
#    list_display = (
#        'user', 'access_token', 'token_type', 'token_expiration'
#    )
#    list_filter = ['token_expiration']
#    search_fields = ['user']
#    date_hierarchy = 'token_expiration'
#

class UserProfileInline(admin.TabularInline):
    model = UserProfile


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]


admin.site.register(Poll, PollAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
