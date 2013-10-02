# -*- coding: utf-8 -*-

import logging
from nvdb import query
from nvdb import query_search
from nvdb import csv_skriv
from nvdb import Objekt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

objekttyper = [{'id': 581, 'antall': 10000}]
lokasjon = {'fylke': [17]}
tunneler = query_search(objekttyper, lokasjon)

csv_list = []

tunnel_nr = 0
for tunnel in tunneler.objekter():

    tunnel_nr += 1
    logger.info('Bearbeider tunnel %s av %s' % (tunnel_nr, tunneler.antall))
    tunnel = Objekt(tunnel)
    
    row = {
        'lengde': 0,
        'ulykker': 0,
        'drept': 0,
        'meget_alvorlig_skadd': 0,
        'alvorlig_skadd': 0,
        'lettere_skadd': 0,
        'sum': 0
    }
    veglenker = []

    try:
        tunnel.assosiasjoner(67)
    except KeyError:
        logger.warning('Tunnel (# %s) har ingen tunnelløp' % tunnel.id)
    else:
        for i in tunnel.assosiasjoner(67):
            try:
                tunnellop = Objekt(query(i['relasjon']['uri']))
            except Exception, e:
                logger.error('Tunnel (# %s) har referanse til tunnelløp som '
                             'ikke er tilgjengelig: %s' % (tunnel.id, e))
            else:
                row['lengde'] += tunnellop.lengde()
                
                if tunnellop.veglenker() not in veglenker:
                    veglenker += tunnellop.veglenker()
    if veglenker:
        objekttyper = [{
            'id': 570, 
            'antall': 10000
        }]
        lokasjon = {'veglenker': veglenker}
        trafikkulykker = query_search(objekttyper, lokasjon)
            
        if trafikkulykker.antall > 0:
            for trafikkulykke in trafikkulykker.objekter():
                trafikkulykke = Objekt(trafikkulykke)
                row['ulykker'] += 1
                row['drept'] += int(trafikkulykke.egenskap(5070, verdi=0))
                row['meget_alvorlig_skadd'] += int(trafikkulykke.egenskap(5071, verdi=0))
                row['alvorlig_skadd'] += int(trafikkulykke.egenskap(5072, verdi=0))
                row['lettere_skadd'] += int(trafikkulykke.egenskap(5073, verdi=0))
    else:
        logger.warning('Tunnel (# %s) har ingen veglenker' % tunnel.id)
                
    try:
        tunnelnavn = tunnel.egenskap(5225)
        skiltet_lengde = tunnel.egenskap(8945)
        parallelle_lop = tunnel.egenskap(3947)
    except KeyError:
        logger.error('Tunnel (# %s) har ingen egenskaper' % tunnel.id)
        skiltetlengde = None
        tunnelnavn = None
        antlop = None
    
    fylke = tunnel.lokasjon('fylke')
    kommune = tunnel.lokasjon('kommune')
    
    row['sum'] = (row['drept'] + row['meget_alvorlig_skadd'] + 
                  row['alvorlig_skadd'] + row['lettere_skadd'])

    csv_row = [
        tunnelnavn, fylke, kommune, skiltet_lengde, int(row['lengde']), 
        parallelle_lop, row['ulykker'], row['drept'], 
        row['meget_alvorlig_skadd'], row['alvorlig_skadd'], 
        row['lettere_skadd'], row['sum']
    ]
    csv_list.append(csv_row)
    
csv_header = [
    'Tunnelnavn', 'Fylke', 'Kommune', 'Skiltet lengde', 'Total lengde', 
    'Antall parallelle hovedlop', 'Antall ulykker', 'Antall drept', 
    'Antall meget alvorlig skadd', 'Antall alvorlig skadd', 
    'Antall lettere skadd', 'Sum drept og skadd'
] 
csv_list.insert(0, csv_header)

csv_skriv('tunneler_med_ulykker.csv', csv_list)
