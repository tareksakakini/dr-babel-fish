import sys
sys.path.insert(0, '/Users/tareksakakini/Box Sync/Arches/Aim1/MTSystem/TM')
from TMTrain import *
import cPickle as pickle
import itertools
import kenlm
import math
import os
from nltk.corpus import stopwords
import re

def generateTranslations(input_sentences):

	generateLMScores(input_sentences)
	LMScores = pickle.load(open("LMScores.pkl"))
	TMScores = pickle.load(open("TMScores.pkl"))

	#print LMScores.keys()[0]

	print len(set(LMScores.keys()))
	print len(set(TMScores.keys()))
		
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
		#print sent, id_trans, words_to_translate
		TM = TMTrain(words_to_translate, ratio, search_cutoff)
		word_translations = []
		for word in words_to_translate:
			word_translations.append(TM[word])
		all_combinations = list(itertools.product(*word_translations))
		#print all_combinations
		cand_translations = []
		print "comb nb: ",len(all_combinations)
		for comb in all_combinations:
			cand_sentence = [word for word in id_trans]
			cand_score = 1.0
			for i,trans in enumerate(comb):
				cand_sentence[indices_to_translate[i]] = " ".join(trans[0])
				cand_score = cand_score*float(trans[1])
			cand_sent_str = unicode(" ".join(cand_sentence))
			cand_translations.append((cand_sent_str, TMScores[cand_sent_str] + LMScores[cand_sent_str]))
		sorted_translations = sorted(cand_translations, key = lambda x:x[1], reverse = True)
		print " ".join(sent), "\t", sorted_translations[0][0]

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

def generateLMScores(input_sentences):
	LMScores = {}
	TMScores = {}
	LM_path = "/Users/tareksakakini/Desktop/MTSystem/LM/rnnlm/"
        LM_sents_path = LM_path + "LM_sents.txt"
        LM_scores_path = LM_path + "LM_scores.txt"
        LM_command_path = LM_path + "faster-rnnlm/faster-rnnlm/rnnlm"
        LM_model_path = LM_path + "large_rnn_lm"
        LM_sents_file = open(LM_sents_path, "w")
	for k,sent in enumerate(input_sentences):
		print k
		sent = sent.split()
		id_trans = identityTransStage(sent)
		words_to_translate = []
		indices_to_translate = []
		for i, word in enumerate(id_trans):
			if word == "":
				words_to_translate.append(sent[i])
				indices_to_translate.append(i)
		if len(words_to_translate) > 5:
			print "skipped"
			continue
		TM = TMTrain(words_to_translate, ratio, search_cutoff)
		word_translations = []
		for word in words_to_translate:
			word_translations.append(TM[word])
		all_combinations = list(itertools.product(*word_translations))
		print "comb nb: ",len(all_combinations)
		for comb in all_combinations:
			cand_score = 1.0
			cand_sentence = [word for word in id_trans]
			for i,trans in enumerate(comb):
				cand_sentence[indices_to_translate[i]] = " ".join(trans[0])
				cand_score = cand_score*float(trans[1])
			sent_string = " ".join(cand_sentence)
			TMScores[sent_string] = math.log(cand_score)
			LM_sents_file.write(sent_string + "\n")
	LM_sents_file.close()
	os.system(LM_command_path + " -rnnlm " + LM_model_path + " -test " + LM_sents_path  + " > " + LM_scores_path)
	i = 0
	LM_sents_lines = open(LM_sents_path).readlines()
	LM_scores_lines = open(LM_scores_path).readlines()
	print len(LM_sents_lines)
	print len(LM_scores_lines)
	for i in range(len(LM_sents_lines)):
		score = LM_scores_lines[i].strip()
		if score == "OOV":
			score = -10000000
		else:
			score = float(score)
		LMScores[LM_sents_lines[i].strip()] = score
	
	pickle.dump(LMScores, open("LMScores.pkl", "w"), protocol = 2)
	pickle.dump(TMScores, open("TMScores.pkl", "w"), protocol = 2)

def getLMScores(current_output_sentence, all_combinations, indices_to_translate):
	LMScores = {}
	cand_sents = []
	for comb in all_combinations:
		cand_sentence = [word for word in current_output_sentence]
		for i,trans in enumerate(comb):
                        cand_sentence[indices_to_translate[i]] = " ".join(trans[0])
		cand_sents.append(cand_sentence)
	LM_path = "/Users/tareksakakini/Desktop/MTSystem/LM/rnnlm/"
	LM_sents_path = LM_path + "LM_sents.txt"
	LM_scores_path = LM_path + "LM_scores.txt" 
	LM_command_path = LM_path + "faster-rnnlm/faster-rnnlm/rnnlm"
	LM_model_path = LM_path + "large_rnn_lm"
	LM_sents_file = open(LM_sents_path, "w")
	for sent in cand_sents:
		LM_sents_file.write(" ".join(sent) + "\n")
	LM_sents_file.close()
	os.system(LM_command_path + " -rnnlm " + LM_model_path + " -test " + LM_sents_path  + " > " + LM_scores_path)
	i = 0
	for line in open(LM_scores_path):
		sent = " ".join(cand_sents[i])
		i += 1
		score = line.strip()
		if score == "OOV":
			score = -10000000
		else:
			score = float(score)
		LMScores[sent] = score
	return LMScores

def getTMScores(current_output_sentence, all_combinations, indices_to_translate):
	TMScores = {}
	for comb in all_combinations:
		cand_score = 1.0
		cand_sentence = [word for word in current_output_sentence]
		for i,trans in enumerate(comb):
                        cand_sentence[indices_to_translate[i]] = " ".join(trans[0])
                        cand_score = cand_score*float(trans[1])
		TMScores[" ".join(cand_sentence)] = math.log(cand_score)
	return TMScores

def scoreLM(sentence):
	return LMModel.score(" ".join(sentence), bos = True, eos = True)
			

def translate(input_sentence):
	output_sentence = []
	for word in input_sentence:
		if vocab.index(word) > vocab_cutoff:
			output_sentence.append("")
		else:
			output_sentence.append(word)
	transs = generateTranslations(input_sentence, output_sentence)
	return transs[0][0]

global vocab, sigs, ratio, vocab_cutoff, search_cutoff, LMModel, stopWords
vocab = pickle.load(open("/Users/tareksakakini/Box Sync/Arches/Aim1/MTSystem/Data/googlenews_vocab.pkl"))
sigs = pickle.load(open("/Users/tareksakakini/Box Sync/Arches/Aim1/MTSystem/Data/Sigs/unstructuredSigs_lc.pkl"))
sigs = list(set(sigs))
sigs = [sent for sent in sigs if sent != ""]
#LMModel = kenlm.Model('LM/test.arpa')
LMModel = kenlm.Model('LM/5gram.lm.bin')
print "loaded LM"
stopWords = stopwords.words('english')
vocab_cutoff = 10000
ratio = 1
search_cutoff = 2

step = 5

print LMModel.score("every 8 weeks for ra", bos = True, eos = True)
print LMModel.score("every 8 weeks for rheumatoid arthritis", bos = True, eos = True)
print LMModel.score("every 8 weeks for anemia refractory", bos = True, eos = True)

#for j in range(15,20,step):
#	#input_sentences = sigs[j:j+step]
#	input_sentences = ["synponi aria infusion every 8 weeks for ra"]
#	generateTranslations(input_sentences)

