import unittest
from decimal import Decimal
from household_views import household_views
from test_recipe_pool import fixture

class HouseholdProfiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c,r=fixture()
        cls.out=household_views(c,r)
    def test_count(self):
        self.assertEqual(len(self.out['profiles']),16)
    def test_same_menu(self):
        ids=[x['id'] for x in self.out['profiles']['2-0']['view']['days']]
        for p in self.out['profiles'].values():
            self.assertTrue(p['available'])
            self.assertEqual([x['id'] for x in p['view']['days']],ids)
    def test_store_totals(self):
        for p in self.out['profiles'].values():
            v=p['view']
            self.assertEqual(sum(v['store_totals_cents'].values()),v['purchase_cents'])
    def test_pack_counts(self):
        for p in self.out['profiles'].values():
            for rows in p['view']['shopping'].values():
                for row in rows:
                    self.assertIs(type(row['packs']),int)
                    self.assertEqual(row['line_cents'],row['packs']*row['pack_cents'])
    def test_per_person(self):
        v=self.out['profiles']['2-1']['view']
        self.assertEqual(Decimal(v['purchase_per_person_day_cents']),Decimal(v['purchase_cents'])/21)
    def test_larger_household(self):
        self.assertGreater(self.out['profiles']['4-3']['view']['purchase_cents'],self.out['profiles']['2-0']['view']['purchase_cents'])
    def test_test_only(self):
        self.assertIs(self.out['publish'],False)
        self.assertIs(self.out['synthetic'],True)
    def test_invalid_range(self):
        c,r=fixture()
        with self.assertRaises(ValueError): household_views(c,r,adults_max=0)
