from unidecode import unidecode
from pyzotero import zotero
import re
import weakref


class References(object):
    """
    Parent of reference sources
    """
    def __init__(self, dbc, dbc_params):
        self.dbc = zotero.Zotero(dbc_params['library_id'],
                                 'user', dbc_params['api_key'])
        self.dbc_params = dbc_params
        self._items = []

    def get_all(self):
        items_raw = self._dbc.everything(self._dbc.top())
        for item_raw in items_raw:
            self.add_item(self, item_raw)

    def add_item(self, raw):
        self._items.append(Item(self, raw))


class Item(object):
    """
    Item
    """
    def __init__(self, parent, raw):
        self._raw = raw
        self.parent = weakref.ref(parent)
        self.people = []

    def update(self):
        if self.parent.dbc.check_items([self._raw]):
            try:
                self._raw = self.parent.update_item(self._raw)
                return True
            except:
                raise
        return False

    def _update_field(self, field, value):
        tmp = self._raw[field] = value
        self._raw[field] = value
        try:
            self.update()
        except:
            self._raw[field] = tmp
            raise

    def _field_value(self, field):
        if field in self._raw:
            return self._raw[field]
        else:
            return None

    def _add_people(self):
        if 'creators' in self._raw:
            for creator in self._raw['creators']:
                if 'firstName' in creator and 'lastName' in creator:
                    self._people.append(Person(self,
                                               creator['firstName'],
                                               creator['lastName']))

    def people(self):
        return self._people

    @property
    def url(self):
        return self._field_value('url')

    @url.setter
    def url(self, value):
        self._update_field('url', value)

    @property
    def journal(self):
        return self._field_value('publicationTitle')

    @journal.setter
    def journal(self, value):
        self._update_field('publicationTitle', value)

    @property
    def journal_abbrev(self):
        return self._field_value('journalAbbreviation')

    @journal_abbrev.setter
    def journal_abbrev(self, value):
        self._update_field('journalAbbreviation', value)

    @property
    def date(self):
        self._field_value('date')

    @date.setter
    def date(self, value):
        self._update_field('date', value)

    def update_person(self, idx, name):
        if 'creators' in self._raw:
            tmp = self._raw['creators'][idx]
            self._raw['creators'][idx]['lastName'] = name[0]
            self._raw['creators'][idx]['firstName'] = name[1]
            try:
                return self.update()
            except:
                self._raw['creators'][idx] = tmp
                raise
                return False
        return False


class People(object):
    """
    People
    """
    def __init__(self, parent):
        self.parent = weakref.ref(parent)

    def __iter__(self):
        return self


class Person(object):
    """
    Author Info
    """
    def __init__(self, parent, name_first, name_last):
        self.parent = weakref.ref(parent)
        self._name = [name_last, name_first]
        self._set_ascii_name()

    def _set_ascii_name(self):
        self._ascii_name = [re.sub(r'`', '\'', unidecode(n))
                            for n in self._name]

    def name(self, idx, uni):
        if uni:
            return self._name[idx]
        else:
            return self._ascii_name[idx]

    def name_last(self, *args, **kwargs):
        uni = kwargs.get('uni', False)
        return self.name(0, uni)

    def name_first(self, *args, **kwargs):
        uni = kwargs.get('uni', True)
        return self.name(1, uni)

    def update(self, name):
        idx = self.parent.people.index(self)
        try:
            if self.parent.update_person(idx, name):
                self._name = name
                self._set_ascii_name()
                return True
        except:
            raise
            return False
        return False
