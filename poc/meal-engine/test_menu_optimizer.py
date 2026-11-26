import unittest
from menu_optimizer import select_menu
from optimizer import Pack
from itertools import combinations
from meal_budget import budget

def recipe(i,p,qty=400): return dict(id=str(i),protein=p,servings=2,ingredients=[(p,qty,'g')])
R=[recipe(i,p) for i,p in enumerate(['chicken','chicken','chicken','pork','pork','beef','beef','fish','fish','vegetarian'])]
U={p:'g' for p in ['chicken','pork','beef','fish','vegetarian']}
P=[Pack(p,'A',1000,c) for p,c in [('chicken',4900),('pork',4000),('beef',6500),('fish',7000),('vegetarian',100)]]
class Tests(unittest.TestCase):
 def runmenu(self,**kw): return select_menu(R,P,U,**kw)
 def test_seven(self): self.assertEqual(len(self.runmenu()['recipes']),7)
 def test_no_vegetarian(self): self.assertNotIn('vegetarian',[r['protein'] for r in self.runmenu()['recipes']])
 def test_fish_limit(self): self.assertLessEqual(sum(r['protein']=='fish' for r in self.runmenu()['recipes']),1)
 def test_no_fish(self): self.assertNotIn('fish',[r['protein'] for r in self.runmenu(max_fish=0)['recipes']])
 def test_variety(self): self.assertGreaterEqual(len({r['protein'] for r in self.runmenu()['recipes']}),3)
 def test_max_protein(self): self.assertTrue(all(sum(r['protein']==p for r in self.runmenu()['recipes'])<=3 for p in U))
 def test_duplicate(self):
  with self.assertRaisesRegex(ValueError,'duplicate'): select_menu(R+[R[0]],P,U)
 def test_limit(self):
  with self.assertRaisesRegex(ValueError,'candidate limit'): self.runmenu(max_candidates=1)
 def test_missing_prices(self):
  with self.assertRaisesRegex(ValueError,'no feasible'): select_menu(R,[P[0]],U)
 def test_cost(self):
  candidates=[budget(s,P,U)['total_cents'] for s in combinations(R[:9],7) if sum(r['protein']=='fish' for r in s)<=1]
  self.assertEqual(self.runmenu()['budget']['total_cents'],min(candidates))
 def test_household(self): self.assertGreater(self.runmenu(adults=4)['budget']['purchase_cents'],self.runmenu()['budget']['purchase_cents'])
 def test_reconcile(self):
  b=self.runmenu()['budget']; self.assertEqual(b['consumed_cents']+b['leftover_value_cents'],b['purchase_cents'])
if __name__=='__main__': unittest.main()
