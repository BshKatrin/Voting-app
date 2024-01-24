from .elector import Elector
import random

def createListElector(listPos, listCandidate):
    listElector = []
    for i in listPos:
        listElector.append(Elector(i, listCandidate))
    return listElector


def createListElectorRand(n, listCandidate) :
    listElector = []
    for _ in range(n):
        x=random.uniform(-1, 1)
        y=random.uniform(-1, 1)
        listElector.append(Elector((x,y), listCandidate))
    return listElector
