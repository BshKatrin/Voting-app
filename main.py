from people import *
from random import uniform

if __name__ == "__main__":
    # code de graphique (QT)
   n_candidates = 3
   lst_candidates = []

   for i in range(n_candidates):
    lst_candidates.append(Candidate((uniform(-1,1), uniform(-1,1))))
