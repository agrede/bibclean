import unittest
import bibdates


class TestParser(unittest.TestCase):
    def test_parse_to_str(self):
        parser = bibdates.BibDateParser()
        testsets = [
            ('2010-01-03T23:20:10.000001', 'Jan. 3, 2010 11:20:10.000001pm'),
            ('2001-02-27T08:03:02', 'February 27, 2001 8:03:02am'),
            ('1985-11-06', '6 Nov. 1985'),
            ('1920-06', 'June 1920'),
            ('2000', '2000')
        ]
        for ts in testsets:
            self.assertEqual(ts[0], parser.parse_to_str(ts[0]), msg=ts[0])
            self.assertEqual(ts[0], parser.parse_to_str(ts[1]), msg=ts[1])


if __name__ == '__main__':
    unittest.main()
