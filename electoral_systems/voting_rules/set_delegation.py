import random

"""set_delegation(Elector[]) -> Elector"""
def set_delegation(electors):
	if len(electors)==0:
		return None
	
	if len(electors)==1:
		return electors[0]
		
	weights=[]
	total_k=0
	
	for e1 in electors:
		total_k+=e1.knowledge
	
	for e2 in electors:
		pn=e1.knowledge/total_k
		weights.append(pn)
		
	return random.choices(electors, weights = weights, k=1)
	

