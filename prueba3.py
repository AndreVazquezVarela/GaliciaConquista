import geopandas as gpd

# Cargar el shapefile de los concellos
concellos = gpd.read_file('Comarcas.shp', encoding='utf-8')

print(concellos['Comarca'])


