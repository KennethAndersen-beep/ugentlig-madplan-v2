"""Isolated end-to-end prototype. No production publication."""
from datetime import date,timedelta
from decimal import Decimal
from collections import defaultdict
from optimizer import Pack
from menu_optimizer import select_menu
from fallback import publish

def build(catalog, recipes, adults=2, children=0, **options):
    start=date.fromisoformat(catalog['shopping_date'])
    if start.weekday()!=5: raise ValueError('Saturday start required')
    if catalog.get('environment')!='test' or catalog.get('publish') is not False: raise ValueError('test only')
    packs=[]; units={}; unknown=[]
    for x in catalog['items']:
        name=x['ingredient']; q=x['quality']
        if q=='E':
            if x['price_dkk'] is not None: raise ValueError('unknown price must be null')
            unknown.append(name); continue
        if q not in ('A','B','C','D','synthetic'): raise ValueError('quality')
        if (q=='synthetic') != (catalog.get('synthetic') is True): raise ValueError('synthetic flag mismatch')
        if q in ('A','B','C'):
            if not x.get('source_url','').startswith('https://'): raise ValueError('source required')
            if x.get('price_type')=='offer' and not date.fromisoformat(x['valid_from'])<=start<=date.fromisoformat(x['valid_to']): raise ValueError('offer outside shopping date')
        if q=='D' and not x.get('estimate_reason'): raise ValueError('estimate reason required')
        unit=x['unit']; qty=x['quantity']; cents=Decimal(str(x['price_dkk']))*100
        if unit not in ('g','ml','stk') or type(qty) is not int or qty<=0 or not cents.is_finite() or cents<=0 or cents!=cents.to_integral_value(): raise ValueError('invalid pack')
        if name in units and units[name]!=unit: raise ValueError('inconsistent unit')
        units[name]=unit
        packs.append(Pack(name,x['store'],qty,int(cents),x.get('limit')))
    # Unpriced ingredients are ineligible, not silently assigned zero.
    eligible=[r for r in recipes if all(k in units for k,_,_ in r['ingredients'])]
    result=select_menu(eligible,packs,units,adults=adults,children=children,**options)
    b=result['budget']; daily=[]
    for i,(r,c) in enumerate(zip(result['recipes'],b['daily_consumed_cents'])):
        daily.append(dict(date=str(start+timedelta(days=i)),id=r['id'],name=r['name'],protein=r['protein'],consumed_cents=str(c)))
    shopping=defaultdict(list)
    for p,n in b['basket']:
        shopping[p.store].append(dict(ingredient=p.ingredient,unit=units[p.ingredient],pack_quantity=p.quantity,packs=n,pack_cents=p.cents,line_cents=p.cents*n))
    out=dict(environment='test',publish=False,synthetic=catalog.get('synthetic') is True,shopping_date=str(start),adults=adults,children=children,days=daily,shopping=dict(shopping),purchase_cents=b['purchase_cents'],total_cents=b['total_cents'],consumed_cents=str(b['consumed_cents']),leftover_value_cents=str(b['leftover_value_cents']),remainder=b['remainder'],unknown=unknown,evaluated=result['evaluated'])
    validate(out); return out

def validate(p):
    if p['environment']!='test' or p['publish'] is not False: raise ValueError('test only')
    if len(p['days'])!=7 or len({d['id'] for d in p['days']})!=7: raise ValueError('seven distinct meals required')
    if sum(d['protein']=='fish' for d in p['days'])>1 or any(d['protein']=='vegetarian' for d in p['days']): raise ValueError('menu constraints')
    if sum(x['line_cents'] for rows in p['shopping'].values() for x in rows)!=p['purchase_cents']: raise ValueError('basket reconciliation')
    if abs(Decimal(p['consumed_cents'])+Decimal(p['leftover_value_cents'])-p['purchase_cents'])>Decimal('0.000001'): raise ValueError('budget reconciliation')
    if abs(sum(Decimal(d['consumed_cents']) for d in p['days'])-Decimal(p['consumed_cents']))>Decimal('0.000001'): raise ValueError('daily reconciliation')

def run(path,catalog,recipes,**options):
    candidate=build(catalog,recipes,**options)
    publish(path,candidate,validate)
    return candidate
