import pandas as pd


def kommuner_fra_api(aar=None, 
                     navn=False,
                     utvalg=None, # antall kommuner, hvis man vil ha et tilfeldig utvalg
                     ):
    """
    Lager liste over kommuner for et gitt aar (eller året vi er i hvis år ikke oppgis).
    navn=True returnerer pandas.DataFrame med kolonnene 'NAVN' og 'KOMMUNENR'.
    """
    
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)
     
    URL = 'https://data.ssb.no/api/klass/v1/classifications/131/codesAt.json?date='+str(aar)+'-01-01'
   
    try:
        df = pd.read_json(URL)
        kommuner = pd.json_normalize(df['codes'])
    except:
        raise ValueError(f"Får ikke lest api-en for {aar}")

    if len(kommuner)==0:
        raise ValueError(f"Finner ikke kommuner for {aar}")
    
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
# navn=True returnerer pandas.DataFrame med kolonnene 'NAVN' og 'FYLKE'.
def fylker_fra_api(aar=None, 
                   navn=False, 
                   utvalg=None,  # antall fylker, hvis man vil ha et tilfeldig utvalg
                   samisk=True):
        
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)

    URL = 'https://data.ssb.no/api/klass/v1/classifications/104/codesAt.json?date='+str(aar)+'-01-01'

    try:
        df = pd.read_json(URL)
        fylker = pd.json_normalize(df['codes'])
    except:
        raise ValueError(f"Får ikke lest api-en for {aar}")
    
    if len(fylker)==0:
        raise ValueError(f"Finner ikke fylker for {aar}")
    
    if navn:
        out = pd.DataFrame(data = {'FYLKE':list(fylker.code), 'NAVN':list(fylker.name)})
        out = out[out["FYLKE"].str.contains("99") == False]             
        if not samisk:
            out["NAVN"] = out["NAVN"].map(lambda x: x.split(" - ")[0].strip(" "))

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


