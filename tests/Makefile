all : uni_condorcet uni_plurality  uni_approval uni_borda  uni_exhaustive  uni_veto uni_ranking

uni_condorcet : 
	python3 -m unittest test_condorcet.py
	
uni_plurality :
	python3 -m unittest test_plurality.py
		
uni_approval :
	python3 -m unittest test_approval.py

uni_borda :
	python3 -m unittest test_borda.py

uni_exhaustive :
	python3 -m unittest test_exhaustive_ballot.py

uni_veto :
	python3 -m unittest test_veto.py

uni_ranking:
	python3 -m unittest test_ranking.py