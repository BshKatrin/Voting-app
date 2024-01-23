def initScores(listCandidates, keyDict):
    for i in listCandidates :
        if keyDict not in i.scores: 
            i.scores[keyDict]=[]
        i.scores[keyDict].append(0)
        
            



def plurality(listCandidates,elector,turn):
    initScores(listCandidates,keyDict)
    for i in range(listCandidates):
        if listCandidates[i]== elector.candidate_ranking[0]:
            listCandidates[i].scores[keyDict][turn]+=1
