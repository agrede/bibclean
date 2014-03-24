from pyzotero import zotero
from References import References, Item, Contributor


class ZoteroRefs(References):
    """
    Ref
    """
    name = "ZoteroRefs"

    def __init__(self, *cargs, **kwargs):
        super().__init__(cargs=cargs, kwargs=kwargs)
        library_id = kwargs.get('library_id', None)
        api_key = kwargs.get('api_key', None)
        self.dbc = zotero.Zotero(library_id, 'user', api_key)

    def get_all(self):
        items_raw = self.dbc.everything(self.dbc.top())
        for item_raw in items_raw:
            pass


class ZoteroItem(Item):
    name = "ZoteroItem"

    def __init__(self, parent, *cargs, **kwargs):
        super().__init__(cargs=cargs, kwargs=kwargs)
        self._raw = kwargs.get('raw', None)
        self._add_contributors()
        self._field_names = {'title': 'title', 'title_short': 'shortTitle',
                             'url': 'url', 'journal': 'publicationTitle',
                             'journal_abbrev': 'journalAbbreviation',
                             'date': 'date'}

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

        def update_contributor(self, idx, name):
            if 'creators' in self._raw:
                self._raw['creators'][idx]['lastName'] = name[0]
                self._raw['creators'][idx]['firstName'] = name[1]
                self.update()

    def _update_field(self, field, value):
        key = self._field_names[field]
        tmp = self._raw[key] = value
        self._raw[key] = value
        try:
            self.update()
        except:
            self._raw[key] = tmp
            raise

    def _field_value(self, field):
        key = self._field_names[field]
        if key in self._raw:
            return self._raw[key]
        else:
            return None

    def _add_contributors(self):
        if 'creators' in self._raw:
            for creator in self._raw['creators']:
                if 'firstName' in creator and 'lastName' in creator:
                    name = (creator['lastName'], creator['firstName'])
                    person = self.parent.get_person(name)
                    contrib = Contributor(self, person, name)
                    self.contributors.append(contrib)
                    person.contributions.add(contrib)
