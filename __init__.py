from kommfylk.fra_api import (
    kommuner_fra_api,
    fylker_fra_api,
    kommunenavn,
    fylkesnavn,
    kommunenummer,
    fylkesnummer,
    kommnavn_til_fylknavn
)

from kommfylk.nabokommuner import nabokommuner

from kommfylk.del_gdf import del_i_kommuner, del_i_fylker

from pandas.core.base import PandasObject
PandasObject.del_i_fylker = del_i_fylker
PandasObject.del_i_kommuner = del_i_kommuner

PandasObject.kommunenavn = kommunenavn
PandasObject.fylkesnavn = fylkesnavn