from dateutil.parser import parser
import regex

re_has_ms = regex.compile('\d{1,2}:\d{1,2}:\d{1,2}\.\d+')


class BibDateParser(parser):
    """Extends parser class to allow for printing out partial dates"""

    def __init__(self, info=None):
        super().__init__(info=info)
        self.atts = ['year', 'month', 'day', 'hour', 'minute', 'second',
                     'microsecond']
        self.seps = ['', '-', '-', 'T', ':', ':', '.']
        self.fmts = ['{num:04d}', '{num:02d}', '{num:02d}', '{num:02d}',
                     '{num:02d}', '{num:02d}', '{num:06d}']

    def get_atts(self, timestr):
        if re_has_ms.search(timestr):
            return self.atts
        else:
            return self.atts[:-1]

    def parse_to_str(self, timestr, **kwargs):
        """Only returns string for datetime parts with a value"""
        res, skipped_tokens = self._parse(timestr, **kwargs)
        if res is None:
            raise ValueError("unknown string format")
            return None

        rtn = []

        for idx, att in enumerate(self.get_atts(timestr)):
            value = getattr(res, att)
            if value is None:
                return ''.join(rtn)
            rtn += [self.seps[idx], self.fmts[idx].format(num=value)]
        return ''.join(rtn)
