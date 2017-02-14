""" Retrieve runner list """
from __future__ import unicode_literals


def get_runners_list(raw=False):
    """
    Retrieve enabled waves_adaptors list from waves settings env file
    :return: a list of Tuple 'value'/'label'
    """
    from waves_addons.loader import load_core, load_addons
    grp_impls = {'': 'Select a implementation class...'}
    raw_impls = []
    for adaptor in load_core() + load_addons():
        grp_name = adaptor[1].__module__.split('.')[2]
        if grp_name not in grp_impls:
            grp_impls[grp_name] = []
        grp_impls[grp_name].append(('.'.join((adaptor[1].__module__, adaptor[1].__name__)), adaptor[0]))
        raw_impls.append(adaptor[0])
    if not raw:
        final = sorted((grp_key, grp_val) for grp_key, grp_val in grp_impls.items())
        return sorted(final, key=lambda tup: tup[0])
    else:
        return raw_impls
