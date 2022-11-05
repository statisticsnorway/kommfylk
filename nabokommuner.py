import geopandas as gpd


# TODO: legg ut kommunedata på dapla 


def les_geoparquet(sti):
#    import dapla as dp
    return gpd.read_file(sti)


# lager ordbok (dict) der f.eks. nabodict["0301"] gir en liste over Oslos nabokommuner
# returnerer liste med nabokommuner (kommunenumre) for en gitt kommune. f.eks. gir nabokommuner("0301") en liste over Oslos nabokommuner

def nabokommuner(kommune=None, 
                 aar=None):
    
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)
        
    abas = les_geoparquet(r"C:\ESTP\Data\ESTP\Day1\Municipalities_2017.shp")

    if kommune is not None:
        
        #spatial join mellom kommunen og alle andre andre kommuner
        kommunen = abas.loc[abas.KOMMUNENR == kommune, ["geometry"]]
        andre_kommuner = abas[abas.KOMMUNENR != kommune]
        joinet = kommunen.sjoin(andre_kommuner)
        
        return list(joinet.KOMMUNENR.unique())

    #lag nabodict
    nabodict = {}
    for kommune in abas.sort_values("KOMMUNENR").KOMMUNENR:
            
        #spatial join mellom kommunen og alle andre andre kommuner
        kommunen = abas.loc[abas.KOMMUNENR == kommune, ["geometry"]]
        andre_kommuner = abas[abas.KOMMUNENR != kommune]
        joinet = kommunen.sjoin(andre_kommuner)

        # gjør liste over unike kommunenumre til value og kommunen til key
        naboer = list(joinet.KOMMUNENR.unique())
        nabodict[kommune] = naboer

    return nabodict

