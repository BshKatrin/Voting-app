def createElector(pos, listCandidate):

    v = vote(pos, listCandidate)

    e = Elector(pos, v)

    return e

def createListElector(listPos, listCandidate):

    listElector = []

    for i in listPos:
        listElector.append(createElector(i, listCandidate))

    return listElector

