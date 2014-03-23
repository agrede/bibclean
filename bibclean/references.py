from pyzotero import zotero
from peoplenames import name_comp, name_to_ascii, fullest_name
import weakref


class References(object):
    """
    Parent of reference sources
    """
    def __init__(self, dbc, dbc_params, *cargs, **kwargs):
        self.test = kwargs.get('test', False)
        self.dbc = zotero.Zotero(dbc_params['library_id'],
                                 'user', dbc_params['api_key'])
        self.dbc_params = dbc_params
        self.items = []
        self.people = {}

    def get_all(self):
        items_raw = self.dbc.everything(self.dbc.top())
        for item_raw in items_raw:
            self.add_item(item_raw)

    def add_item(self, raw):
        self.items.append(Item(self, raw))

    def get_person(self, name):
        if not name[0] in self.people:
            self.people[name[0]] = {}
        if name[1] not in self.people[name[0]]:
            self.people[name[0]][name[1]] = Person(name)
        return self.people[name[0]][name[1]]


class Item(object):
    """
    Item
    """
    def __init__(self, parent, raw):
        self._raw = raw
        self.parent = weakref.proxy(parent)
        self.contributors = []
        self._add_contributor()

    def update(self):
        if self.parent.test:
            return True
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
                    name = (creator['lastName'], creator['firstName'])
                    person = self.parent.get_person(name)
                    contrib = Contributor(self, person, name)
                    self.contributors.append(contrib)
                    person.contributions.add(contrib)

    @property
    def title(self):
        return self._field_value('title')

    @title.setter
    def title(self, value):
        return self._update_field('title', value)

    @property
    def title_short(self):
        return self._field_value('shortTitle')

    @title.setter
    def title(self, value):
        return self._update_field('shortTitle', value)

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
        self.contributions = weakref.WeakSet()
        self._name = name

    @property
    def ascii_name(self):
        return name_to_ascii(self._name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        for c in self.contributions:
            if c.name != value:
                c.name = value
        self._name = value

    def compare(self, person):
        return name_comp(self.name, person.name)

    def cocontributors(self):
        cocontrib = []
        counts = []
        for contrib in self.contributions:
            for cocon in contrib.cocontributors():
                if cocon.person not in cocontrib:
                    cocontrib.append(cocon.person)
                    counts.append(1)
                else:
                    idx = cocontrib.index(cocon.person)
                    counts[idx] += 1
        return zip(cocontrib, counts)

    def condensed_cocontributors(self, min_score):
        cocontribs = sorted(self.cocontributors, key=lambda c: c[0].ascii_name)
        cond_cocontrib = []
        cur_cocontrib = cocontribs.pop()
        for cocon in cocontribs:
            if name_comp(cur_cocontrib[0].name, cocon[0].name) >= min_score:
                cur_cocontrib[1] += cocon[1]
                if cocon[0].name is fullest_name(cur_cocontrib[0].name,
                                                 cocon[0].name):
                    cur_cocontrib[0] = cocon[0]
            else:
                cond_cocontrib.append(cur_cocontrib)
                cur_cocontrib = cocon
        cond_cocontrib.append(cur_cocontrib)
        return cond_cocontrib

    def __str__(self):
        return ''.join(['Person: ', ', '.join(self.name), '; Items: ',
                        str(len(self.contributions))])

    def __lt__(self, other):
        return ' '.join(self.ascii_name) < ' '.join(other.ascii_name)


class Contributor(object):
    """
    Contributor
    """
    def __init__(self, item, person, name):
        self.item = weakref.proxy(item)
        self._person = weakref.proxy(person)
        self._name = name

    @property
    def ascii_name(self):
        return name_to_ascii(self._name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        idx = self.item.contributors.index(self)
        if self._name != value:
            self.item.update_contributor(idx, value)
            self._name = value

    @property
    def person(self):
        return self._person

    @person.setter
    def person(self, value):
        value.contributions.add(self)
        self._person.contributions.remove(self)
        self._person = weakref.proxy(value)
        self.name = value.name

    def cocontributors(self):
        return [con for con in self.item.contributors if con is not self]

    def __str__(self):
        return ''.join(['Contrib: ', ', '.join(self.name)])
