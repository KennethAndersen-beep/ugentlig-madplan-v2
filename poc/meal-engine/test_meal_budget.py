import unittest
from decimal import Decimal
from optimizer import Pack
from meal_budget import budget
class TestBudget(unittest.TestCase):
    def setUp(self):
        self.p=[Pack('kylling','A',450,2900),Pack('kylling','B',1000,4900),Pack('ris','A',1000,1500)]
        self.units={'kylling':'g','ris':'g'}
        self.r=[{'servings':2,'ingredients':[('kylling',.4,'kg'),('ris',200,'g')]},{'servings':2,'ingredients':[('kylling',400,'g'),('ris',.2,'kg')]}]
    def runbudget(self,**kw): return budget(self.r,self.p,self.units,**kw)
    def test_aggregate(self): self.assertEqual(self.runbudget()['exact_needs'],{'kylling':800,'ris':400})
    def test_purchase(self): self.assertEqual(self.runbudget()['purchase_cents'],6400)
    def test_consumption(self): self.assertEqual(self.runbudget()['consumed_cents'],Decimal(4520))
    def test_leftover(self): self.assertEqual(self.runbudget()['leftover_value_cents'],Decimal(1880))
    def test_daily(self): self.assertEqual(self.runbudget()['daily_consumed_cents'],[2260,2260])
    def test_child(self): self.assertEqual(self.runbudget(children=2)['exact_needs']['kylling'],1200)
    def test_one_adult(self): self.assertEqual(self.runbudget(adults=1)['exact_needs']['ris'],200)
    def test_empty_household(self):
        with self.assertRaises(ValueError): self.runbudget(adults=0)
    def test_incompatible(self):
        with self.assertRaises(ValueError): budget(self.r,self.p,{'kylling':'ml','ris':'g'})
    def test_fractional(self):
        r=budget([{'servings':3,'ingredients':[('ris',1,'g')]}],self.p,self.units,adults=1)
        self.assertEqual(r['remainder']['ris'],999)
        self.assertEqual(r['exact_needs']['ris'],Decimal(1)/3)
    def test_missing_price(self):
        with self.assertRaises(ValueError): budget(self.r,[],self.units)
    def test_bad_factor(self):
        with self.assertRaises(ValueError): self.runbudget(child_factor=2)
    def test_volume(self):
        r=budget([{'servings':2,'ingredients':[('fløde',2,'dl'),('fløde',.1,'l')]}],[Pack('fløde','A',500,2000)],{'fløde':'ml'})
        self.assertEqual(r['exact_needs']['fløde'],300)
        self.assertEqual(r['consumed_cents'],1200)
if __name__=='__main__': unittest.main()
