"""Test-only production orchestration with atomic last-good snapshot."""
import json, os, tempfile
from pathlib import Path
from datetime import datetime, timezone
from household_views import household_views
from reuse_overview import enrich_profiles

def atomic_json(path, payload):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:
            tmp=f.name
            json.dump(payload,f,ensure_ascii=False,allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if tmp and os.path.exists(tmp): os.unlink(tmp)

def run_cycle(catalog, recipes, snapshot, diagnostic, **options):
    snapshot=Path(snapshot); diagnostic=Path(diagnostic)
    if snapshot.resolve()==diagnostic.resolve(): raise ValueError('separate snapshot and diagnostics required')
    timestamp=datetime.now(timezone.utc).isoformat()
    try:
        if catalog.get('environment')!='test' or catalog.get('publish') is not False:
            raise ValueError('test only')
        bundle=enrich_profiles(household_views(catalog,recipes,**options))
        if not bundle['profiles'][bundle['default']]['available']:
            raise ValueError('default household unavailable')
        unavailable=[k for k,p in bundle['profiles'].items() if not p['available']]
        if unavailable: raise ValueError('incomplete household coverage')
        atomic_json(snapshot,bundle)
    except Exception as e:
        atomic_json(diagnostic,dict(timestamp=timestamp,status='failed',error_type=type(e).__name__,message=str(e),snapshot_exists=snapshot.exists(),publish=False))
        raise
    atomic_json(diagnostic,dict(timestamp=timestamp,status='success',profiles=len(bundle['profiles']),synthetic=bundle['synthetic'],publish=False))
    return bundle
