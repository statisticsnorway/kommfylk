import geopandas as gpd


# TODO: legg ut kommunedata på dapla 
def les_geoparquet(sti):
    pass


def nabokommuner(kommune=None,
                 aar=None):
    
    """
    Lager ordbok (dict) der f.eks. nabodict["0301"] gir en liste over Oslos nabokommuner
    Hvis kommune er spesifisert, returneres liste med nabokommuner    nabokommuner("0301", 2017) -> ['0213', '0229', '0217', '0219', '0605', '0230', '0231', '0233', '0533']
    """
    
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)
        
    abas = gpd.read_file(r"C:\Users\ort\OneDrive - Statistisk sentralbyrå\data\Basisdata_0000_Norge_25833_Kommuner_FGDB.gdb", 
                         layer="kommune")
    abas["KOMMUNENR"] = abas.kommunenummer

    if kommune:
        
        #spatial join mellom kommunen og alle andre andre kommuner
        kommunen = abas.loc[abas.KOMMUNENR == kommune, ["geometry"]]
        andre_kommuner = abas.loc[abas.KOMMUNENR != kommune, ["KOMMUNENR", "geometry"]]
        joinet = kommunen.sjoin(andre_kommuner)
        
        return list(joinet.KOMMUNENR.unique())

    # hvis ikke kommune er oppgitt, lag ordbok med kommunene som keys og naboene som values
    nabodict = {}
    for kommune in abas.sort_values("KOMMUNENR").KOMMUNENR:
            
        #spatial join mellom kommunen og alle andre andre kommuner
        kommunen = abas.loc[abas.KOMMUNENR == kommune, ["geometry"]]
        andre_kommuner = abas.loc[abas.KOMMUNENR != kommune, ["KOMMUNENR", "geometry"]]
        joinet = kommunen.sjoin(andre_kommuner)

        # gjør liste over kommunenumre til value og kommunen til key
        naboer = list(joinet.KOMMUNENR.unique())
        nabodict[kommune] = naboer

    return nabodict

