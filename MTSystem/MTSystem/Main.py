import sys
sys.path.insert(0, '/home/sakakini/sakakini/ARCHES/MTSystem/MTSystem/TM')
from TMTrain import *
import cPickle as pickle
import itertools
import kenlm
import math
import os
from nltk.corpus import stopwords
import re
import numpy as np
import gensim

def generateTranslations(input_sentences):

	for sent in input_sentences:
		sent = sent.split()
		id_trans = identityTransStage(sent)
		words_to_translate = []
		indices_to_translate = []
		for i, word in enumerate(id_trans):
			if word == "":
				words_to_translate.append(sent[i])
				indices_to_translate.append(i)
		#print words_to_translate
		if len(indices_to_translate) > 5:
			print "skipped"
			continue
		#print sent, id_trans, words_to_translate
		TM = TMTrain(words_to_translate, ratio, search_cutoff)
		word_translations = []
		for word in words_to_translate:
			word_translations.append(TM[word])
		all_combinations = list(itertools.product(*word_translations))
		#print all_combinations
		cand_translations = []
		#print "comb nb: ",len(all_combinations)
		for comb in all_combinations:
			cand_sentence = [word for word in id_trans]
			cand_score = 1.0
			for i,trans in enumerate(comb):
				#cand_sentence[indices_to_translate[i]] = " ".join(trans[0])
				cand_sentence[indices_to_translate[i]] = trans[0]
				cand_score = cand_score*float(trans[1])
			cand_sent_str = unicode(" ".join(cand_sentence))
			LMScore = scoreLM(cand_sent_str)
			TMScore = math.log(cand_score)
			#print cand_sent_str
			#print "LMScore: ", LMScore, "TMScore: ", TMScore
			cand_translations.append((cand_sent_str, TMScore + LMScore))
		sorted_translations = sorted(cand_translations, key = lambda x:x[1], reverse = True)
		#print " ".join(sent), "\t", sorted_translations[0][0]
		print sorted_translations[0][0]


def generateTranslationsByEmb(input_sentences):

	for sent in input_sentences:
		#print sent
		sent = sent.split()
		id_trans = identityTransStage(sent)
		words_to_translate = []
		indices_to_translate = []
		for i, word in enumerate(id_trans):
			if word == "":
				words_to_translate.append(sent[i])
				indices_to_translate.append(i)
		#print words_to_translate
		if len(indices_to_translate) > 5:
			print "skipped"
			continue
		#print sent, id_trans, words_to_translate
		#TM = TMTrain(words_to_translate, ratio, search_cutoff)
		TM = {}
		for word in words_to_translate:
			TM[word] = [(word,1.0)]
			try:
				TM[word] += model.most_similar(positive=[word],topn=20)
			except:
				a=None
		word_translations = []
		for word in words_to_translate:
			word_translations.append(TM[word])
		all_combinations = list(itertools.product(*word_translations))
		#print all_combinations
		cand_translations = []
		#print "comb nb: ",len(all_combinations)
		for comb in all_combinations:
			cand_sentence = [word for word in id_trans]
			cand_score = 1.0
			for i,trans in enumerate(comb):
				#cand_sentence[indices_to_translate[i]] = " ".join(trans[0])
				cand_sentence[indices_to_translate[i]] = trans[0]
				cand_score = cand_score*float(trans[1])
			cand_sent_str = unicode(" ".join(cand_sentence))
			LMScore = scoreLM(cand_sent_str)
			TMScore = math.log(cand_score)
			#print cand_sent_str
			#print "LMScore: ", LMScore, "TMScore: ", TMScore
			cand_translations.append((cand_sent_str, TMScore + LMScore))
		sorted_translations = sorted(cand_translations, key = lambda x:x[1], reverse = True)
		#print " ".join(sent), "\t", sorted_translations[0][0]
		print sorted_translations[0][0]

def getMinAvgComb(combs):
	#print len(combs)
	if len(combs) == 0:
		return combs
	avgs = []
	for comb in combs:
		string = ""
		for el in comb:
			string += el[0]
		words = string.split()
		total = 0.0
		for word in words:
			if word in stopWords:
				total += 1
			elif not re.search(r'[a-zA-Z]', word):
				total += 1
			elif word not in word_to_index:
				total += 10000000
			else:
				total += word_to_index[word]
		avgs.append(total/len(words))
	return combs[np.argmin(avgs)]

