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

parser = argparse.ArgumentParser(description='process user given parameters')
#parser.add_argument("-u", "--username", required =  True, dest="username", help = "enter username")
#parser.add_argument("-p", "--password", required =  True, dest="password", help = "enter passowrd")
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-s", "--string", required =  True, dest="string", help = "enter a search term, like 'diabetic foot'")

args = parser.parse_args()
#username = args.username
#password = args.password
apikey = args.apikey
version = args.version
string = args.string
uri = "https://uts-ws.nlm.nih.gov"
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
cui = jsonData["results"][0]["ui"]

###################################
#get TGT for our session
###################################

identifier = cui

tgt = AuthClient.gettgt()
uri = "https://uts-ws.nlm.nih.gov"

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

print name


