
import json
import requests
import csv

api = 'https://www.vegvesen.no/nvdb/api'

class Objekt:
    'NVDB-objekt'
   
    def __init__(self, data):
        self.data = data 
        self.id = data['objektId']
        
        self.veglenker = data['lokasjon']['veglenker']
        for i, veglenke in enumerate(self.veglenker):
            del self.veglenker[i]['direction']
            
    def lengde(self):
        """Gjelder kun strekningsobjekttyper. Egen subklasse etter hvert?"""
        return self.data['strekningslengde']
        
    def egenskaper(self):
        return self.data['egenskaper']
                
    def egenskap(self, egenskapstype, enum='', verdi=''):
        """ Gir inn id på egenskap som skal returnere. 
        Argumentet verdi er default-verdi """
        
        for egenskap in self.data['egenskaper']:
            if egenskap['id'] == egenskapstype:
                if not enum:
                    verdi = egenskap['verdi']
                elif enum and egenskap['enumVerdi']['id'] == enum:
                    verdi = egenskap['verdi']
        return verdi
        
    def lokasjon(self, omradetype):
        return self.data['lokasjon'][omradetype]['navn']
        
    def assosiasjoner(self, objekttype=''):
        """Hvis objekttype er satt, lag en liste med alle datterobjektene som
        er av den typen. Hvis det ikke finnes noen, raise KeyError"""
        
        if objekttype:
            respons = []
            for assosiasjon in self.data['assosiasjoner']:
                if assosiasjon['relasjon']['typeId'] == objekttype:
                    respons.append(assosiasjon)   
                    
            if not respons:
                raise KeyError('Objektet har ingen assosiasjoner '
                               'av objekttype %s' % objekttype)
            else:
                return respons
        else:
            return self.data['assosiasjoner']
            
class Objekter:
    'En liste med NVDB-objekter'
    
class Resultat:
    'Resultat som returnes fra søkegrensesnittet. Støtter bare én objekttype'
    
    def __init__(self, data):
        self.data = data
        self.antall = data['totaltAntallReturnert']
        
    def objekter(self):
        return self.data['resultater'][0]['vegObjekter']

def query(path, params=''):
    """Leverer data på JSON-format fra NVDB. Returnerer et objekt.
    
    Argumenter:
    path -- Beskrivelse
    params -- Beskrivelse (default: '')
    
    """
    url = api+path
    headers = {'accept': 'application/vnd.vegvesen.nvdb-v1+json'}
    
    r = requests.get(url, headers=headers, params=params, verify=False)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        raise Exception('Feil ved henting av '+r.url+': '+str(r.status_code))

def query_search(objekttyper, lokasjon=''):
    """Leverer data på JSON-format fra NVDB API gjennom sokegrensesnittet. 
    Objekttyper må angis, men lokasjon er valgfritt. Returnerer et objekt.
    
    Argumenter:
    objekttyper -- Beskrivelse
    lokasjon -- Beskrivelse (default: '')
    
    """
    sokobjekt = {}
    if lokasjon:
        sokobjekt['lokasjon'] = lokasjon
    sokobjekt['objektTyper'] = objekttyper
                
    return Resultat(query('/sok', {'kriterie': json.dumps(sokobjekt)}))
    
def csv_skriv(filnavn, input):
    """Skriver en CSV-fil.
    
    Argumenter:
    filnavn -- Beskrivelse
    input -- Beskrivelse
    
    """
    for ix, x in enumerate(input):
        for iy, y in enumerate(x):
            try: 
                input[ix][iy] = y.encode('utf-8')
            except AttributeError:
                pass

    with open(filnavn, "wb") as f:
        f.write(u'\ufeff'.encode('utf-8')) 
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerows(input)