# -*- coding: utf-8 -*-

import json
import requests
import csv

class Objekttyper:
    """Klasse som håndterer en liste med objekttyper:
    https://www.vegvesen.no/nvdb/api/dokumentasjon/datakatalog
    
    """
    
class ObjektType:
    """Klasse som håndterer en enkelt objekttype:
    https://www.vegvesen.no/nvdb/api/dokumentasjon/datakatalog/{objekttypeid}
    
    """
    
    def __init__(self, objekttype_id):
        self.data = query('/datakatalog/objekttyper/%s' % objekttype_id)
        self.id = objekttype_id
        self.navn = self.data['navn']
        self.egenskapstyper = self.data['egenskapsTyper']
        
        
class EgenskapsType:
    """Klasse som håndterer en egenskapstype:
    https://www.vegvesen.no/nvdb/api/dokumentasjon/datakatalog/{objekttypeid}
        
    """

    def __init__(self, data):
        self.data = data
        self.id = self.data['id']
        self.navn = self.data['navn']
        
    def enum(self):
        return self.data['enumVerdier']


class Objekt:
    """Klasse som håndterer ett vegobjekt med den strukturen som leveres
    gjennom NVDB API: 
    https://www.vegvesen.no/nvdb/api/dokumentasjon/vegobjekter
    
    """
   
    def __init__(self, data):
        self.data = data 
        self.id = data['objektId']
        
    def veglenker(self):
        """Returnerer veglenker"""
        
        veglenker = []
        for veglenke in self.data['lokasjon']['veglenker']:            
            veglenkerad = {
                'id': veglenke['id'],
                'fra': veglenke['fra'], 
                'til': veglenke['til']
            }
        veglenker.append(veglenkerad)        
        return veglenker
            
    def lengde(self):
        """Returnerer utledet lengde for et strekningsobjekt"""
        return self.data['strekningslengde']
        
    def egenskaper(self):
        """Returnerer alle egenskaper"""
        return self.data['egenskaper']
                
    def egenskap(self, egenskapstype, enum='', verdi=''):
        """ Returnerer verdien til en valgt egenskapstype.
        
        Argumenter:
        egenskapstype -- id på egenskapstype, angitt i datakatalogen
        enum -- id på enum-verdi på valgt egenskapstype (default: '')
        verdi -- verdi som returneres når egenskapen ikke finnes (default: '')
        
        """
        
        for egenskap in self.data['egenskaper']:
            if egenskap['id'] == egenskapstype:
                if not enum:
                    verdi = egenskap['verdi']
                elif enum and egenskap['enumVerdi']['id'] == enum:
                    verdi = egenskap['verdi']
        return verdi
        
    def lokasjon(self, omradetype):
        """Returnerer navnet på en angitt områdetype, for eksempel kommune
        
        Argumenter:
        omradetype: navn på den områdetypen som skal returneres
        
        """
        return self.data['lokasjon'][omradetype]['navn']
        
    def assosiasjoner(self, objekttype=''):
        """ Returnerer alle assosiasjoner til objektet, eller alle 
        assosiasjoner til en angitt objekttype.
        
        Argumenter:
        objekttype -- (default: '')
        
        """
        
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
    """En liste med NVDB-objekter. Får sikkert bruk for denne senere"""
    
class Resultat:
    """Klasse som håndterer den responsen som blir returnert ved å bruke
    NVDB APIets søkegrensesnitt:
    https://www.vegvesen.no/nvdb/api/dokumentasjon/sok
    
    Støtter foreløpig bare søk som returnerer én objekttype
     
    """
    
    def __init__(self, data):
        self.data = data
        self.antall = data['resultater'][0]['statistikk']['antallFunnet']
        
    def objekter(self):
        """Returnerer en liste med NVDB-objekter"""
        return self.data['resultater'][0]['vegObjekter']

def query(path, params=''):
    """Leverer data fra NVDB APIet på JSON-format:
    https://www.vegvesen.no/nvdb/api/
    
    Argumenter:
    path -- Sti bak adresse til NVDB API
    params -- Parametere (default: '')
    
    """
    
    api = 'https://www.vegvesen.no/nvdb/api'
    
    url = api+path
    headers = {'accept': 'application/vnd.vegvesen.nvdb-v1+json'}
    
    r = requests.get(url, headers=headers, params=params, verify=False)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        raise Exception('Feil ved henting av '+r.url+': '+str(r.status_code))

def query_search(objekttyper, lokasjon=''):
    """Leverer en instans av klassen Resultat etter en spørring
    mot NVDB APIets søkegrensesnitt:
    https://www.vegvesen.no/nvdb/api/dokumentasjon/sok/
    
    Argumenter:
    objekttyper -- En liste ned objekttyper
    lokasjon -- En dictionary med lokasjoner (default: '')
    
    """
    sokobjekt = {}
    if lokasjon:
        sokobjekt['lokasjon'] = lokasjon
    sokobjekt['objektTyper'] = objekttyper
                
    return Resultat(query('/sok', {'kriterie': json.dumps(sokobjekt)}))
    
def csv_skriv(filnavn, input):
    """Skriver innholdet i en liste med lister til en csv-fil.
    
    Argumenter:
    filnavn -- navn på fil som skal opprettes
    input -- liste med lister
    
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

def andel(a,b):

    return round((a / float(b)),3)*100