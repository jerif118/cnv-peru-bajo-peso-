# ubigeo_distrito.csv

Fuente: Jesús M. Castagnetto, *ubigeo-peru-aumentado* (licencia MIT; el repositorio tiene DOI en Zenodo, citar la versión usada).
https://github.com/jmcastagnetto/ubigeo-peru-aumentado

Una fila por distrito con código INEI, macrorregión, altitud (msnm), IDH 2019, % de pobreza total y extrema e índice de vulnerabilidad alimentaria. El notebook 01 la carga como `raw.ubigeo_distrito_referencia` y la une por `IdUbigeoInei` (coincide en el 99.98 % de los registros).

# peru_provincial_simple.geojson y peru_departamental_simple.geojson

Fuente: Juan Eladio Sánchez Rosas, *peru-geojson* (Mozilla Public License 2.0).
https://github.com/juaneladio/peru-geojson

Límites simplificados de 197 provincias (`FIRST_IDPR` = código INEI de 4 dígitos) y 25 departamentos (`FIRST_IDDP`). El notebook 06 los usa para los mapas. Putumayo (1608, creada en 2014) no tiene polígono propio: queda dentro de Maynas (1601).
