"""Versioned presentation adapter for the isolated meal engine."""
from copy import deepcopy
from decimal import Decimal
from integrated import build
from meal_budget import UNITS

def build_view(catalog, recipes, adults=2, children=0, **options):
    if catalog.get('schema_version') != 1:
        raise ValueError('unsupported catalog schema')
    for r in recipes:
        for key in ('short_recipe','detailed_recipe'):
            if not isinstance(r.get(key),list) or not r[key] or any(not isinstance(s,str) or not s.strip() for s in r[key]):
                raise ValueError('missing recipe instructions: '+key)
    out=build(catalog,recipes,adults,children,**options)
    out['schema_version']=1
    out['child_factor']=str(options.get('child_factor','0.5'))
    portions=Decimal(adults)+Decimal(children)*Decimal(out['child_factor'])
    by_id={r['id']:r for r in recipes}
    for d in out['days']:
        r=by_id[d['id']]
        d['short_recipe']=deepcopy(r['short_recipe'])
        d['detailed_recipe']=deepcopy(r['detailed_recipe'])
        d['ingredients']=[dict(ingredient=k,quantity=str(Decimal(str(q))*portions/Decimal(str(r['servings']))),unit=u) for k,q,u in r['ingredients']]
        d['image']=r.get('image')
    for store,rows in out['shopping'].items():
        for row in rows:
            matches=[x for x in catalog['items'] if x['quality']!='E' and x['ingredient']==row['ingredient'] and x['store']==store and x['unit']==row['unit'] and x['quantity']==row['pack_quantity'] and Decimal(str(x['price_dkk']))*100==row['pack_cents']]
            if len(matches)!=1:
                raise ValueError('ambiguous price provenance')
            row['price_evidence']=deepcopy(matches[0])
    out['store_totals_cents']={s:sum(x['line_cents'] for x in rows) for s,rows in out['shopping'].items()}
    return out