def generateTranslationsByMinAvg(input_sentences):

	for sent in input_sentences:
		sent = sent.split()
		id_trans = identityTransStage(sent)
		words_to_translate = []
		indices_to_translate = []
		for i, word in enumerate(id_trans):
			if word == "":
				words_to_translate.append(sent[i])
				indices_to_translate.append(i)
		if len(indices_to_translate) > 5:
			print "skipped"
			continue
		TM = TMTrain(words_to_translate, ratio, search_cutoff)
		word_translations = []
		for word in words_to_translate:
			word_translations.append(TM[word])
		all_combinations = list(itertools.product(*word_translations))
		cand_sentence = [word for word in id_trans]
		if len(words_to_translate) != 0:
			comb = getMinAvgComb(all_combinations)
		else:
			comb = []
		for i,trans in enumerate(comb):
			cand_sentence[indices_to_translate[i]] = trans[0]
		cand_sent_str = unicode(" ".join(cand_sentence))
		print cand_sent_str

def pnameTransStage(input_sentence):
	output_sentence = []
        for word in input_sentence:
		if word in stopWords:
			output_sentence.append(word)
		elif not re.search(r'[a-zA-Z]', word):
			output_sentence.append(word)
		elif word not in vocab:
			pname = str_to_pname(word)
			if pname != None:
				output_sentence.append(pname)
			else:
				output_sentence.append(word)
		else:
			if vocab.index(word) > vocab_cutoff:
				pname = str_to_pname(word)
				if pname != None:
					output_sentence.append(pname)
				else:
					output_sentence.append(word)
                        else:
                                output_sentence.append(word)
	return output_sentence

def generateTranslationsByPname(input_sentences):
	for sent in input_sentences:
		#print sent
                sent = sent.split()
                id_trans = identityTransStage(sent)
                words_to_translate = []
                indices_to_translate = []
                for i, word in enumerate(id_trans):
                        if word == "":
                                words_to_translate.append(sent[i])
                                indices_to_translate.append(i)
		print words_to_translate
                if len(indices_to_translate) > 5:
                        #print "skipped"
                        continue
		#output_sent = pnameTransStage(sent)
		#print " ".join(output_sent)
		

def identityTransStage(input_sentence):
	output_sentence = []
        for word in input_sentence:
		if word in stopWords:
			output_sentence.append(word)
		elif not re.search(r'[a-zA-Z]', word):
			output_sentence.append(word)
		elif word not in vocab:
			output_sentence.append("")
		else:
			if vocab.index(word) > vocab_cutoff:
                                output_sentence.append("")
                        else:
                                output_sentence.append(word)
	return output_sentence

def scoreLM(sentence):
	return LMModel.score(sentence, bos = True, eos = True)
			
global vocab, sigs, ratio, vocab_cutoff, search_cutoff, LMModel, stopWords, word_to_index, model
vocab = pickle.load(open("../../Large_Files/Data/googlenews_vocab.pkl"))
#stSigs = pickle.load(open("/Users/tareksakakini/Box Sync/Arches/Aim1/MTSystem/Data/Sigs/structuredSigs_lc.pkl"))
#unstSigs = pickle.load(open("/Users/tareksakakini/Box Sync/Arches/Aim1/MTSystem/Data/Sigs/unstructuredSigs_lc.pkl"))
stSigs = open("../../Large_Files/Data/Sigs/cleaned_stSigs.txt").readlines()
unstSigs = open("../../Large_Files/Data/Sigs/cleaned_unstSigs.txt").readlines()
stSigs = list(set(stSigs))
stSigs = [sent for sent in stSigs if sent != ""]
unstSigs = list(set(unstSigs))
unstSigs = [sent for sent in unstSigs if sent != ""]
LMModel = kenlm.Model('../../Large_Files/LM/5gram.lm.bin')
print "loaded LM"
stopWords = stopwords.words('english')
vocab_cutoff = 10000
ratio = 1
search_cutoff = 2
word_to_index = {}
#model = gensim.models.KeyedVectors.load_word2vec_format("Data/GoogleNews-vectors-negative300.bin", binary = True)

for i,word in enumerate(vocab):
	word_to_index[word] = i

print "Done"

input_sentences = unstSigs[66:67]
generateTranslations(input_sentences)
#for sent in input_sentences:
#	print sent.strip()

#for sig in unstSigs:
#	print sig

#print scoreLM("indications : pneumonia caused by inhaling a substance into the lungs")
#print scoreLM("indications : lung inflammation caused by inhaling a substance into the lungs")
#print scoreLM("patients has 4 days left of this to take from 10/20/15")
#print scoreLM("Patient has 4 days left of this to take from 10/20/15")
