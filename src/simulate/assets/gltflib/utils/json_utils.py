# Copyright 2022 The HuggingFace Authors.
# Copyright (c) 2019 Sergey Krilov
# Copyright (c) 2018 Luke Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Lint as: python3


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
