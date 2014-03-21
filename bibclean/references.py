from unidecode import unidecode
from pyzotero import zotero
import regex
import weakref

reBRK = regex.compile(r"\b((\p{Ll})\p{Ll}*)\b|((\p{Lu})('\p{Lu})?\p{Ll}*)")


def break_name(name):
    parts = [[], []]
    for idx, nm in enumerate(name):
        for p in reBRK.findall(nm):
            if p[0] == '':
                parts[idx].append((p[2], p[3]))
            else:
                parts[idx].append(p[:2])
    return parts


def part_comp(parts, comp):
    return [p[comp] for p in parts]


def inv_idx(idxs, N):
    """
    numbers between in range(0, N) that are not in idxs
    """
    return [idx for idx in range(0, N) if idx not in idxs]


def name_comp(a, b):
    """
    Calculate comparison score between two Unicode name tuples (last, first)
    """
    # Break names into parts --------------------------------------------------
    # Name a
    ap = break_name(a)           # Unicode parts
    aa = name_to_ascii(a)        # ASCII name
    aap = break_name(aa)         # ASCII parts
    lnap = part_comp(aap[0], 0)  # Full ASCII last name parts
    # Name b
    bp = break_name(b)
    ba = name_to_ascii(b)
    bap = break_name(ba)
    lnbp = part_comp(bap[0], 0)
    # Score Last Name ---------------------------------------------------------
    # Get array of tuples [(ai,bi)] where lnap[ai] == lnbp[bi]
    lnm = [(idx, lnbp.index(n)) for idx, n in enumerate(lnap) if n in lnbp]
    if not lnm:  # No matches for last name
        return 0
    score = 0.0
    if a[0] == b[0]:                               # Last name Uni full match
        score += 2
    elif aa[0] == ba[0]:                           # Last name ASCII full match
        score += 1.75
    elif len(lnm) == max([len(lnap), len(lnbp)]):  # Out of order ASCII match
        for idx in lnm:
            if ap[0][idx[0]][0] == bp[0][idx[1]][0]:
                score += 0.75
            else:
                score += 0.5
    else:  # Partial match, add non-matching parts to first name parts
        for idx in lnm:
            if ap[0][idx[0]][0] == bp[0][idx[1]][0]:
                score += 0.75
            else:
                score += 0.5
        aiidx = inv_idx(part_comp(lnm, 0), len(ap[0]))
        biidx = inv_idx(part_comp(lnm, 1), len(bp[0]))
        ap[1] += [ap[0][idx] for idx in aiidx]
        aap[1] += [aap[0][idx] for idx in aiidx]
        bp[1] += [bp[0][idx] for idx in biidx]
        bap[1] += [bap[0][idx] for idx in biidx]
    # Insure that more first name parts are in  a than b
    if len(ap[1]) < len(bp[1]):
        tmp = ap
        ap = bp
        bp = tmp
        tmp = aap
        aap = bap
        bap = aap
    # Build arrays needed for scoring first names
    # Arrays for a
    afns = part_comp(ap[1], 0)    # Full Uni first name parts
    ains = part_comp(ap[1], 1)    # First name Uni initials
    aafns = part_comp(aap[1], 0)  # Full ASCII fist name parts
    aains = part_comp(aap[1], 1)  # First name ASCII initials
    # Arrays for b
    bfns = part_comp(bp[1], 0)
    bins = part_comp(bp[1], 1)
    bafns = part_comp(bap[1], 0)
    bains = part_comp(bap[1], 1)
    # Score First Name --------------------------------------------------------
    for idx in range(0, len(afns)):
        if afns[idx] in bfns:      # Full Uni
            tidx = bfns.index(afns[idx])
            score += 2/(idx+tidx+2)
        elif aafns[idx] in bafns:  # Full ASCII
            tidx = bafns.index(aafns[idx])
            score += 1.75/(idx+tidx+2)
        elif ains[idx] in bins:    # Uni Initials
            tidx = bins.index(ains[idx])
            score += 1/(idx+tidx+2)
        elif aains[idx] in bains:  # ASCII Initials
            tidx = bains.index(aains[idx])
            score += 1/(idx+tidx+2)
    return score


def name_to_ascii(name):
    """
    Changes names to pseudo-ASCII equivilent
    e.g. ('Ó Súilleabháin', 'Jörg Tanjō') -> ("O'Suilleabhain", 'Jorg Tanjo')
    """
    name = [regex.sub(r'\bÓ\s?(\p{Lu})', 'O\'\g<1>', n) for n in name]
    return tuple([regex.sub(r'`', '\'', unidecode(n)) for n in name])


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

    @property
    def ascii_name(self):
        return name_to_ascii(self._name)

    def add_contribution(self, item, name):
        contrib = Contributor(item, self, name)
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

    def __str__(self):
        return ''.join(['Person: ', ', '.join(self.name), '; Items: ',
                        str(len(self.contributions))])


class Contributor(object):
    """
    Author Info
    """
    def __init__(self, item, person, name):
        self.item = weakref.proxy(item)
        self.person = weakref.proxy(person)
        self._name = name

    @property
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

    def cocontributors(self):
        return [con for con in self.item.contributors if con is not self]

    def change_person(self, person):
        self.person.contributions.remove(self)
        if person.name != self.name:
            self.name = person.name
        self.person = weakref.proxy(person)

    def __str__(self):
        return ''.join(['Contrib: ', ', '.join(self.name)])
