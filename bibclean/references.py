from unidecode import unidecode
from pyzotero import zotero
import re
import weakref


def name_to_ascii(name):
    return [re.sub(r'`', '\'', unidecode(n)) for n in name]


class References(object):
    """
    Parent of reference sources
    """
    def __init__(self, dbc, dbc_params):
        self.dbc = zotero.Zotero(dbc_params['library_id'],
                                 'user', dbc_params['api_key'])
        self.dbc_params = dbc_params
        self.items = []
        self.people = {}

    def get_all(self):
        items_raw = self._dbc.everything(self._dbc.top())
        for item_raw in items_raw:
            self.add_item(self, item_raw)

    def add_item(self, raw):
        self.items.append(Item(self, raw))

    def get_person(self, name):
        if not name[0] in self.people:
            self.people[name[0]] = {}
        if name[1] in self.people[name[0]]:
            return self.people[name[0]][name[1]]
        else:
            self.people[name[0]][name[1]] = Person(name)


class Item(object):
    """
    Item
    """
    def __init__(self, parent, raw):
        self._raw = raw
        self.parent = weakref.ref(parent)
        self.contributors = []

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

    def _add_contributor(self):
        if 'creators' in self._raw:
            for creator in self._raw['creators']:
                if 'firstName' in creator and 'lastName' in creator:
                    name = [creator['lastName'], creator['firstName']]
                    person = self.parent.get_person(name)
                    self.contributors.append(
                        person.add_contribution(self, name))

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

    def update_contributor(self, idx, name):
        if 'creators' in self._raw:
            self._raw['creators'][idx]['lastName'] = name[0]
            self._raw['creators'][idx]['firstName'] = name[1]
            self.update()


class Person(object):
    """
    Person
    """
    def __init__(self, name):
        self.contributions = []
        self._name = name

    def ascii_name(self):
        return name_to_ascii(self._name)

    def add_contribution(self, item, name):
        contrib = Contributer(item, self, name)
        if self._name != name:
            contrib.name = self._name
        self.contributions.append(contrib)
        return contrib

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        for c in self.contributions:
            if c.name != value:
                c.name = value

    def __str__(self):
        return print(', '.join(self._name))


class Contributer(object):
    """
    Author Info
    """
    def __init__(self, item, person, name):
        self.item = weakref.ref(item)
        self.person = weakref.ref(person)
        self._name = name

    def ascii_name(self):
        return name_to_ascii(self._name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        idx = self.item.index(self)
        if self._name != value:
            self.item.update_contributor(idx, value)
            self._name = value

    def change_person(self, person):
        self.person.contributions.remove(self)
        if person.name != self.name:
            self.name = person.name
        self.person = weakref.ref(person)
