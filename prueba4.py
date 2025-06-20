import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

# 1. Carga original y asigna CRS UTM ETRS89 / zona 29N (EPSG:25829)
gdf = gpd.read_file("Geographic_data/Concellos_IGN.shp", encoding="utf-8")
gdf = gdf.set_crs(epsg=25829, inplace=False)

# 2. Reproyecta a Web Mercator (EPSG:3857) para trabajar en metros
gdf = gdf.to_crs(epsg=3857)

# 3. Repara geometrías defectuosas y elimina vacías
gdf["geometry"] = gdf.geometry.buffer(0)
gdf = gdf.loc[~gdf.geometry.is_empty].copy()

# 4. Spatial join para quedarnos sólo con concellos que tocan
touches = gpd.sjoin(gdf, gdf, how="inner", predicate="touches")

# 5. Construye el grafo completo (nodos = nombre de concello)
G = nx.from_pandas_edgelist(
    touches,
    source="NAMEUNIT_left",
    target="NAMEUNIT_right"
)

# 6. Centroides → posiciones reales (diccionario: nombre → (x,y))
gdf["centroid"] = gdf.geometry.centroid
pos = gdf.set_index("NAMEUNIT")["centroid"].apply(lambda p: (p.x, p.y)).to_dict()

# 7. Dibuja el contorno de Galicia como fondo
fig, ax = plt.subplots(figsize=(24, 24))
gdf.boundary.plot(ax=ax, linewidth=0.5, color="gray")

# 8. Superpone las aristas del grafo
nx.draw_networkx_edges(
    G, pos, ax=ax,
    edge_color="black",
    alpha=0.5,
    width=0.8
)

# 9. Dibuja nodos con tamaño proporcional al grado
node_sizes = [50 + 10 * G.degree(n) for n in G.nodes()]
nx.draw_networkx_nodes(
    G, pos, ax=ax,
    node_size=node_sizes,
    node_color="red",
    alpha=0.7
)

# 10. Añade etiquetas de nombre (puedes omitirlas o filtrar por grado)
nx.draw_networkx_labels(
    G, pos, ax=ax,
    font_size=6
)

# 11. Estética final
ax.set_title("Grafo de concellos limítrofes sobre el mapa de Galicia", fontsize=14)
ax.set_axis_off()
plt.tight_layout()
plt.show()

import json

# 1. Extrae lista ordenada de nombres únicos
all_names = sorted(gdf["NAMEUNIT"].unique())

# 2. Asigna un ID numérico a cada nombre
name_to_id = {name: idx+1 for idx, name in enumerate(all_names)}

# 3. Para cada concello, recoge sus vecinos según el DataFrame 'touches'
#    (es el resultado del sjoin con predicate="touches")
concellos = {}
for name in all_names:
    cid = name_to_id[name]
    # vecinos por nombre
    neigh_names = touches.loc[
        touches["NAMEUNIT_left"] == name,
        "NAMEUNIT_right"
    ].unique()
    # conviértelos a IDs y ordénalos
    vecinos_ids = sorted(name_to_id[n] for n in neigh_names)
    concellos[cid] = {
        "nombre": name,
        "vecinos": vecinos_ids
    }

# 4. Guarda a JSON (opcional)
with open("concellos_vecinos.json", "w", encoding="utf-8") as f:
    json.dump(concellos, f, ensure_ascii=False, indent=2)

# 5. (Opcional) Imprime un ejemplo
print(json.dumps({k: concellos[k] for k in range(1,6)}, ensure_ascii=False, indent=2))
