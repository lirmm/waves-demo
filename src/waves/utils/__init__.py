""" Base Utils classes """
from __future__ import unicode_literals

from django.urls import reverse
from django.utils.safestring import mark_safe


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def normalize_value(value):
    import inflection
    import re
    value = re.sub(r'[^\w\.]+', '_', value)
    return inflection.underscore(value)


def url_to_edit_object(obj):
    """ Retrieve url to access admin change object """
    url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
    return mark_safe('<a class="" href="{}" title="Edit {}">{}</a>'.format(url, obj._meta.model_name, str(obj)))
