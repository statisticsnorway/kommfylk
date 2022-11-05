import pandas as pd



# Lager liste over kommuner for et gitt aar (eller året vi er i hvis år ikke oppgis).
# med navn=True returnerer DataFrame med kolonnene 'NAVN' og 'KOMMUNENR'.
def kommuner_fra_api(aar=None, 
                     navn=False,
                     utvalg=None, # antall kommuner hvis man vil ha et tilfeldig utvalg
                     ):

    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)
     
    URL = 'http://data.ssb.no/api/klass/v1/classifications/131/codesAt.json?date='+str(aar)+'-01-01'
   
    # Siden dette er json kan vi bruke Pandas.read_json(). Den kan ta nettadresser direkte.
    df = pd.read_json(URL)
        
    kommuner = pd.json_normalize(df['codes'])

    if navn:
        out = pd.DataFrame(data = {'KOMMUNENR':list(kommuner.code), 'NAVN':list(kommuner.name)})
        out = out[out["KOMMUNENR"].str.contains("9999") == False]
    else:
        out = list(kommuner.code)
        out.sort()
        if "9999" in out:
            out.remove("9999")

    if utvalg is not None:
        if navn:
            out = out.sample(utvalg)
        else:
            import random
            out = random.sample(out, utvalg)
            
    return out


            
# Lager liste over fylker for et gitt aar (eller året vi er i hvis år ikke oppgis).
# med navn=True returnerer pd.dataframe med kolonnene 'NAVN' og 'FYLKE'.
def fylker_fra_api(aar=None, navn=False, utvalg=None):
        
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)

    URL = 'http://data.ssb.no/api/klass/v1/classifications/104/codesAt.json?date='+str(aar)+'-01-01'

    df = pd.read_json(URL)

    fylker = pd.json_normalize(df['codes'])

    if navn:
        out = pd.DataFrame(data = {'FYLKE':list(fylker.code), 'NAVN':list(fylker.name)})
        out = out[out["FYLKE"].str.contains("99") == False]
                       
    else:
        out = list(fylker.code.unique())
        out.sort()
        if "99" in out:
            out.remove("99")

    if utvalg is not None:
        if navn:
            out = out.sample(utvalg)
        else:
            import random
            out = random.sample(out, utvalg)

    return out



