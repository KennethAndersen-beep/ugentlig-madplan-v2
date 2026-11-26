"""Exact ingredient balance and reuse overview; no shelf-life assumptions."""
from collections import defaultdict
from decimal import Decimal
from meal_budget import UNITS

def reuse_overview(view):
    bought=defaultdict(int); costs=defaultdict(int); units={}; uses=defaultdict(lambda: defaultdict(Decimal))
    for rows in view['shopping'].values():
        for row in rows:
            k=row['ingredient']; u=row['unit']
            if k in units and units[k]!=u: raise ValueError('inconsistent purchase unit')
            units[k]=u
            bought[k]+=row['pack_quantity']*row['packs']
            costs[k]+=row['line_cents']
    for day in view['days']:
        for item in day['ingredients']:
            k=item['ingredient']; u,mult=UNITS[item['unit']]
            q=Decimal(str(item['quantity']))*mult
            if not q.is_finite() or q<0: raise ValueError('invalid consumption')
            if q==0: continue
            if units.get(k)!=u: raise ValueError('missing or incompatible purchase')
            uses[k][day['date']]+=q
    rows=[]
    for k in sorted(bought):
        q=Decimal(bought[k]); used=sum(uses[k].values(),Decimal(0)); rest=q-used
        if q<=0 or rest<0: raise ValueError('insufficient purchase')
        value=Decimal(costs[k])*rest/q
        rows.append(dict(ingredient=k,unit=units[k],purchased=str(q),used=str(used),remaining=str(rest),remaining_value_cents=str(value),use_days=[dict(date=d,quantity=str(n)) for d,n in sorted(uses[k].items())],reused_across_days=len(uses[k])>1,storage_status='not_verified'))
    total=sum((Decimal(r['remaining_value_cents']) for r in rows),Decimal(0))
    if abs(total-Decimal(view['leftover_value_cents']))>Decimal('0.000001'): raise ValueError('remaining value reconciliation')
    return dict(ingredients=rows,remaining_value_cents=str(total),storage_status='not_verified',note='Restmængder er ikke nødvendigvis madspild. Følg produktets mærkning og opbevaringsanvisninger.')

def enrich_profiles(bundle):
    for profile in bundle['profiles'].values():
        if profile['available']:
            v=profile['view']; v['reuse']=reuse_overview(v)
    return bundle
