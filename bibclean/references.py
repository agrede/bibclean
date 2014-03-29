from peoplenames import name_comp, name_to_ascii, fullest_name, is_name
from simpleplugins import PluginMount
from bibdates import BibDateParser
import weakref


class References(metaclass=PluginMount):
    """
    Parent of reference sources
    """
    name = "Base References"

    def __init__(self, *cargs, **kwargs):
        self.test = kwargs.get('test', False)
        self.items = []
        self.people = {}
        self.date_parser = BibDateParser()

    def get_all(self):
        pass

    def get_person(self, name):
        if not name[0] in self.people:
            self.people[name[0]] = {}
        if name[1] not in self.people[name[0]]:
            self.people[name[0]][name[1]] = Person(name)
        return self.people[name[0]][name[1]]

    def remove_person_if_empty(self, name):
        try:
            if len(self.people[name[0]][name[1]]) < 1:
                del(self.people[name[0]][name[1]])
                if len(self.people[name[0]]) < 1:
                    del(self.people[name[0]])
                return True
            else:
                return False
        except:
            return True


class Item:
    """
    Item
    """
    name = "Base Item"

    def __init__(self, parent, *cargs, **kwargs):
        self.parent = weakref.proxy(parent)
        self.contributors = []
        self._add_contributors()

    def update(self):
        pass

    def update_contributor(self, idx, name):
        pass

    def _update_field(self, field, value):
        pass

    def _field_value(self, field):
        pass

    def _add_contributors(self):
        pass

    @property
    def title(self):
        return self._field_value('title')

    @title.setter
    def title(self, value):
        self._update_field('title', value)

    @property
    def title_short(self):
        return self._field_value('title_short')

    @title_short.setter
    def title_short(self, value):
        self._update_field('title_short', value)

    @property
    def url(self):
        return self._field_value('url')

    @url.setter
    def url(self, value):
        self._update_field('url', value)

    @property
    def journal(self):
        return self._field_value('journal')

    @journal.setter
    def journal(self, value):
        self._update_field('journal', value)

    @property
    def journal_abbrev(self):
        return self._field_value('journal_abbrev')

    @journal_abbrev.setter
    def journal_abbrev(self, value):
        self._update_field('journal_abbrev', value)

    @property
    def date(self):
        return self._field_value('date')

    @date.setter
    def date(self, value):
        self._update_field('date', value)

    def formatted_date(self):
        return self.parent.date_parser.parse_to_str(self.date)


class Person:
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
        if is_name(value):
            self._name = value
        else:
            raise Exception('Invalid name')

    def compare(self, person):
        return name_comp(self.name, person.name)

    def cocontributors(self, ignore=[]):
        cocons = []
        counts = []
        for contrib in self.contributions:
            for cocon in contrib.cocontributors():
                if cocon.person in ignore:
                    continue
                elif cocon.person not in cocons:
                    cocons.append(cocon.person)
                    counts.append(1)
                else:
                    idx = cocons.index(cocon.person)
                    counts[idx] += 1
        return zip(cocons, counts)

    def condensed_cocontributors(self, min_score, ignore=[]):
        # Get uncondensed list of cocontribs, ignore not used to catch more
        cocons = sorted(self.cocontributors(),
                        key=lambda c: c[0].ascii_name)
        cond_cocons = []
        cur_cocon = list(cocons[0])
        # ignore_flag is True when any of similar people is in ignore
        ignore_flag = cur_cocon[0] in ignore
        for cocon in cocons[1:]:
            if cur_cocon[0].compare(cocon[0]) >= min_score:
                ignore_flag = ignore_flag or cocon[0] in ignore
                cur_cocon[1] += cocon[1]
                if cocon[0].name is fullest_name(cur_cocon[0].name,
                                                 cocon[0].name):
                    cur_cocon[0] = cocon[0]
            else:
                if not ignore_flag:
                    cond_cocons.append(cur_cocon)
                cur_cocon = list(cocon)
                ignore_flag = cur_cocon[0] in ignore
        if not ignore_flag:
            cond_cocons.append(cur_cocon)
        return cond_cocons

    def complex_compare(self, person, min_score):
        simp = self.compare(person)
        if simp == 0:
            return 0
        comp_list = sorted(
            [(x[0], x[1], 'a')
             for x in self.condensed_cocontributors(min_score,
                                                    ignore=[person])]
            + [(x[0], x[1], 'b')
               for x in person.condensed_cocontributors(min_score,
                                                        ignore=[self])],
            key=lambda x: x[0].ascii_name
        )
        cur_score = 0
        a = comp_list[0]
        for b in comp_list[1:]:
            cmpscore = a[0].compare(b[0])
            if a[2] is not b[2] and cmpscore >= min_score:
                cur_score += cmpscore*(a[1]+b[1])
            a = b
        return simp*cur_score

    def __str__(self):
        return ''.join(['Person: ', ', '.join(self.name), '; Items: ',
                        str(len(self.contributions))])

    def __lt__(self, other):
        return ' '.join(self.ascii_name) < ' '.join(other.ascii_name)


class Contributor:
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
            try:
                self.item.update_contributor(idx, value)
            except:
                raise
            else:
                self._name = value

    @property
    def person(self):
        return self._person

    @person.setter
    def person(self, value):
        try:
            self.name = value.name
        except:
            raise
        else:
            prev_name = self._person.name
            value.contributions.add(self)
            self._person.contributions.remove(self)
            self._person = weakref.proxy(value)
            self.item.parent.remove_person_if_empty(prev_name)

    def cocontributors(self):
        return [con for con in self.item.contributors if con is not self]

    def __str__(self):
        return ''.join(['Contrib: ', ', '.join(self.name)])
