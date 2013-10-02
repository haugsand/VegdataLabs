# -*- coding: utf-8 -*-

import logging
from nvdb_utv import query_search
from nvdb import ObjektType
from nvdb import EgenskapsType
from nvdb import andel 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

objekttype = ObjektType(input("Skriv inn objekttypeid: "))
print objekttype.navn+' (id: %s)' % objekttype.id

objekttyper = [{'id': objekttype.id, 'antall':1}]
antall_objekt = query_search(objekttyper).antall
print 'Antall forekomster: %s' % antall_objekt

for egenskapstype in objekttype.egenskapstyper:
    egenskapstype = EgenskapsType(egenskapstype)
        
    objekttyper = [{
        'id': objekttype.id, 'antall':1, 
        'filter': [{
            'typeId': egenskapstype.id,
            'operator': '!=',
            'verdi': [None]
        }]
    }]
    antall_egenskap = query_search(objekttyper).antall
    prosent = andel(antall_egenskap, antall_objekt)
    print '- %s: %s (%s %%)' % (egenskapstype.navn, antall_egenskap, prosent)
    
    try:
        egenskapstype.enum()
    except KeyError:
        pass
    else: 
        for enum in egenskapstype.enum():
            verdi = egenskapstype.enum()[enum]['verdi']
            objekttyper = [{
                'id': objekttype.id, 'antall':1, 
                'filter': [{
                    'typeId': egenskapstype.id,
                    'operator': '=',
                    'verdi': [verdi]
                }]
            }]
            antall_enum = query_search(objekttyper).antall
            prosent = andel(antall_enum, antall_egenskap)
            print '-- %s: %s (%s %%)' % (verdi, antall_enum, prosent)
