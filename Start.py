import random

class Person : #Classe mère d'Elector et Candidate
    def __init__(self, position): #est composé d'un tuple (x,y) qui corrrespond à sa position
        self.position = position

    def __getPosition__(self):
        return self.position

class Elector(Person) : #Un Elector a sa position et une liste qui correspond à son vote
    def __init__(self, position, vote) :
        super(self, position)
        self.vote = vote

    def __getVote__(self):
        return self.vote

class Candidate(Person) : #Un Candidate a sa position
    def __init__(self, position) :
        super(self, position)
        self.score = 0
    
def createElector(pos, listCandidate):

    v = vote(pos, listCandidate)

    e = Elector(pos, v)

    return e

def createListElector(listPos, listCandidate):

    listElector = []

    for i in listPos:
        listElector.append(createElector(i, listCandidate))

    return listElector

