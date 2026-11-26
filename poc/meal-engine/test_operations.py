import unittest,tempfile,json
from pathlib import Path
from test_recipe_pool import fixture
from operations import run_cycle

class Operations(unittest.TestCase):
    def test_cycle_and_failure(self):
        c,r=fixture()
        with tempfile.TemporaryDirectory() as d:
            s=Path(d)/'last.json'; log=Path(d)/'diagnostic.json'
            b=run_cycle(c,r,s,log)
            self.assertEqual(json.loads(s.read_text()),b)
            self.assertEqual(json.loads(log.read_text())['status'],'success')
            previous=s.read_bytes()
            c['publish']=True
            with self.assertRaises(ValueError): run_cycle(c,r,s,log)
            self.assertEqual(s.read_bytes(),previous)
            self.assertEqual(json.loads(log.read_text())['status'],'failed')
    def test_first_failure(self):
        c,r=fixture(); c['publish']=True
        with tempfile.TemporaryDirectory() as d:
            s=Path(d)/'last.json'; log=Path(d)/'diagnostic.json'
            with self.assertRaises(ValueError): run_cycle(c,r,s,log)
            self.assertFalse(s.exists())
            self.assertFalse(json.loads(log.read_text())['snapshot_exists'])
    def test_same_path(self):
        c,r=fixture()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'last.json'
            with self.assertRaises(ValueError): run_cycle(c,r,p,p)
            self.assertFalse(p.exists())
