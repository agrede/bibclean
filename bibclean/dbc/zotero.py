from pyzotero import zotero
from references import References, Item, People, Person


class ZoteroRefs(References):
    """
    Ref
    """
    def get_all(self):
        self._dbc