def kommunenavn(kommune=None,
                aar=None):

    """
    Returnerer kommunenavn som string, liste, pandas-kolonne eller ordbok, avhengig av hva som er input.
    kommunenavn() -> ordbok der kommunenumrene er keys og navnene values
    kommunenavn('0301') -> 'Oslo'
    kommunenavn(['3001', 101.0]) -> ['Halden', 'Halden'] 
    kommunenavn(['3001', 101.0], aar=2022) -> ValueError siden '0101' ikke finnes i 2022
    df.FYLKE.kommunenavn() -> pandas-kolonne med kommunenavn
    """

    kommuner = kommuner_fra_api(aar, navn=True)
    
    kommuneordbok = {kommnr: kommnavn for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
    
    if kommune is None:
        return kommuneordbok
    
    # lager funksjon for å ikke gjenta for hver type
    def finn_kommnavn(kommune, kommuneordbok, aar):
        
        kommune = str(int(kommune)).zfill(4)       
        
        if aar is None:
            import datetime
            aar2 = str(datetime.datetime.now().year)
        else:
            aar2 = aar
            
        # let etter kommunen ett år av gangen
        while True:
            
            if kommune in kommuneordbok:
                return kommuneordbok[kommune]
            
            if aar is not None:
                raise ValueError(f"Fant ikke kommunen '{kommune}' i {aar}")
            
            aar2 = int(aar2)-1
            
            try:
                kommuner = kommuner_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke kommunenumret du oppga")
            
            kommuneordbok = {kommnr: kommnavn for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
    
    if isinstance(kommune, str) or isinstance(kommune, int):
        return finn_kommnavn(kommune, kommuneordbok, aar)
    
    elif isinstance(kommune, pd.Series):
        return kommune.map(lambda x: finn_kommnavn(x, kommuneordbok, aar))
    
    elif isinstance(kommune, list) or isinstance(kommune, tuple):
        return [finn_kommnavn(k, kommuneordbok, aar) for k in kommune]
    
    else:
        raise ValueError("'kommune' må være str, int, float, liste, tuple eller pd.Series")


def kommnavn_til_fylknavn(aar=None, samisk=False):
    """ konverterer fra kommunenavn inni fylkesnavn() """
    kommuner = kommuner_fra_api(aar, navn=True)
    fylker = fylker_fra_api(aar, navn=True, samisk=samisk).set_index("FYLKE")
    fylkesnavn = kommuner.KOMMUNENR.str[:2].map(fylker.NAVN)
    return {kommnavn: fylknavn for kommnavn, fylknavn in zip(kommuner.NAVN, fylkesnavn)}


def fylkesnavn(fylke=None, # fylkesnummer (evt. kommunenr) som string, tall, liste eller pandas-kolonne
               aar = None, 
               samisk=False):

    """
    Returnerer fylkesnavn som string, liste, pandas-kolonne eller ordbok, avhengig av hva som er input.
    fylkesnavn() -> ordbok der fylkesnumrene er keys og navnene values
    fylkesnavn('03') -> 'Oslo'
    fylkesnavn(['0101', '3001']) -> ['Østfold', 'Viken'] 
    fylkesnavn(['0101', '3001'], aar=2022) -> ValueError siden 0101 ikke finnes i 2022
    df.FYLKE.fylkesnavn() -> pandas-kolonne med fylkesnavn
    """
    
    fylker = fylker_fra_api(aar, navn=True, samisk=samisk)
    
    fylkesordbok = {fylknr: fylknavn for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
    
    if fylke is None:
        return fylkesordbok
    
    # lager en funksjon for å ikke gjenta for hver type
    def finn_fylknavn(fylke, fylkesordbok, aar):
        
        if aar is None:
            import datetime
            aar2 = str(datetime.datetime.now().year)
        else:
            aar2 = aar
        
        if isinstance(fylke, float):
            fylke = int(fylke)
                
        # let etter fylket ett år av gangen
        while True:
                
            if fylke in fylkesordbok:
                return fylkesordbok[fylke]
            
            # hvis feil format (tall og ikke ledende 0)
            if len(str(fylke))<2:
                try:
                    fylknr = str(int(fylke)).zfill(2)
                    if fylknr in fylkesordbok:
                        return fylkesordbok[fylknr]
                # try/except her fordi int() feiler når man oppgir kommunenavn
                except ValueError:
                    pass
                
            # hvis man oppgir kommunenr
            if len(str(fylke))==3 or len(str(fylke))==4:
                try:
                    fylknr = str(int(fylke)).zfill(4)[:2]
                    if fylknr in fylkesordbok:
                        return fylkesordbok[fylknr]
                except ValueError:
                    pass
            
            # hvis man oppgir kommunenavn
            if str(fylke).capitalize() in kommnavn_til_fylknavn(aar, samisk):
                return kommnavn_til_fylknavn(aar, samisk)[str(fylke).capitalize()]
            
            if aar:
                raise ValueError(f"Fant ikke fylket '{fylke}' i {aar}")
        
            aar2 = int(aar2)-1
            
            try:
                fylker = fylker_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke fylkesnumret du oppga")
            
            # fjerner her samisk navn
            fylkesordbok = {fylknr: fylknavn.split(" - ")[0].strip(" ") for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
                                    
    if isinstance(fylke, str) or isinstance(fylke, int):
        return finn_fylknavn(fylke, fylkesordbok, aar)
        
    elif isinstance(fylke, pd.Series):
        return fylke.map(lambda x: finn_fylknavn(x, fylkesordbok, aar))
    
    elif isinstance(fylke, list) or isinstance(fylke, tuple):
        return [finn_fylknavn(f, fylkesordbok, aar) for f in fylke]
    
    else:
        raise ValueError("'fylke' må være str, int, float, liste, tuple eller pd.Series")


def kommunenummer(kommune=None,
           aar = None):

    """
    Returnerer kommunenummer som string, liste eller ordbok, avhengig av hva som er input
    kommunenummer() -> ordbok der kommunenavnene er keys og numrene values
    kommunenummer('oslo') -> '0301'
    kommunenummer(["andebu", "sandefjord"]) -> ['0719', '3804']
    kommunenummer(["andebu", "sandefjord"], 2022) -> ValueError siden Andebu ikke finnes i 2022
    """
    
    kommuner = kommuner_fra_api(aar, navn=True)
    
    kommuneordbok = {kommnavn: kommnr for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
    
    if kommune is None:
        return kommuneordbok
    
    # lager en funksjon for å ikke gjenta for hver type
    def finn_kommnr(kommune, kommuneordbok, aar):
        
        kommune = kommune.capitalize()
        
        if aar is None:
            import datetime
            aar2 = str(datetime.datetime.now().year)
        else:
            aar2 = aar

        # let etter kommunen ett år av gangen
        while True:
        
            if kommune in kommuneordbok:
                return kommuneordbok[kommune]

            if aar is not None:
                raise ValueError(f"Fant ikke kommunen '{kommune}' i {aar}")
            
            aar2 = int(aar2)-1
            
            try:
                kommuner = kommuner_fra_api(aar2, navn=True)
            except Exception:
                raise ValueError("Finner ikke kommunenumret du oppga")
            
            kommuneordbok = {kommnavn: kommnr for kommnr, kommnavn in zip(kommuner.KOMMUNENR, kommuner.NAVN)}
            
    if isinstance(kommune, str):        
        return finn_kommnr(kommune, kommuneordbok, aar)

    elif isinstance(kommune, list) or isinstance(kommune, tuple):
        return [finn_kommnr(k, kommuneordbok, aar) for k in kommune]
    
    else:
        raise ValueError("'kommune' må være str, liste, tuple eller pd.Series")


def fylkesnummer(fylke=None, # fylkesnavn som string, tall, liste eller tuple
                 aar = None, 
                 samisk=False):

    """
    Returnerer fylkesnummer som string, liste eller ordbok, avhengig av hva som er input
    fylkesnummer() -> ordbok der fylkesnavnene er keys og numrene values
    fylkesnummer('Oslo') -> '03'
    fylkesnummer(["andebu", "sandefjord"]) -> ['07', '38']
    fylkesnummer(["andebu", "sandefjord"], 2022) -> ValueError siden Andebu ikke finnes i 2022
    """

    fylker = fylker_fra_api(aar, navn=True, samisk=samisk)
    fylkesordbok = {fylknavn: fylknr for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}
    
    if fylke is None:
        return fylkesordbok
    
    # lager en funksjon for å ikke gjenta for hver type
    def finn_fylknr(fylke, fylkesordbok, aar):
        
        fylke = fylke.capitalize()

        if aar is None:
            import datetime
            aar2 = str(datetime.datetime.now().year) 
        else:
            aar2 = aar 

        # let etter fylket ett år av gangen
        while True:
            
            if fylke in fylkesordbok:
                return fylkesordbok[fylke]
            
            # hvis man har oppgitt kommunenavn
            try:
                if fylke in kommunenummer(aar=aar2):
                    return kommunenummer(fylke, aar2)[:2]
            except Exception:
                raise ValueError(f"Finner ikke fylket '{fylke}'")

            if aar is not None:
                raise ValueError(f"Finner ikke fylket '{fylke}' i {aar}")

            aar2 = int(aar2)-1
            
            try:
                fylker = fylker_fra_api(aar2, navn=True, samisk=samisk)
            except Exception:
                raise ValueError(f"Finner ikke fylket '{fylke}'")
            
            fylkesordbok = {fylknavn: fylknr for fylknr, fylknavn in zip(fylker.FYLKE, fylker.NAVN)}       
    
    if isinstance(fylke, str):
        return finn_fylknr(fylke, fylkesordbok, aar)
    
    elif isinstance(fylke, list) or isinstance(fylke, tuple):
        return [finn_fylknr(f, fylkesordbok, aar) for f in fylke]
    
    else:
        raise ValueError("'fylke' må være str, liste, tuple eller pd.Series")
