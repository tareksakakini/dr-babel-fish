from functions import *

def TMTrain(vocab, ratio, search_cutoff):
	TM = {}
	for j, word in enumerate(vocab):
		#print j
		TM[word] = []
		curr_atoms = []
		for i in range(search_cutoff):
			print word
			cui = getCui(word, i)
			if cui != u"NONE": 
				atoms = getAllEnglishAtoms(cui)
				#print word, atoms
				#print len(atoms)
				#print atoms
				for atom in atoms:
					if atom not in curr_atoms:
						curr_atoms.append(atom)
						TM[word].append((atom, ratio**(search_cutoff-i-1)))
			else:
				break
		TM[word].append((word, ratio**(search_cutoff-0-1)))
	TM_wrangled = {}
	for word in TM:
		new_probs = []
		temp_sum = 0.0
		for tup in TM[word]:
			temp_sum += tup[1]
		for tup in TM[word]:
			new_probs.append((tup[0], tup[1]/temp_sum))
		new_probs_sorted = sorted(new_probs, key = lambda x:x[1], reverse = True)
		TM_wrangled[word] = new_probs_sorted
	#pickle.dump(TM_wrangled, open("TM.pkl", "w"), protocol = 2)
	return TM_wrangled

def str_to_pname(instr):
	identifier = getCui(instr, 0)
	if identifier != u"NONE":
		#print identifier
		pname = getPreferredName(identifier)
		return pname
	else:
		return None

#vocab = pickle.load(open("/Users/tareksakakini/Box Sync/Arches/Aim1/MTSystem/Data/googlenews_vocab.pkl"))
#vocab = vocab[:100]
#vocab = ["prn"]
#TMTrain(vocab, 2, 5)
			
