""" Profiles Admin """
from __future__ import unicode_literals
from django.contrib import admin

from profiles.models import UserProfile
from profiles.forms import ProfileForm
from authtools.admin import NamedUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    """ Added field to user admin """
    model = UserProfile
    form = ProfileForm
    extra = 1
    fields = ['api_key', 'registered_for_api', 'banned', 'ip', 'country', 'institution', 'comment']
    readonly_fields = ('api_key',)
    can_delete = False
    max_num = 1

    def has_add_permission(self, request):
        """ Can't add more than one profile per user """
        return False


class NewUserAdmin(NamedUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('is_active', 'email', 'name', 'is_superuser', 'is_staff', 'group', 'country',
                    'institution')
    list_filter = ('profile__country', 'is_active', 'profile__institution', 'name', 'email')
    ordering = ['name', 'email', 'is_staff']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(NewUserAdmin, self).get_fieldsets(request, obj)
        # all fieldset except first one should be collapsed
        for fieldset in fieldsets[1:]:
            fieldset[1].update({'classes': ('grp-collapse grp-closed',)})
        return fieldsets

    def country(self, obj):
        return obj.profile.country.name

    def institution(self, obj):
        return obj.profile.institution

    def group(self, obj):
        return ','.join(group.name for group in obj.groups.all())

    def api_key(self, obj):
        return obj.profile.api_key

admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
