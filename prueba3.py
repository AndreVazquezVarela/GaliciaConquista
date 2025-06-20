import geopandas as gpd

# Cargar el shapefile de los concellos
concellos = gpd.read_file('Geographic_data/Concellos_IGN.shp', encoding='utf-8')

print(concellos.head())


primer = concellos.iloc[0]
print(primer)

concellos = gpd.read_file('Geographic_data/Comarcas.shp', encoding='utf-8')

print(concellos.head())


primer = concellos.iloc[0]
print(primer)