def normalize_value(value):
    import inflection
    import re
    value = re.sub(r'[^\w\.]+', '_', value)
    return inflection.underscore(value)