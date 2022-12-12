import geopandas as gpd
import pandas as pd

def les_geoparquet(sti):
#    import dapla as dp
    return gpd.read_file(sti)


# deler en geodataframe i kommuner for et gitt år med intersection.
# hvis kolonnen KOMMUNENR finnes fra før, endres navnet til KOMMUNENR_opprinnelig.
def del_i_kommuner(gdf: gpd.GeoDataFrame, 
                   aar=None, *,
                   intersect=True,
                   loop: int = None
                   ) -> gpd.GeoDataFrame:

    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)      
          
    abas = gpd.read_file(r"C:\Users\ort\OneDrive - Statistisk sentralbyrå\data\Basisdata_0000_Norge_25833_Kommuner_FGDB.gdb", 
                         layer="kommune")
    abas["KOMMUNENR"] = abas.kommunenummer
    
    abas = abas[["KOMMUNENR", "geometry"]]
    
    gdf2 = gdf.drop("KOMMUNENR", axis=1, errors="ignore")
    gdf2 = gdf2.loc[:, ~gdf2.columns.str.contains("index|level_")]
    
    if loop:
#        for i in loop:
        delt = pd.DataFrame()
        for i, kommnr in enumerate(abas.KOMMUNENR.unique()):
            abas_komm = abas[abas.KOMMUNENR==kommnr]
            if intersect:
                delt_komm = gdf2.overlay(abas_komm, how="intersection", keep_geom_type=True)
            else:
                delt_komm = gdf2.sjoin(abas_komm)
            delt = gpd.GeoDataFrame(pd.concat([delt, delt_komm], axis=0, ignore_index=True), geometry="geometry", crs=gdf.crs)
            print(f"Ferdig med {i+1} av {len(abas)}", end="\r")
    else:
        if intersect:
            delt = gdf2.overlay(abas, how="intersection", keep_geom_type=True)
        else:
            delt = gdf2.sjoin(abas)
        
    delt = delt.reset_index(drop=True)
    delt = delt.loc[:, ~delt.columns.str.contains("index|level_")]

    #fjern tomme geometrier
    delt = delt[~delt.geometry.is_empty]
    delt = delt.dropna(subset = ["geometry"])
            
    return delt


#samme for fylker
def del_i_fylker(gdf: gpd.GeoDataFrame, 
                 aar=None, 
                 intersect=True
                 ) -> gpd.GeoDataFrame:
    
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)

    abas = gpd.read_file(r"C:\Users\ort\OneDrive - Statistisk sentralbyrå\data\Basisdata_0000_Norge_25833_Fylker_FGDB.gdb", 
                         layer="fylke")
    abas["FYLKE"] = abas.fylkesnummer
    
    abas = abas[["FYLKE", "geometry"]]
    
    gdf2 = gdf.drop("FYLKE", axis=1, errors="ignore")
    gdf2 = gdf2.loc[:, ~gdf2.columns.str.contains("index|level_")]

    if intersect:
        delt = gdf2.overlay(abas, how="intersection", keep_geom_type=True)
    else:
        delt = gdf2.sjoin(abas)
    
    delt = delt.reset_index(drop=True)
    delt = delt.loc[:, ~delt.columns.str.contains("index|level_")]

    #fjern tomme geometrier
    delt = delt[~delt.geometry.is_empty]
    delt = delt.dropna(subset = ["geometry"])
    
    return delt
