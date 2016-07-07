from __future__ import unicode_literals

from authtools.admin import NamedUserAdmin
from django.contrib import admin
from django.contrib.auth import get_user_model

from waves.forms.admin import ProfileForm
from waves.models.profiles import APIProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = APIProfile
    form = ProfileForm
    extra = 0
    fields = ['api_key', 'registered_for_api', 'ip', 'country', 'institution', 'authorized_services',
              'comment']
    readonly_fields = ('api_key',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class NewUserAdmin(NamedUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('is_active', 'email', 'name', 'apikey', 'is_superuser', 'is_staff', 'group', 'country',
                    'institution')

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

    def apikey(self, obj):
        return obj.profile.api_key

admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
