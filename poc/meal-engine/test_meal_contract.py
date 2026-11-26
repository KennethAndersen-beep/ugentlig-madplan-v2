import unittest,copy,json
from test_integrated import fixture
from meal_contract import build_view
class Contract(unittest.TestCase):
 def setUp(self):
  self.c,self.r=fixture(); self.c['schema_version']=1
  for r in self.r: r.update(short_recipe=['Tilbered testretten.'],detailed_recipe=['Forbered testdata.','Tilbered testretten.'])
 def test_schema(self): self.assertEqual(build_view(self.c,self.r)['schema_version'],1)
 def test_instructions(self):
  for d in build_view(self.c,self.r)['days']: self.assertEqual(len(d['detailed_recipe']),2)
 def test_portions(self): self.assertEqual(build_view(self.c,self.r,adults=3,children=1)['days'][0]['ingredients'][0]['quantity'],'700.0')
 def test_evidence(self):
  for rows in build_view(self.c,self.r)['shopping'].values():
   for row in rows: self.assertIn(row['price_evidence'],self.c['items'])
 def test_totals(self):
  b=build_view(self.c,self.r); self.assertEqual(sum(b['store_totals_cents'].values()),b['purchase_cents'])
 def test_missing_recipe(self):
  del self.r[0]['detailed_recipe']
  with self.assertRaises(ValueError): build_view(self.c,self.r)
 def test_version(self):
  self.c['schema_version']=2
  with self.assertRaises(ValueError): build_view(self.c,self.r)
 def test_ambiguity(self):
  self.c['items'].append(copy.deepcopy(self.c['items'][-1]))
  with self.assertRaisesRegex(ValueError,'ambiguous'): build_view(self.c,self.r)
 def test_serializable(self):
  b=build_view(self.c,self.r); self.assertEqual(json.loads(json.dumps(b)),b)
