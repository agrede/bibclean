from unidecode import unidecode
import re
import weakref

class References(object):
    """
    Parent of reference sources
    """
    def __init__(self):
        self._items = []
        self._authors = []
        self._journals = []


class Item(object):
    """
    Item
    """
    def __init__(self, parent, raw):
        self._raw = raw


class Author(object):
    """
    Author Info
    """
    def __init__(self, parent, name_first, name_last):
        self.parent = weakref.ref(parent)
        self._name = [name_last, name_first]
        self._ascii_name = [unidecode(n) for n in self._name]

    def get_name(self, idx, uni):
        if uni:
            return self._name[idx]
        else:
            return self._ascii_name[idx]

    def name_last(self, *args, **kwargs):
        uni = kwargs.get('uni', False)
        return self.get_name(0, uni)

    def name_first(self, *args, **kwargs):
        uni = kwargs.get('uni', True)
        return self.get_name(1, uni)
