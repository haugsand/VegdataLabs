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
        'pe_skum': None,
        'pe_skum_lengde': 0,
        'pe_skum_reg_lengde': 0,
        'pe_skum_reg_areal': 0
    }
     
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
                try:
                    tunnellop.assosiasjoner(70)
                except KeyError:
                    pass
                else:
                    for j in tunnellop.assosiasjoner(70):
                        try:
                            frostsikring = Objekt(query(j['relasjon']['uri']))
                        except Exception, e:
                            logger.error('Tunnelløp (# %s) har referanse til et objekt '
                                         'som ikke er tilgjengelig: %s' % (tunnel.id, e))
                        else:
                            try:
                                frostsikring.egenskaper()
                            except KeyError:
                                logger.warning('Vann- og frostsikring (# %s) '
                                'har ingen egenskaper' % frostsikring.id)
                            else:
                                if frostsikring.egenskap(1132, enum=12281):
                                    row['pe_skum'] = 'Ja'
                                    row['pe_skum_lengde'] += frostsikring.lengde()
                                    row['pe_skum_reg_lengde'] += float(frostsikring.egenskap(7543, verdi=0))
                                    row['pe_skum_reg_areal'] += int(frostsikring.egenskap(9307, verdi=0))
                                    logger.debug(row)
    try:
        tunnelnavn = tunnel.egenskap(5225)
    except KeyError, e:
        logger.warning('Tunnel (# %s) har ingen egenskaper' % tunnel.id)
        tunnelnavn = None
        
    fylke = tunnel.lokasjon('fylke')
    kommune = tunnel.lokasjon('kommune')
        
    # Legger til en rad per tunnel
    csv_row = [
        tunnelnavn, fylke, kommune, int(row['lengde']), row['pe_skum'], 
        int(row['pe_skum_lengde']), float(row['pe_skum_reg_lengde']), 
        int(row['pe_skum_reg_areal'])
    ]
    csv_list.append(csv_row)
    
csv_header = [
    'Tunnelnavn', 'Fylke', 'Kommune', 'Total lengde', 'Utildekket PE-skum', 
    'Lengde med PE-skum', 'Registrert lengde', 
    'Registrert areal'
] 
csv_list.insert(0, csv_header)

csv_skriv('tunneler_med_utildekket_peskum.csv', csv_list)
