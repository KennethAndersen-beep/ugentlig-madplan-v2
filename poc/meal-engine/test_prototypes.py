import unittest, tempfile, json
from pathlib import Path
from optimizer import Pack,optimize
from fallback import publish
class Test(unittest.TestCase):
    def setUp(self):
        self.p=[Pack('kylling','A',450,2900),Pack('kylling','B',1000,4900),Pack('ris','A',1000,1500),Pack('ris','B',1000,1800)]
    def test_shared_pack(self): self.assertEqual(optimize({'kylling':800},self.p)['purchase_cents'],4900)
    def test_remainder(self): self.assertEqual(optimize({'kylling':800},self.p)['remainder'],{'kylling':200})
    def test_two_stores(self): self.assertEqual(optimize({'kylling':800,'ris':400},self.p)['purchase_cents'],6400)
    def test_one_store(self): self.assertEqual(optimize({'kylling':800,'ris':400},self.p,max_stores=1)['purchase_cents'],6700)
    def test_visit_cost(self): self.assertEqual(optimize({'kylling':800,'ris':400},self.p,visit_cents=500)['stores'],['B'])
    def test_limit(self): self.assertEqual(optimize({'x':1000},[Pack('x','A',500,100,1),Pack('x','B',500,200)])['purchase_cents'],300)
    def test_missing(self):
        with self.assertRaises(ValueError): optimize({'unknown':100},self.p)
    def test_zero_price(self):
        with self.assertRaises(ValueError): optimize({'x':1},[Pack('x','A',1,0)])
    def test_invalid_size(self):
        with self.assertRaises(ValueError): optimize({'x':1},[Pack('x','A',0,1)])
    def test_empty(self): self.assertEqual(optimize({},self.p)['purchase_cents'],0)
    def test_negative_need(self):
        with self.assertRaises(ValueError): optimize({'x':-1},self.p)
    def test_inadequate_limit(self):
        with self.assertRaises(ValueError): optimize({'x':3},[Pack('x','A',1,1,2)])
    def test_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'live.json';p.write_text('{"version":1}')
            def reject(x): raise ValueError('invalid')
            with self.assertRaises(ValueError): publish(p,{'version':2},reject)
            self.assertEqual(p.read_text(),'{"version":1}')
    def test_success(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'live.json';p.write_text('{"version":1}')
            publish(p,{'version':2},lambda x:None)
            self.assertEqual(json.loads(p.read_text()),{'version':2})
    def test_serialization_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'live.json';p.write_text('{"version":1}')
            with self.assertRaises(ValueError): publish(p,{'price':float('nan')},lambda x:None)
            self.assertEqual(p.read_text(),'{"version":1}');self.assertEqual(len(list(Path(d).iterdir())),1)
if __name__=='__main__': unittest.main(verbosity=2)
