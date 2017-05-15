#################################################################################
# usage of the script
# usage: python search-terms.py -k APIKEY -v VERSION -s STRING
# see https://documentation.uts.nlm.nih.gov/rest/search/index.html for full docs
# on the /search endpoint
#################################################################################

from Authentication import *
import requests
import json
import argparse
import csv
import re
import cPickle as pickle
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import *
from collections import Counter
import sys

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-s", "--string", required =  False, dest="string", default = "No String in input", help = "enter a search term, like 'diabetic foot'")
args = parser.parse_args()
string = args.string

vocab_thresh = 10000

global apikey, version, uri, vocab, vocab_trunc, stemmer, V
apikey = "ce3ce3c9-0eed-4e29-8bb6-3f1080716fcc"
version = "current"
uri = "https://uts-ws.nlm.nih.gov"
vocab = pickle.load(open("googlenews_vocab.pkl"))
vocab_trunc = vocab[:vocab_thresh]
data_path = "/Users/tareksakakini/Box Sync/Arches/Aim1/Datasets/OSF_data.csv"
stemmer = PorterStemmer()
V = len(vocab)

def augment_sentence(sent):
	aug_sent = []
	for word in sent.split():
		aug_sent.append(word)
		pref_word = getCommonName(word)
		aug_sent.append("{{"+ pref_word +"}}")
	return " ".join(aug_sent)		

def getSemanticType(cui):

        AuthClient = Authentication(apikey)
        identifier = cui
        tgt = AuthClient.gettgt()

        try:
           source
        except NameError:
           source = None

        ##if we don't specify a source vocabulary, assume we're retrieving UMLS CUIs
        if source is None:
            content_endpoint = "/rest/content/"+str(version)+"/CUI/"+str(identifier)

        else:
            content_endpoint = "/rest/content/"+str(version)+"/source/"+str(source)+"/"+str(identifier)

        ##ticket is the only parameter needed for this call - paging does not come into play because we're only asking for one Json object
	query = {'ticket':AuthClient.getst(tgt)}
        r = requests.get(uri+content_endpoint,params=query)
        r.encoding = 'utf-8'
        items  = json.loads(r.text)
        jsonData = items["result"]
	semanticType = jsonData["semanticTypes"][0]["name"]
	return semanticType


def getAllEnglishAtoms(cui):

	AuthClient = Authentication(apikey)
	identifier = cui
	tgt = AuthClient.gettgt()

	try:
	   source
	except NameError:
	   source = None

	##if we don't specify a source vocabulary, assume we're retrieving UMLS CUIs
	if source is None:
	    content_endpoint = "/rest/content/"+str(version)+"/CUI/"+str(identifier)+"/atoms?language=ENG"

	else:
	    content_endpoint = "/rest/content/"+str(version)+"/source/"+str(source)+"/"+str(identifier)+"/atoms?language=ENG"

	##ticket is the only parameter needed for this call - paging does not come into play because we're only asking for one Json object
	query = {'ticket':AuthClient.getst(tgt)}
	r = requests.get(uri+content_endpoint,params=query)
	r.encoding = 'utf-8'
	items  = json.loads(r.text)
	jsonData = items["result"]
	atomNames = []
	for entry in jsonData:
		atomNames += entry["name"].lower().split()
	return atomNames

def getCui(string, i):

	content_endpoint = "/rest/search/"+version
	##get at ticket granting ticket for the session
	AuthClient = Authentication(apikey)
	tgt = AuthClient.gettgt()
	pageNumber=0
	ticket = AuthClient.getst(tgt)
	query = {'string':string,'ticket':ticket, 'pageNumber':pageNumber}
	r = requests.get(uri+content_endpoint,params=query)
	r.encoding = 'utf-8'
	items  = json.loads(r.text)
	jsonData = items["result"]
	cui = jsonData["results"][i]["ui"]
	return cui

def getPreferredName_2(cui):

	AuthClient = Authentication(apikey)
	identifier = cui
	tgt = AuthClient.gettgt()

	try:
	   source
	except NameError:
	   source = None

	##if we don't specify a source vocabulary, assume we're retrieving UMLS CUIs
	if source is None:
	    content_endpoint = "/rest/content/"+str(version)+"/CUI/"+str(identifier)+"/atoms?language=ENG"

	else:
	    content_endpoint = "/rest/content/"+str(version)+"/source/"+str(source)+"/"+str(identifier)+"/atoms?language=ENG"

	##ticket is the only parameter needed for this call - paging does not come into play because we're only asking for one Json object
	query = {'ticket':AuthClient.getst(tgt)}
	r = requests.get(uri+content_endpoint,params=query)
	r.encoding = 'utf-8'
	items  = json.loads(r.text)
	jsonData = items["result"]
	atomNames = []
	for entry in jsonData:
		atomNames.append(entry["name"].lower())
	names_appended = []
	for name in atomNames:
		Freqs = []
		for word in name.split():
			if word in vocab:
				Freqs.append(vocab.index(word))
			else:
				Freqs.append(V)
		avgF = float(sum(Freqs))/len(Freqs)
		names_appended.append((name, avgF))

	names_sorted = sorted(names_appended, key = lambda x: x[1])

	return names_sorted[0][0]

