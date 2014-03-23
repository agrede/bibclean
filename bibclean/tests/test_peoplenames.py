import unittest
import peoplenames


class TestRecursiveFunctions(unittest.TestCase):
    def test_rec_apply(self):
        testsets = [
            (
                {'A': 7, 'B': 13},
                lambda x: x+2,
                {'A': 5, 'B': 11}
            ),
            (
                (7, 13),
                lambda x: x+2,
                (5, 11)
            ),
            (
                [7, 13],
                lambda x: x+2,
                [5, 11]
            ),
            (
                {0},
                lambda x: x*0,
                {3, 5}
            ),
            (
                {'A': [7, 13], 'B': [(7, 13), (19, 31)]},
                lambda x: x+2,
                {'A': [5, 11], 'B': [(5, 11), (17, 29)]}
            )
        ]
        for ts in testsets:
            self.assertEqual(ts[0], peoplenames.rec_apply(ts[1], ts[2]),
                             msg=str(ts[0]))


class TestUnicodeFunctions(unittest.TestCase):
    def test_single_name_to_ascii(self):
        self.assertEqual("O'Suilleabhain",
                         peoplenames.single_name_to_ascii('Ó Súilleabháin'))

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
            self.assertEqual(peoplenames.break_name(name), tnmes[idx],
                             msg=str(name))

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
            self.assertEqual(tprt, peoplenames.part_comp(parts, idx),
                             msg=str(tprt))

    def test_inv_idx(self):
        self.assertEqual([0, 2, 3], peoplenames.inv_idx([1, 4], 5))


class TestNameComparisonFunctions(unittest.TestCase):
    def test_name_comp(self):
        namesets = [
            (2+1+1/4, ('Smith', 'Jane Kate'), ('Smith', 'Jane K.')),
            (1.75+1.75/2+1/4, ('Ó Súilleabháin', 'Jörg Tanjō'),
             ("O'Suilleabhain", 'Jorg T.'))]
        for ns in namesets:
            self.assertEqual(ns[0], peoplenames.name_comp(ns[1], ns[2]),
                             msg=str(ns))

    def test_fullest_name(self):
        namesets = [
            (
                ('Ó Súilleabháin', 'Jörg Tanjō'),
                ('Ó Súilleabháin', 'Jörg Tanjō'),
                ("O'Suilleabhain", 'Jorg Tanjo')
            ),
            (
                ('Ó Súilleabháin', 'Jorg Tanjo'),
                ('Ó Súilleabháin', 'J.T.'),
                ("O'Suilleabhain", 'Jorg Tanjo')
            ),
            (
                ('Ó Súilleabháin', 'Jorg Tanjo'),
                ('Ó Súilleabháin', 'Jörg Tanjō J.T.'),
                ("O'Suilleabhain", 'Jorg Tanjo')
            ),
            (
                ('Doe', 'Josh B.'),
                ('Doe', 'Josh'),
                ('Doe', 'J.B.')
            )
        ]
        for ns in namesets:
            self.assertEqual(ns[0], peoplenames.fullest_name(ns[1], ns[2]),
                             msg=str(ns[0]))

    def test_name_part_in_parts(self):
        testsets = [
            (1, ('Tanjō', 'T'), [('Jörg', 'J'), ('Tanjō', 'T')]),
            (0, ('Jörg', 'J'), [('Jorg', 'J'), ('Tanjo', 'T')]),
            (1, ('Ἑρμιόνη', 'Ἑ'), [('Φοίβη', 'Φ'), ('Ἑ', 'Ἑ')]),
            (0, ('Φοίβη', 'Φ'), [('P', 'P'), ('Ἑ', 'Ἑ')])
        ]
        for ts in testsets:
            self.assertEqual(ts[0],
                             peoplenames.name_part_in_parts(ts[1], ts[2]),
                             msg=str(ts[1]))


class TestNameRedundancyFunctions(unittest.TestCase):
    def test_name_repeat_block_length(self):
        testsets = [
            (2, [('Jane', 'J'), ('Kate', 'K'), ('J', 'J'), ('K', 'K')]),
            (2, [('Jane', 'J'), ('Kate', 'K'), ('J', 'J'), ('k', 'k')]),
            (2, [('Jane', 'J'), ('Kate', 'K')]),
            (3, [('Jane', 'J'), ('Kate', 'K'), ('J', 'J')]),
            (2, [('Jane', 'J'), ('Jill', 'J')])
        ]
        for ts in testsets:
            self.assertEqual(ts[0],
                             peoplenames.name_repeat_block_length(ts[1]),
                             msg=str(ts[1]))

    def test_name_redundancy(self):
        self.assertTrue(
            peoplenames.name_redundancy(
                [('Jane', 'J'), ('Kate', 'K'), ('J', 'J'), ('K', 'K')]))
        self.assertFalse(peoplenames.name_redundancy(
            [('Jane', 'J'), ('Kate', 'K')]))

    def test_name_remove_redundancy(self):
        testsets = [
            (
                [('Jane', 'J'), ('Kate', 'K')],
                [('Jane', 'J'), ('Kate', 'K'), ('J', 'J'), ('K', 'K')]
            ),
            (
                [('Jane', 'J')],
                [('J', 'J'), ('Jane', 'J')]
            )
        ]
        for ts in testsets:
            self.assertEqual(ts[0], peoplenames.remove_redundancies(ts[1]),
                             msg=str(ts[0]))


if __name__ == '__main__':
    unittest.main()
