# -*- coding: utf-8 -*-

### Master-funksjon for å hente data fra NVDB APIet
def hentData(path):
	'Returnerer data fra NVDB API p√• JSON.format'
	import requests

	api = 'https://www.vegvesen.no/nvdb/api'
	url = api+path
	headers = {'accept': 'application/vnd.vegvesen.nvdb-v1+json'}

	r = requests.get(url, headers=headers)
	respons = r.json()

	return respons

def hentObjekt(objektid):
	objekt = hentData('/vegobjekter/objekt/'+objektid)
	return objekt

def hentObjektType(objekttypeid):
	objekttype = hentData('/datakatalog/objekttyper/'+objekttypeid)
	return objekttype



### Funksjonene nedenfor har OBJEKTTYPE som innparameter
def skrivObjektType(objekttype):
	print objekttype['navn']
	return

### Funksjonene nedenfor har OBJEKT som innparameter

### Tester
# print hentData('/datakatalog/objekttyper')
# print hentObjekt('338309712')
# objekttype = hentObjektType('3')
# skrivObjektType(objekttype)



