"""Precalculate a bounded set of household budgets for a static website."""
from meal_contract import build_view
from decimal import Decimal

def household_views(catalog, recipes, adults_max=4, children_max=3, **options):
    if type(adults_max) is not int or type(children_max) is not int or not 1<=adults_max<=6 or not 0<=children_max<=6:
        raise ValueError('invalid household range')
    if 'child_factor' in options and not 0<Decimal(str(options['child_factor']))<=1:
        raise ValueError('invalid child factor')
    base=build_view(catalog,recipes,adults=2,children=0,**options)
    selected={d['id'] for d in base['days']}
    fixed=[r for r in recipes if r['id'] in selected]
    profiles={}
    for a in range(1,adults_max+1):
        for c in range(children_max+1):
            key=f'{a}-{c}'
            try:
                v=build_view(catalog,fixed,adults=a,children=c,**options)
                if [d['id'] for d in v['days']] != [d['id'] for d in base['days']]:
                    raise ValueError('menu changed')
                v['purchase_per_person_day_cents']=str(Decimal(v['purchase_cents'])/Decimal(7*(a+c)))
                v['consumed_per_person_day_cents']=str(Decimal(v['consumed_cents'])/Decimal(7*(a+c)))
                profiles[key]={'available':True,'view':v}
            except ValueError as e:
                if str(e)!='no feasible priced menu': raise
                profiles[key]={'available':False,'reason':'No complete priced basket'}
    return dict(schema_version=1,environment='test',publish=False,synthetic=base['synthetic'],default='2-0' if adults_max>=2 else '1-0',profiles=profiles)
