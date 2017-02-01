""" Retrieve runner list """
from __future__ import unicode_literals

from django.conf import settings


def get_runners_list(raw=False):
    """
    Retrieve enabled adaptors list from waves settings env file
    :return: a list of Tuple 'value'/'label'
    """
    from django.utils.module_loading import import_module
    grp_impls = {'': 'Select a implementation class...'}
    raw_impls = []
    from waves.adaptors.core import ADAPTORS_LIST
    impls = ADAPTORS_LIST
    for mod in settings.WAVES_ADAPTORS_MODS:
        available_impl = import_module(mod)
        impls.extend([adapt for adapt in available_impl.ADAPTORS_LIST])
    for adaptor in impls:
        grp_name = adaptor[2].split('/', 1)[0]
        if grp_name not in grp_impls:
            grp_impls[grp_name] = []
        grp_impls[grp_name].append((adaptor[0], adaptor[1]))
        raw_impls.append(adaptor[0])
    if not raw:
        final = sorted((grp_key, grp_val) for grp_key, grp_val in grp_impls.items())
        return sorted(final, key=lambda tup: tup[0])
    else:
        return raw_impls
