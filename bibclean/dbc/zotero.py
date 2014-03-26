from pyzotero import zotero
from References import References, Item, Contributor
import exceptions as bexc


class ZoteroRefs(References):
    """Zotero based References"""
    name = "ZoteroRefs"

    def __init__(self, *cargs, **kwargs):
        super().__init__(*cargs, **kwargs)
        library_id = kwargs.get('library_id', None)
        api_key = kwargs.get('api_key', None)
        self.dbc = zotero.Zotero(library_id, 'user', api_key)

    def get_all(self):
        try:
            items_raw = self.dbc.everything(self.dbc.top())
        except Exception as exc:
            raise bexc.RefGetError(
                'Could not retrieve all items').with_traceback(
                exc.__traceback__)
        for item_raw in items_raw:
            self.items.append(ZoteroItem(self, raw=item_raw))


class ZoteroItem(Item):
    """Extention to Item class for Zotero connectivity"""
    name = "ZoteroItem"

    def __init__(self, parent, *cargs, **kwargs):
        super().__init__(parent, *cargs, **kwargs)
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
            except Exception as exc:
                raise bexc.RefUpdateError(
                    'Error when updating').with_traceback(exc.__traceback_)
        else:
            raise bexc.RefUpdateError('Update not properly formated')
            return False

    def update_contributor(self, idx, name):
        if 'creators' in self._raw:
            old_creator = self._raw['creators'][idx]
            self._raw['creators'][idx]['lastName'] = name[0]
            self._raw['creators'][idx]['firstName'] = name[1]
            try:
                self.update()
            except Exception:
                self._raw['creators'][idx] = old_creator
                raise

    def _update_field(self, field, value):
        if field in self._field_names:
            key = self._field_names[field]
            has_key = key in self._raw
            tmp = None
            if has_key:
                tmp = self._raw[key] = value
            self._raw[key] = value
            try:
                self.update()
            except:
                if has_key:
                    self._raw[key] = tmp
                else:
                    del(self._raw[key])
                raise
        else:
            raise bexc.RefNoFieldDefined(''.join([str(field),
                                                  ' is not defined']))

    def _field_value(self, field):
        if field in self._field_names:
            key = self._field_names[field]
            if key in self._raw:
                return self._raw[key]
            else:
                return None
        else:
            raise bexc.RefNoFieldDefined(''.join([str(field),
                                                  ' is not defined']))
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
