import unittest
import references as r


class TestReferences(unittest.TestCase):
    def test_get_person(self):
        refs = r.References()
        name = ('Doe', 'John')
        self.assertEqual(0, len(refs.people))
        pers = refs.get_person(name)
        self.assertEqual(1, len(refs.people))
        self.assertEqual(name, pers.name)

    def test_remove_person_if_empty(self):
        refs = r.References()
        name = ('Doe', 'John')
        self.assertEqual(0, len(refs.people))
        refs.get_person(name)
        self.assertEqual(1, len(refs.people))
        self.assertTrue(refs.remove_person_if_empty(name))
        self.assertEqual(0, len(refs.people),
                         msg=', '.join(list(refs.people.keys())))


if __name__ == '__main__':
    unittest.main()
