import unittest
import peoplenames


class TestUnicodeFunctions(unittest.TestCase):
    def test_name_to_ascii(self):
        name = ('Ó Súilleabháin', 'Jörg Tanjō')
        rnme = peoplenames.name_to_ascii(name)
        tnme = ("O'Suilleabhain", 'Jorg Tanjo')
        self.assertEqual(rnme, tnme)


class TestListFunctions(unittest.TestCase):
    def test_break_name(self):
        names = [('(George) Ó Súilleabháin', 'Jörg-T.'),
                 ('Smith', 'Jane Kate'),
                 ("O'Brian", 'James T.')]

        tnmes = [[[('George', 'G'), ('Ó Súilleabháin', 'Ó')],
                  [('Jörg', 'J'), ('T', 'T')]],
                 [[('Smith', 'S')], [('Jane', 'J'), ('Kate', 'K')]],
                 [[("O'Brian", 'O')], [('James', 'J'), ('T', 'T')]]]
        for idx, name in enumerate(names):
            self.assertEqual(peoplenames.break_name(name), tnmes[idx])

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

    def test_inv_idx(self):
        self.assertEqual([0, 2, 3], peoplenames.inv_idx([1, 4], 5))


class TestNameComparisons(unittest.TestCase):
    def test_name_comp(self):
        namesets = [
            (2+1+1/4, ('Smith', 'Jane Kate'), ('Smith', 'Jane K.')),
            (1.75+1.75/2+1/4, ('Ó Súilleabháin', 'Jörg Tanjō'),
             ("O'Suilleabhain", 'Jorg T.'))]
        for ns in namesets:
            self.assertEqual(ns[0], peoplenames.name_comp(ns[1], ns[2]))

    def test_name_redundancy(self):
        redparts = [[('Jane', 'J'), ('Kate', 'K'), ('J', 'J'), ('K', 'K')],
                    [('Jane', 'J'), ('Kate', 'K'), ('J', 'J'), ('k', 'k')]]
        nonredparts = [[('Jane', 'J'), ('Kate', 'K')],
                       [('Jane', 'J'), ('Kate', 'K'), ('J', 'J')],
                       [('Jane', 'J'), ('Jill', 'J')]]
        for rp in redparts:
            self.assertTrue(peoplenames.name_redundancy(rp))
        for nrp in nonredparts:
            self.assertFalse(peoplenames.name_redundancy(nrp))

if __name__ == '__main__':
    unittest.main()
