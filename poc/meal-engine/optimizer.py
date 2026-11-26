"""Isolated prototype: integer quantities in a common unit, prices in øre."""
from dataclasses import dataclass
from itertools import combinations, product
@dataclass(frozen=True)
class Pack:
    ingredient: str
    store: str
    quantity: int
    cents: int
    limit: int | None = None

def optimize(needs, packs, visit_cents=0, max_stores=None):
    if type(visit_cents) is not int or visit_cents < 0: raise ValueError('visit cost')
    if any(type(q) is not int or q < 0 for q in needs.values()): raise ValueError('invalid demand')
    if any(type(p.quantity) is not int or p.quantity<=0 or type(p.cents) is not int or p.cents<=0 or (p.limit is not None and (type(p.limit) is not int or p.limit<0)) for p in packs): raise ValueError('invalid pack')
    stores=sorted({p.store for p in packs}); best=None
    for n in range(1,min(len(stores),max_stores if max_stores is not None else len(stores))+1):
        for allowed in combinations(stores,n):
            basket=[]; cost=0; rest={}; feasible=True
            for ingredient,demand in needs.items():
                if demand==0: continue
                opts=[p for p in packs if p.ingredient==ingredient and p.store in allowed]
                choices=[]
                for counts in product(*(range(min((demand+p.quantity-1)//p.quantity,p.limit if p.limit is not None else (demand+p.quantity-1)//p.quantity)+1) for p in opts)):
                    qty=sum(p.quantity*c for p,c in zip(opts,counts))
                    if qty>=demand:
                        choices.append((sum(p.cents*c for p,c in zip(opts,counts)),qty-demand,counts))
                if not choices: feasible=False; break
                c,r,counts=min(choices); cost+=c; rest[ingredient]=r
                basket.extend((p,k) for p,k in zip(opts,counts) if k)
            if not feasible: continue
            used={p.store for p,k in basket}; total=cost+visit_cents*len(used)
            rank=(total,len(used),sum(rest.values()))
            if best is None or rank<best[0]: best=(rank,dict(purchase_cents=cost,total_cents=total,stores=sorted(used),basket=basket,remainder=rest))
    if not any(needs.values()): return dict(purchase_cents=0,total_cents=0,stores=[],basket=[],remainder={})
    if best is None: raise ValueError('no complete priced basket')
    return best[1]
