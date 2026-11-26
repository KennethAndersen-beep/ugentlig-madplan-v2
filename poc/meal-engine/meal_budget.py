"""Prototype: aggregate recipe needs, buy whole packs, allocate weighted cost.
All canonical quantities are integer grams, ml or pieces. No density assumptions.
"""
from decimal import Decimal, ROUND_CEILING
from collections import defaultdict
from optimizer import optimize
UNITS={'g':('g',1),'kg':('g',1000),'ml':('ml',1),'cl':('ml',10),'dl':('ml',100),'l':('ml',1000),'stk':('stk',1)}
def number(x):
    d=Decimal(str(x))
    if not d.is_finite() or d<0: raise ValueError('invalid quantity')
    return d

def budget(recipes,packs,ingredient_units,adults=2,children=0,child_factor='0.5',**options):
    if type(adults) is not int or type(children) is not int or min(adults,children)<0: raise ValueError('invalid household')
    factor=number(child_factor)
    if factor>1: raise ValueError('invalid child factor')
    portions=Decimal(adults)+Decimal(children)*factor
    if portions<=0: raise ValueError('empty household')
    daily=[]; totals=defaultdict(Decimal)
    for recipe in recipes:
        base=number(recipe['servings'])
        if not base: raise ValueError('zero servings')
        demand=defaultdict(Decimal)
        for ingredient,qty,unit in recipe['ingredients']:
            canonical,mult=UNITS[unit]
            if ingredient_units[ingredient]!=canonical: raise ValueError('incompatible unit')
            demand[ingredient]+=number(qty)*mult*portions/base
        for k,v in demand.items(): totals[k]+=v
        daily.append(demand)
    needs={k:int(v.to_integral_value(rounding=ROUND_CEILING)) for k,v in totals.items() if v>0}
    result=optimize(needs,packs,**options)
    bought=defaultdict(int); spent=defaultdict(int)
    for p,n in result['basket']:
        bought[p.ingredient]+=p.quantity*n; spent[p.ingredient]+=p.cents*n
    rates={k:Decimal(spent[k])/bought[k] for k in bought}
    used=sum((v*rates[k] for k,v in totals.items() if v),Decimal(0))
    result.update(consumed_cents=used,leftover_value_cents=Decimal(result['purchase_cents'])-used,daily_consumed_cents=[sum((v*rates[k] for k,v in d.items() if v),Decimal(0)) for d in daily],exact_needs=dict(totals),adult_equivalents=portions)
    return result
