def topCandidates(ListCandidates,keyDict, turn): #trie les cnadidat en fonction de leur score au tour turn
    l=[] #la liste retournée est du type [Tuple(Candidate : candidat, int : score)]
    for i in ListCandidates :
        if keyDict not in i.scores :
            print("ce mode de vote n'a pas été utlisé")
        elif turn>=len(i.scores[keyDict]) :
            print("ce tours n'a pas été fait")
        else :
            for j in i.scores[keyDict][turn] :
                if l==[]:
                    l.append((i,j)) #ajoute si la liste est vide
                else:
                    t=len(l)
                    for k in range(t) :
                        _,s=l[k]
                        if j>s :
                            l.insert(k,(i,j)) #insere au bon index
                    if len(l)==t :
                        l.append((i,j)) #rajoute en fin de liste si cela n'a pas été fait
    return l


def initScores(listCandidates, keyDict):
    for i in listCandidates :
        if keyDict not in i.scores: 
            i.scores[keyDict]=[]
        i.scores[keyDict].append(0)
        
            



def plurality(listCandidates,elector,turn): # vote uninominal avec turn tours
    s="plurality"
    initScores(listCandidates,s)
    for i in range(listCandidates):
        if listCandidates[i]== elector.candidate_ranking[0]:
            listCandidates[i].scores[s][turn]+=1

def Borda(listCandidates,elector) : #pas fini
    s="Borda"
    initScores(listCandidates,s)

