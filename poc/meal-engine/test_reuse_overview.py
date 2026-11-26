import unittest
from decimal import Decimal
from copy import deepcopy
from reuse_overview import reuse_overview,enrich_profiles
from household_views import household_views
from test_recipe_pool import fixture

class Reuse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c,r=fixture()
        cls.bundle=enrich_profiles(household_views(c,r))
        cls.view=cls.bundle['profiles']['2-0']['view']
    def test_balances(self):
        for p in self.bundle['profiles'].values():
            if not p['available']: continue
            for r in p['view']['reuse']['ingredients']:
                self.assertEqual(Decimal(r['purchased']),Decimal(r['used'])+Decimal(r['remaining']))
                self.assertGreaterEqual(Decimal(r['remaining']),0)
    def test_values(self):
        for p in self.bundle['profiles'].values():
            if p['available']:
                v=p['view']
                self.assertLess(abs(Decimal(v['reuse']['remaining_value_cents'])-Decimal(v['leftover_value_cents'])),Decimal('0.000001'))
    def test_daily_uses(self):
        for r in self.view['reuse']['ingredients']:
            self.assertEqual(sum((Decimal(d['quantity']) for d in r['use_days']),Decimal(0)),Decimal(r['used']))
    def test_shared_ingredients(self):
        self.assertTrue(any(r['reused_across_days'] for r in self.view['reuse']['ingredients']))
    def test_storage_unknown(self):
        self.assertEqual(self.view['reuse']['storage_status'],'not_verified')
    def test_tampered_consumption(self):
        v=deepcopy(self.view)
        v['days'][0]['ingredients'][0]['quantity']='99999999'
        with self.assertRaises(ValueError): reuse_overview(v)
    def test_tampered_value(self):
        v=deepcopy(self.view); v['leftover_value_cents']='-1'
        with self.assertRaises(ValueError): reuse_overview(v)
