import unittest
import peoplenames


class TestUnicodeFunctions(unittest.TestCase):
    def test_name_to_ascii(self):
        name = ('Ó Súilleabháin', 'Jörg Tanjō')
        rnme = peoplenames.name_to_ascii(name)
        tnme = ("O'Suilleabhain", 'Jorg Tanjo')
        self.assertEqual(rnme, tnme)


class TestListFunctions(unittest.TestCase):
    def test_break_name_unicode(self):
        name = ('(George) Ó Súilleabháin', 'Jörg-T.')
        rnme = peoplenames.break_name(name)
        tnme = [[('George', 'G'), ('Ó Súilleabháin', 'Ó')],
                [('Jörg', 'J'), ('T', 'T')]]
        self.assertEqual(rnme, tnme)

    def test_break_name_simple(self):
        name = ('Smith', 'Jane Kate')
        rnme = peoplenames.break_name(name)
        tnme = [[('Smith', 'S')],
                [('Jane', 'J'), ('Kate', 'K')]]
        self.assertEqual(rnme, tnme)

    def test_break_name_complex(self):
        name = ("O'Brian", 'James T.')
        rnme = peoplenames.break_name(name)
        tnme = [[("O'Brian", 'O')],
                [('James', 'J'), ('T', 'T')]]
        self.assertEqual(rnme, tnme)

    def test_part_comp(self):
        parts = [('Jane', 'J'), ('Kate', 'K')]
        tprts = [['Jane', 'Kate'], ['J', 'K']]
        for idx, tprt in enumerate(tprts):
            self.assertEqual(tprt, peoplenames.part_comp(parts, idx))

if __name__ == '__main__':
    unittest.main()
