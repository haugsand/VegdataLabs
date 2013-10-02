    
def lag(sted, vegkategori, navn):
    api = 'http://vegnett.vegdata.no/nvdb/api/vegnett/'
    uri = api+sted+'.json?kategori='+vegkategori
    
    lag = QgsVectorLayer(uri, navn, "ogr")
    QgsMapLayerRegistry.instance().addMapLayer(lag)


def lag_kategorier(sted, navn):
    vegkategorier = ['e', 'r', 'f', 'k', 'p', 's']
    
    for kategori in vegkategorier:
        lag(sted, kategori, navn+' '+kategori)