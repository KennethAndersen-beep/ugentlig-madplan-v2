import unittest,copy,tempfile,json
from pathlib import Path
from integrated import build,run,validate
from decimal import Decimal

def fixture():
    items=[dict(ingredient=k,quality='synthetic',quantity=1000,unit='g',price_dkk=p,store=s) for k,p,s in [('chicken',49,'A'),('pork',40,'B'),('beef',65,'A'),('fish',70,'B'),('ris',15,'A')]]
    recipes=[dict(id=str(i),name='Testret '+str(i),protein=p,servings=2,ingredients=[(p,400,'g'),('ris',100,'g')]) for i,p in enumerate(['chicken']*3+['pork']*2+['beef']*2+['fish']*2)]
    return dict(environment='test',publish=False,synthetic=True,shopping_date='2026-11-28',items=items),recipes
class Integration(unittest.TestCase):
 def setUp(self): self.c,self.r=fixture()
 def test_seven_dates(self):
  b=build(self.c,self.r); self.assertEqual([d['date'] for d in b['days']],['2026-11-28','2026-11-29','2026-11-30','2026-12-01','2026-12-02','2026-12-03','2026-12-04'])
 def test_budget(self):
  b=build(self.c,self.r); self.assertEqual(b['purchase_cents'],21800); self.assertEqual(Decimal(b['consumed_cents'])+Decimal(b['leftover_value_cents']),21800)
 def test_family(self): self.assertGreater(build(self.c,self.r,adults=4)['purchase_cents'],build(self.c,self.r)['purchase_cents'])
 def test_unknown(self):
  self.c['items'][3].update(quality='E',price_dkk=None); self.assertIn('fish',build(self.c,self.r)['unknown'])
 def test_missing_essential_preserves(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'last.json'; run(p,self.c,self.r); old=p.read_bytes(); self.c['items'][-1].update(quality='E',price_dkk=None)
   with self.assertRaises(ValueError): run(p,self.c,self.r)
   self.assertEqual(p.read_bytes(),old)
 def test_invalid_price(self):
  self.c['items'][0]['price_dkk']=0
  with self.assertRaises(ValueError): build(self.c,self.r)
 def test_expired(self):
  self.c['synthetic']=False
  for x in self.c['items']: x.update(quality='B',source_url='https://example.com',price_type='offer',valid_from='2026-11-20',valid_to='2026-11-27')
  with self.assertRaisesRegex(ValueError,'outside'): build(self.c,self.r)
 def test_production_blocked(self):
  self.c['publish']=True
  with self.assertRaises(ValueError): build(self.c,self.r)
 def test_snapshot(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'last.json'; b=run(p,self.c,self.r); self.assertEqual(json.loads(p.read_text()),b)
 def test_tampering(self):
  b=build(self.c,self.r); b['purchase_cents']+=1
  with self.assertRaises(ValueError): validate(b)
if __name__=='__main__': unittest.main()