# returnerer kommunenavn hvis man oppgir kommunenummer (f.eks. returneres "Oslo" hvis man skriver 'kommunenavn("0301")' )
# returnerer kommuneordbok (dict) hvis man ikke spesifiserer kommune. Da kan man skrive kommdict = kommunenavn(), så 'kommdict["0301"]' for å få 'Oslo'
# returnerer liste med kommunenavn hvis man oppgir liste med kommunenumre
def kommunenavn(kommune=None, 
                aar=None):

    if aar is None:
        import datetime
        aar2 = str(datetime.datetime.now().year)
    else:
        aar2 = aar
    
    kommuner = kommuner_fra_api(aar2, navn=True)
    
    kommuneordbok = {kommnr: kommnavn for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
    
    if kommune is None:
        return kommuneordbok

    if isinstance(kommune, float):
        kommune = int(kommune)
        
    # hvis bare én kommune, returner kommunenumret fra ordboka
    if isinstance(kommune, str) or isinstance(kommune, int):
        
        if aar is not None:
            return kommuneordbok[str(kommune).zfill(4)]

        # hvis ikke kommunenumret finnes i kommuneordboka, let gjennom tidligere år fram til man finner den
        while not kommune in kommuneordbok:
            aar2 = int(aar2)-1
            try:
                kommuner = kommuner_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke kommunenumret du oppga")
            kommuneordbok = {kommnr: kommnavn for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
        return kommuneordbok[str(kommune).zfill(4)]

    # hvis man oppgir liste med kommunenumre, returner liste med kommunenavn
    # hvis ikke år er oppgitt, let tilbake til man finner alle kommunenumrene
    if isinstance(kommune, list):
        
        kommune = [str(int(k)).zfill(4) for k in kommune]
        
        if aar is not None:
            return [kommuneordbok[k] for k in kommune]
        if all([i in kommuneordbok for i in kommune]):
            return [kommuneordbok[k] for k in kommune]
        while True:
            aar2 = int(aar2)-1
            try:
                kommuner = kommuner_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke alle kommunenumrene du oppga")
            kommuneordbok = {kommnr: kommnavn for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
            if all([i in kommuneordbok for i in kommune]):
                return [kommuneordbok[k] for k in kommune]



# returnerer fylkesnavn hvis man oppgir kommune- eller fylkesnummer (f.eks. returneres "Oslo" hvis man skriver 'fylkesnavn("0301")' )
# returnerer fylkesordbok (dict) hvis man ikke spesifiserer kommune/fylke. Da kan man skrive fylkdict = fylkesnavn(), så 'fylkdict["03"]' for å få 'Oslo'
def fylkesnavn(fylke=None, aar = None, samisk=False):

    if aar is None:
        import datetime
        aar2 = str(datetime.datetime.now().year)
    else:
        aar2 = aar
    
    fylker = fylker_fra_api(aar2, navn=True)
    
    # funksjon som lager kommuneordbok med eller uten samiske navn
    def fylkesdict(fylker, samisk):
        if samisk:
            return {fylknr: fylknavn for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
        return {fylknr: fylknavn.split("-")[0].strip(" ") for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
    
    fylkesordbok = fylkesdict(fylker, samisk)
    
    if fylke is None:
        return fylkesordbok
    
    if isinstance(fylke, float):
        fylke = int(fylke)
    
    # hvis man oppgir kommunenr
    def komm_til_fylk(aar):
        kommuner = kommuner_fra_api(aar, navn=True)
        kommuner["FYLKE"] = kommuner.KOMMUNENR.str[:2]
        return {kommnavn: fylknr for fylknr, kommnavn in zip(kommuner.FYLKE, kommuner.NAVN)}
    
    # hvis bare ett fylke, returner fylkesnumret fra ordboka
    if isinstance(fylke, str) or isinstance(fylke, int):
        
        if str(fylke).capitalize() in komm_til_fylk(aar2):
            return komm_til_fylk(aar2)[fylke]
            
        fylke = str(fylke)[:2].zfill(2)
        
        if aar is not None:
            return fylkesordbok[fylke]

        # hvis ikke fylkesnumret finnes i fylkesordboka, let gjennom tidligere år fram til man finner det
        while not fylke in fylkesordbok:
            aar2 = int(aar2)-1
            try:
                fylker = fylker_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke fylkesnumret du oppga")
            fylkesordbok = fylkesdict(fylker, samisk)
            
            if str(fylke).capitalize() in komm_til_fylk(aar2):
                return komm_til_fylk(aar2)[fylke]
        
        return fylkesordbok[fylke]

    # hvis man oppgir flere fylkenumre, returner liste med fylkesnavn
    # hvis ikke år er oppgitt, let tilbake til man finner alle fylkenumrene
    if isinstance(fylke, list) or isinstance(fylke, tuple):
        
        fylke = [str(f)[:2].zfill(2) for f in fylke]
        
        if aar is not None or all([f in fylkesordbok for f in fylke]):
            return [fylkesordbok[f] for f in fylke]
        
        # let etter fylkesnumrene så langt api-en rekker
        while True:
            aar2 = int(aar2)-1
            try:
                fylker = fylker_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke alle fylkenumrene du oppga")
            fylkesordbok = fylkesdict(fylker, samisk)
            if all([f in fylkesordbok for f in fylke]):
                return [fylkesordbok[f] for f in fylke]



def kommunenummer(kommune=None, 
                aar=None):

    if aar is None:
        import datetime
        aar2 = str(datetime.datetime.now().year)
    else:
        aar2 = aar
    
    kommuner = kommuner_fra_api(aar2, navn=True)
    
    kommuneordbok = {kommnavn: kommnr for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
    
    if kommune is None:
        return kommuneordbok
        
    # hvis bare én kommune, returner kommunenumret fra ordboka
    if isinstance(kommune, str):
        
        kommune = kommune.capitalize()
        
        if aar is not None:
            return kommuneordbok[kommune]

        # hvis ikke kommunenumret finnes i kommuneordboka, let gjennom tidligere år fram til man finner den
        while not kommune in kommuneordbok:
            aar2 = int(aar2)-1
            try:
                kommuner = kommuner_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke kommunenumret du oppga")
            kommuneordbok = {kommnavn: kommnr for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
        return kommuneordbok[kommune]

    # hvis man oppgir liste med kommunenumre, returner liste med kommunenavn
    # hvis ikke år er oppgitt, let tilbake til man finner alle kommunenumrene
    if isinstance(kommune, list):
        
        kommune = [k.capitalize() for k in kommune]

        if aar is not None:
            return [kommuneordbok[k] for k in kommune]
        if all([i in kommuneordbok for i in kommune]):
            return [kommuneordbok[k] for k in kommune]
        while True:
            aar2 = int(aar2)-1
            try:
                kommuner = kommuner_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke alle kommunenumrene du oppga")
            kommuneordbok = {kommnavn: kommnr for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
            if all([i in kommuneordbok for i in kommune]):
                return [kommuneordbok[k] for k in kommune]



def fylkesnummer(fylke=None, 
                aar=None):
    
    if aar is None:
        import datetime
        aar2 = str(datetime.datetime.now().year)
    else:
        aar2 = aar

    fylker = fylker_fra_api(aar, navn=True)
    fylkesordbok = {fylknavn: fylknr for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
    
    if fylke is None:
        return fylkesordbok
    
    # hvis bare ett fylke, returner fylkenumret fra ordboka
    if isinstance(fylke, str):
        
        fylke = fylke.capitalize()
        
        if aar is not None:
            if fylke in fylkesordbok:
                return fylkesordbok[fylke]
            if fylke in kommunenummer(aar=aar2):
                return kommunenummer(fylke, aar2)[:2]

        # hvis ikke fylkenumret finnes i fylkesordboka, let gjennom tidligere år fram til man finner den
        while not fylke in fylkesordbok:
            
            if fylke in fylkesordbok:
                return fylkesordbok[fylke]
            
            if fylke in kommunenummer(aar=aar2):
                return kommunenummer(fylke, aar2)[:2]
                   
            aar2 = int(aar2)-1
            
            try:
                fylker = fylker_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke fylkenumret du oppga")
            
            fylkesordbok = {fylknavn: fylknr for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
            

    # hvis man oppgir liste med fylkesnumre, returner liste med fylkenavn
    # hvis ikke år er oppgitt, let tilbake til man finner alle fylkenumrene
    if isinstance(fylke, list):
        
        fylke = [f.capitalize() for f in fylke]
        
        if aar is not None:
            if all([f in fylkesordbok for f in fylke]):
                return [fylkesordbok[f] for f in fylke]
            elif all([f in kommunenummer(aar=aar2) for f in fylke]):
                return [kommunenummer(f, aar2)[:2] for f in fylke]
        
        while True:
            
            if all([f in fylkesordbok for f in fylke]):
                return [fylkesordbok[f] for f in fylke]
            
            if all([f in kommunenummer(aar=aar2) for f in fylke]):
                return [kommunenummer(f, aar2)[:2] for f in fylke]
            
            aar2 = int(aar2)-1
            
            try:
                fylker = fylker_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke alle fylkenumrene du oppga")
            
            fylkesordbok = {fylknavn: fylknr for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}

            