def getPreferredName(identifier):

	AuthClient = Authentication(apikey)	
	tgt = AuthClient.gettgt()

	try:
	   source
	except NameError:
	   source = None

	##if we don't specify a source vocabulary, assume we're retrieving UMLS CUIs
	if source is None:
	    content_endpoint = "/rest/content/"+str(version)+"/CUI/"+str(identifier)

	else:
	    content_endpoint = "/rest/content/"+str(version)+"/source/"+str(source)+"/"+str(identifier)

	##ticket is the only parameter needed for this call - paging does not come into play because we're only asking for one Json object
	query = {'ticket':AuthClient.getst(tgt)}
	r = requests.get(uri+content_endpoint,params=query)
	r.encoding = 'utf-8'
	items  = json.loads(r.text)
	jsonData = items["result"]

	name = jsonData["name"]
	
	return name

def getCommonName(string):
	
	forbid_types = ["Geographic Area"]

	translations_retrieved = []

	if not(re.search('[a-zA-Z]', string)):
		translation = "No Characters"
		translations_retrieved.append(translation)
		return translations_retrieved

	if string in vocab_trunc:
		translation =  "Common Word"
		translations_retrieved.append(translation)
		return translations_retrieved

	for i in range(10):

		try:
			identifier = getCui(string, i)
			name = getPreferredName_2(identifier).lower()

			if string not in getAllEnglishAtoms(identifier):
				translation = "not English"
				translations_retrieved.append(translation)
			elif getSemanticType(identifier) in forbid_types:
				translation = "invalid sem type"
				translations_retrieved.append(translation)
			elif name == string:
				translation = "identity translation"
				translations_retrieved.append(translation)
			elif stemmer.stem(name) == stemmer.stem(string):
				translation = "morph related translation"
				translations_retrieved.append(translation)
			else:
				translations_retrieved.append(name)
				return translations_retrieved
		except:
			translation =  "not in UMLS"
			translations_retrieved.append(translation)
			return translations_retrieved

	return translations_retrieved

def getSigs(path):
	csvfile = open(path, "rb")
	data = csv.DictReader(csvfile)
	sigs = []
	for row in data:
		sigs.append(row["Sig"])
	return sigs

def divideAndStoreSigs(path):
	csvfile = open(path, "rb")
	data = csv.DictReader(csvfile)
	structuredSigs = []
	unstructuredSigs = []
	for row in data:
		Dose = row["Dose"]
		Route = row["Route"]
		Frequency = row["Frequency"]
		Sig = row["Sig"]
		Sigs = Sig.split(". ")
		Sigs_tok = []
		for sig in Sigs:
			Sigs_tok.append(" ".join(word_tokenize(sig)))
		if Dose == "" and Route == "" and Frequency == "":
			unstructuredSigs.append(" ".join(Sigs_tok))
		else:
			structuredSigs += Sigs_tok[:1]
			unstructuredSigs += Sigs_tok[1:]
	pickle.dump(structuredSigs, open("structuredSigs.pkl", "w"), protocol = 2)
	pickle.dump(unstructuredSigs, open("unstructuredSigs.pkl", "w"), protocol = 2)

	strSigs_lc = []
	unstrSigs_lc = []

	for sig in structuredSigs:
		strSigs_lc.append(sig.lower())
	for sig in unstructuredSigs:
		unstrSigs_lc.append(sig.lower())
		
	pickle.dump(strSigs_lc, open("structuredSigs_lc.pkl", "w"), protocol = 2)
        pickle.dump(unstrSigs_lc, open("unstructuredSigs_lc.pkl", "w"), protocol = 2)
		
def getVocab(ListOfStrings):
	all_words = []
	for string in ListOfStrings:
		all_words += string.split()
	c = Counter(all_words)
	tups = []
	for key in c:
		tups.append((key,c[key]))
	sorted_tups = sorted(tups, key = lambda x: x[1], reverse = True)	
	#unique_words = set(all_words)
	return sorted_tups

