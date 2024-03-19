from math import sqrt

RADIUS=0.2

"""carre(float)->float
Retourne l'argument au carré"""
def carre(a):
	return a*a

"""liste_delegation(Elector[], Elector)->Elector[]
Retourne la liste des electeurs auquels delegator peut déléguer son vote"""
def liste_delegation(electors, delegator):
	electors_in_radius=[]
	x1,y1=delegator.get_position()
	
	for elector in electors:
		x2,y2=elector.get_position()
		dist=sqrt(carre(x2-x1)+carre(y2-y1))
		
		if(dist<=RADIUS):
			electors_in_radius.append(elector)
			
	return electors_in_radius
		
		
		
