def del_none(d: dict) -> dict:
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input, so you may wish to ``copy`` the dict first.

    Courtesy Chris Morgan and modified from:
    https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    del_none(item)
    return d  # For convenience


def replace_unique_id_and_remove_none(d: dict) -> dict:
    """
    Replace objects in values which have a "_unique_id" attribute by their unique id.
    Also delete keys with the value ``None``.
    All this recursively.

    This alters the input, so you may wish to ``copy`` the dict first.

    Courtesy Chris Morgan and modified from:
    https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif hasattr(value, "_unique_id"):
            d[key] = value._unique_id
        elif isinstance(value, dict):
            del_none(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    del_none(item)
    return d  # For convenience
