from pyzotero import zotero
from references import References, Item, Contributor
import exceptions as bexc
import regex


class ZoteroRefs(References):
    """Zotero based References"""
    name = "Zotero"

    args = {'library_id': str, 'api_key': str}

    def __init__(self, *cargs, **kwargs):
        super().__init__(*cargs, **kwargs)
        library_id = kwargs.get('library_id', None)
        api_key = kwargs.get('api_key', None)
        try:
            self.dbc = zotero.Zotero(library_id, 'user', api_key)
        except Exception as exc:
            raise bexc.RefConnectError(
                'Could not connect to zotero').with_traceback(
                exc.__traceback__)

    def get_all(self):
        try:
            items_raw = self.dbc.everything(self.dbc.top())
        except Exception as exc:
            raise bexc.RefGetError(
                'Could not retrieve all items').with_traceback(
                exc.__traceback__)
        else:
            for item_raw in items_raw:
                self.items.append(ZoteroItem(self, raw=item_raw))


class ZoteroItem(Item):
    """Extention to Item class for Zotero connectivity"""
    name = "ZoteroItem"

    _field_names = {
        'title': 'title',
        'title_short': 'shortTitle',
        'url': 'url',
        'journal': 'publicationTitle',
        'journal_abbrev': 'journalAbbreviation',
        'date': 'date'
    }

    reBCN = regex.compile(r'bibcleannames\[([^\]]+)\]')
    reECN = regex.compile(r'bibcleannames\[\]')
    reGCN = regex.compile(r'([^,]+),([^=]+)=([^,]+),([^;]+);?')

    def __init__(self, parent, *cargs, **kwargs):
        self._raw = kwargs.get('raw', None)
        super().__init__(parent, *cargs, **kwargs)

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
            raise bexc.RefUpdateError('Update not properly formatted')
            return False

    def _update_clean_names(self):
        bibcleannames = []
        for contrib in self.contributors:
            if contrib.name != contrib.citename:
                bibcleannames.append(
                    '='.join(
                        [
                            ','.join(contrib.citename),
                            ','.join(contrib.name)
                        ]
                    )
                )
        clean_name_entry = ''.join([
            'bibcleannames[',
            ';'.join(bibcleannames),
            ']'
        ])
        if 'extra' not in self._raw:
            if len(bibcleannames) > 0:
                self._raw['extra'] = clean_name_entry
        elif self.reBCN.search(self._raw['extra']):
            if len(bibcleannames) > 0:
                self._raw['extra'] = self.reECN.sub(
                    '',
                    self.reECN.sub(
                        clean_name_entry,
                        self.reBCN.sub(
                            'bibcleannames[]',
                            self._raw['extra']
                        ),
                        1
                    )
                )
            else:
                self._raw['extra'] = self.reBCN.sub('', self._raw['extra'])
        elif len(bibcleannames) > 0:
            self._raw['extra'] = '\n'.join([
                self._raw['extra'], clean_name_entry, ''])

    def update_contributor(self, idx, name, change_citename=None):
        if 'creators' in self._raw:
            old_extra = self._raw.get('extra', None)
            self._update_clean_names()
            if self.change_citename or change_citename:
                old_creator = self._raw['creators'][idx]
                self._raw['creators'][idx]['lastName'] = name[0]
                self._raw['creators'][idx]['firstName'] = name[1]
            try:
                self.update()
            except Exception:
                self._raw['creators'][idx] = old_creator
                if 'extra' in self._raw or old_extra is not None:
                    self._raw['extra'] = old_extra
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
        clean_names = {}
        if 'extra' in self._raw:
            bcns_sets = self.reBCN.findall(self._raw['extra'])
            for bcns_set in bcns_sets:
                bcns = self.reGCN.findall(bcns_set)
                for bcn in bcns:
                    clean_names[bcn[0]] = bcn[1]
        if 'creators' in self._raw:
            for creator in self._raw['creators']:
                if 'firstName' in creator and 'lastName' in creator:
                    citename = (creator['lastName'], creator['firstName'])
                    name = None
                    person = None
                    if citename in clean_names:
                        name = clean_names[citename]
                        person = self.parent.get_person(name)
                    else:
                        person = self.parent.get_person(citename)
                    contrib = Contributor(self, person, citename, name=name)
                    self.contributors.append(contrib)
                    person.contributions.add(contrib)
