import json, unittest
from pathlib import Path
from decimal import Decimal
from meal_contract import build_view

def fixture():
    doc=json.loads(Path(__file__).with_name('recipes-demo.json').read_text(encoding='utf-8'))
    recipes=doc['recipes']
    units={}
    for r in recipes:
        for k,n,u in r['ingredients']:
            if k in units and units[k]!=u: raise ValueError('inconsistent unit')
            units[k]=u
    # Explicitly synthetic pack sizes and prices. Not shopping advice.
    items=[dict(ingredient=k,quality='synthetic',quantity={'g':500,'ml':500,'stk':5}[u],unit=u,price_dkk=20,store='Testbutik') for k,u in units.items()]
    return dict(schema_version=1,environment='test',publish=False,synthetic=True,shopping_date='2026-11-28',items=items),recipes

class RealisticRecipePool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c,cls.r=fixture()
        cls.view=build_view(cls.c,cls.r)
    def test_pool(self):
        self.assertEqual(len(self.r),8)
        self.assertEqual(len({r['id'] for r in self.r}),8)
        for r in self.r:
            self.assertEqual(r['servings'],2)
            self.assertGreater(r['minutes'],0)
            self.assertTrue(r['short_recipe'])
            self.assertGreaterEqual(len(r['detailed_recipe']),3)
            self.assertTrue(all(n>0 and u in ('g','ml','stk') for k,n,u in r['ingredients']))
    def test_menu(self):
        days=self.view['days']
        self.assertEqual(len(days),7)
        self.assertLessEqual(sum(d['protein']=='fish' for d in days),1)
        self.assertFalse(any(d['protein']=='vegetarian' for d in days))
    def test_details(self):
        for d in self.view['days']:
            self.assertTrue(d['ingredients'] and d['short_recipe'] and d['detailed_recipe'])
    def test_budget(self):
        self.assertEqual(sum(self.view['store_totals_cents'].values()),self.view['purchase_cents'])
        self.assertLess(abs(Decimal(self.view['consumed_cents'])+Decimal(self.view['leftover_value_cents'])-self.view['purchase_cents']),Decimal('0.000001'))
    def test_household(self):
        larger=build_view(self.c,self.r,adults=4)
        self.assertGreater(larger['purchase_cents'],self.view['purchase_cents'])
    def test_synthetic_and_no_publication(self):
        self.assertIs(self.view['synthetic'],True)
        self.assertIs(self.view['publish'],False)
