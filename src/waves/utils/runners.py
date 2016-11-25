import sys

import waves.settings


def get_runners_list(raw=False):
    """
    Retrieve enabled adaptors list from waves settings env file
    :return: a list of Tuple 'value'/'label'
    """
    from django.utils.module_loading import import_module
    for adaptor_mod in waves.settings.WAVES_ADAPTORS_MODS:
        available_impl = import_module(adaptor_mod)
        impls = [adapt for adapt in available_impl.CURRENT_IMPLEMENTATION()]
        grp_impls = {'': 'Select a implementation class...'}
        raw_impls = []
        for adaptor in impls:
            mod = sys.modules[adaptor.__module__]
            grp_name = getattr(mod, 'grp_name', 'None')
            if grp_name not in grp_impls:
                grp_impls[grp_name] = []
            grp_impls[grp_name].append(("%s.%s" % (adaptor.__module__, adaptor.__name__),
                                        adaptor.name if hasattr(adaptor, 'name') else "%s.%s" % (
                                        adaptor.__module__, adaptor.__name__)))
            raw_impls.append("%s.%s" % (adaptor.__module__, adaptor.__name__))
    if not raw:
        final = sorted((grpkey, grpvals) for grpkey, grpvals in grp_impls.items())
        return sorted(final, key=lambda tup: tup[0])
    else:
        return raw_impls