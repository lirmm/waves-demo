from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django_countries.widgets import CountrySelectWidget
from waves.models import Service, APIProfile
import waves.const

__all__ = ['UserForm', 'ProfileForm']

User = get_user_model()


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('name'),
        )

    class Meta:
        model = User
        fields = ['name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = APIProfile
        fields = ['api_key', 'registered_for_api', 'comment', 'ip', 'country', 'comment', 'institution',
                  'authorized_services']

    filter_horizontal = ['authorized_services']
    widgets = {
        'country': CountrySelectWidget()
    }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['authorized_services'].initial = \
                (self.instance.authorized_services.all())
            # (self.instance.authorized_services.filter(status=waves.const.SRV_PUBLIC) if self.instance.pk else ())
    # TODO repair bug in backoffice when disabling API access.

    authorized_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(api_on=True, status=waves.const.SRV_PUBLIC),
        required=False,
        # limit_choices_to=Service.objects.filter(api_on=True, status=waves.const.SRV_PUBLIC),
        widget=FilteredSelectMultiple(
            verbose_name='access to services',
            is_stacked=False,
        )
    )

    def save(self, commit=True):
        return super(ProfileForm, self).save(commit)
