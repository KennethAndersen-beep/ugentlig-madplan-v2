"""Bounded exact menu selection for a small, preapproved recipe pool."""
from itertools import combinations
from collections import Counter
from math import comb
from meal_budget import budget

def select_menu(recipes,packs,units,*,days=7,max_fish=1,min_proteins=3,max_per_protein=3,max_candidates=1000,**options):
    if len({r['id'] for r in recipes})!=len(recipes): raise ValueError('duplicate recipe id')
    eligible=[r for r in recipes if r['protein'] in {'fish','pork','beef','chicken','other_meat'}]
    if not 1<=days<=len(eligible): raise ValueError('insufficient recipes')
    if comb(len(eligible),days)>max_candidates: raise ValueError('candidate limit exceeded')
    best=None; evaluated=0; unpriced=0
    for subset in combinations(eligible,days):
        counts=Counter(r['protein'] for r in subset)
        if counts['fish']>max_fish or len(counts)<min_proteins or max(counts.values())>max_per_protein: continue
        evaluated+=1
        try: b=budget(subset,packs,units,**options)
        except ValueError as e:
            if str(e)!='no complete priced basket': raise
            unpriced+=1; continue
        rank=(b['total_cents'],len(b['stores']),b['leftover_value_cents'],tuple(sorted(r['id'] for r in subset)))
        if best is None or rank<best[0]: best=(rank,subset,b)
    if best is None: raise ValueError('no feasible priced menu')
    return dict(recipes=best[1],budget=best[2],evaluated=evaluated,unpriced=unpriced)
