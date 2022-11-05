import geopandas as gpd


def les_geoparquet(sti):
#    import dapla as dp
    return gpd.read_file(sti)


# deler en geodataframe i kommuner for et gitt år med intersection.
# hvis kolonnen KOMMUNENR finnes fra før, endres navnet til KOMMUNENR_opprinnelig.
def del_i_kommuner(gdf: gpd.GeoDataFrame, 
                   aar=None, 
                   intersect=True
                   ) -> gpd.GeoDataFrame:

    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)      
          
    abas = les_geoparquet(r"C:\ESTP\Data\ESTP\Day1\Municipalities_2017.shp")

    abas = abas[["KOMMUNENR", "geometry"]]
    
    if "KOMMUNENR" in gdf.columns:
        gdf = gdf.rename(columns = {'KOMMUNENR':'KOMMUNENR_opprinnelig'})

    if intersect:
        out = gdf.overlay(abas, how="intersection", keep_geom_type=True)
    else:
        out = gdf.sjoin(abas)

    #fjern tomme geometrier
    til_fjerning = [i for i in out.index
                    if out[out.index==i].geometry.values[0] is None
                    or out[out.index==i].geometry.is_empty[i]]
    out = out[~out.index.isin(til_fjerning)]
            
    return out.reset_index(drop=True)


#samme for fylker
def del_i_fylker(gdf: gpd.GeoDataFrame, 
                 aar=None, 
                 intersect=True
                 ) -> gpd.GeoDataFrame:
    
    if aar is None:
        import datetime
        aar = str(datetime.datetime.now().year)

    abas = les_geoparquet(r"C:\ESTP\Data\ESTP\Day1\Counties_Poly.shp")
    abas["FYLKE"] = abas.County_nr
    
    abas = abas[["FYLKE", "geometry"]]
    if "FYLKE" in gdf.columns:
        gdf = gdf.rename(columns = {'FYLKE':'FYLKE_opprinnelig'})
    if intersect:
        out = gdf.overlay(abas, how="intersection", keep_geom_type=True)
    else:
        out = gdf.sjoin(abas)
    #fjern tomme geometrier
    til_fjerning = [i for i in out.index
                    if out[out.index==i].geometry.values[0] is None
                    or out[out.index==i].geometry.is_empty[i]]
    out = out[~out.index.isin(til_fjerning)]
    return out.reset_index(drop=True)
