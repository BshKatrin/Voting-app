from people.candidate import Candidate

"""isDraw(Candidate, Candidate, String) -> bool
Renvoit True s'il y a égalité entre deux candidats selon un système de vote"""
def is_draw(candidate1, candidate2, voting_system) :
	if(candidate1.scores[voting_system] == candidate2.scores[voting_system]):
		return True
	return False


"""isFirstDraw(Candidate[], String) -> int
Renvoit 0 s'il n'y a pas d'égalité pour la première place (sur une liste de candidat déjà trié) pour système de vote en particulier, sinon renvoit l'indice du dernier candidat à éaglité pour la première place"""
def first_draw(candidates, voting_system):
	if(is_draw(candidates[0], candidates[1]):
	    i = 1
	    lc = len(candidates)
	    while(i<lc-2 && is_draw(candidates[i], candidates[i+1], voting_system)  ):
	        i++
	
	else:
	    return 0
	    
    return i

"""where_draw(Candidate[], String) -> int, int, int
Renvoit 0,0 s'il n'y à aucune égalité, sinon renvoit la place de l'égalité et l'indice du premier et dernier candidat à égalité pour cette place"""
def where_draw(candidates, voting_system):
    
    i = 0
    indice_fin = 0
	lc = len(candidates)
	
	while(i<lc-2):
	    
	    if(is_draw(candidates[i], candidates[i+1],voting_system)):
	       
	        indice_fin = i + first_draw(candidates[i:], voting_system)
	        return i+1, i, indice_fin
    
    return 0,0,0

"""all_draws(Candidate[], String) -> [(int, int, int)]
Renvoit toutes les égalités contenue dans la liste"""    
def all_draws(candidates, voting_system):
    list_draw = []
    i = 0
    place = 0
    indice_debut = 0
    indice_fin = 0
    lc = len(candidates)
    
    while(i<lc-2):
        place,indice_debut,indice_fin = where_draw(candidates[i:],voting_system)
        if(place == 0):
            return list_draw
        else: 
            list_draw.append((place, indice_debut, indice_fin))
            i = indice_fin
    return list_draw

"""print_draws(Candidate[], String) -> void
Affiche dans la consolle toutes les équalité de la liste"""
def print_draws(candidates, voting_system):
    list_draw = all_draws(candidates, voting_system)
    place = 0
    indice_debut = 0
    indice_fin = 0
    for(i in range len(candidates)):
        place,indice_debut,indice_fin = list_draw[i]
        
        print("Egalité pour la ", place, "avec les candidats d'indice ", indice_debut, " à ", indice_fin)
