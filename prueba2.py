import random

import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt

# Crear los concellos con identificadores únicos y nombres originales
concellos = {
    50: {'nombre': 'Coristanco', 'vecinos': [40, 88, 35, 26, 97, 16]},
    26: {'nombre': 'Zas', 'vecinos': [35, 61, 25, 97, 50, 66]},
    25: {'nombre': 'Vimianzo', 'vecinos': [61, 37, 73, 55, 66, 26]},
    73: {'nombre': 'Muxía', 'vecinos': [37, 25, 55, 44]},
    44: {'nombre': 'Cee', 'vecinos': [58, 49, 55, 73]},
    58: {'nombre': 'Fisterra', 'vecinos': [44]},
    49: {'nombre': 'Corcubión', 'vecinos': [44]},
    55: {'nombre': 'Dumbría', 'vecinos': [44, 73, 25, 66, 74]},
    66: {'nombre': 'Mazaricos', 'vecinos': [55, 25, 26, 97, 77, 83, 74]},
    74: {'nombre': 'Carnota', 'vecinos': [66, 74, 55]},

}

# Inicializar el grafo
G = nx.Graph()

# Añadir nodos y aristas al grafo, con nombre y nombre_original como atributos
for id_concello, datos in concellos.items():
    G.add_node(id_concello, nombre=datos["nombre"], nombre_original=datos["nombre"])
    for vecino in datos["vecinos"]:
        G.add_edge(id_concello, vecino)

galicia_map = gpd.read_file("Geographic_data/Concellos_IGN.shp", encoding ="utf-8")




# Visualizar el mapa básico de Galicia con los concellos
plt.figure(figsize=(20, 20))
galicia_map.plot(edgecolor="black", linewidth=0.1, color="white")



'''for idx, row in galicia_map.iterrows():
    # Calcular el centroide de la provincia
    centroid = row['geometry'].centroid
    # Obtener el nombre de la provincia
    nombre_provincia = row['CONCELLO']  # Ajusta 'Provincia' según el nombre correcto de la columna

    # Anotar el nombre de la provincia en el centroide
    plt.annotate(text =nombre_provincia, xy=(centroid.x, centroid.y),
                 horizontalalignment='center', fontsize=12, color='black', fontweight='bold')'''

plt.title("Provincias de Galicia")
plt.savefig("mapa_galicia.png", dpi=2160, bbox_inches='tight')
plt.show()

def conquistar_concello(G):
    # Seleccionar un concello aleatorio
    concello_inicial = random.choice(list(G.nodes))

    # Obtener los vecinos limítrofes
    vecinos = list(G.neighbors(concello_inicial))

    # Filtrar los vecinos para evitar que el concello inicial se conquiste a sí mismo
    vecinos_filtrados = [v for v in vecinos if G.nodes[concello_inicial]['nombre'] not in G.nodes[v]['nombre']]

    if not vecinos_filtrados:
        # Si no hay vecinos válidos, no puede conquistar
        print(f"{G.nodes[concello_inicial]['nombre']} no puede conquistar más territorios")
        return G

    # Seleccionar un vecino aleatorio para conquistar
    concello_atacado = random.choice(vecinos_filtrados)

    # Obtener nombres para el mensaje
    nombre_inicial = G.nodes[concello_inicial]['nombre']
    nombre_atacado = G.nodes[concello_atacado]['nombre']
    nombre_original_atacado = G.nodes[concello_atacado]['nombre_original']

    # Mostrar el ataque
    print(
        f"El concello de {nombre_inicial} ha conquistado el concello de {nombre_original_atacado}, perteneciente a {nombre_atacado}")

    # Actualizar el nombre del concello conquistado
    G.nodes[concello_atacado]['nombre'] = f"{nombre_inicial}"

    return G

# Función para colorear concellos según su nuevo dueño
def colorear_concellos(galicia_map, G):
    # Crear una copia del mapa de Galicia
    mapa_coloreado = galicia_map.copy()

    # Asociar colores según el concello conquistador
    colores_disponibles = [
        "red", "green", "blue", "yellow", "orange", "purple",
        "pink", "brown", "gray", "lightblue", "lightgreen", "lightpink"
    ]

    colores = {
        50: {'nombre': 'Coristanco', 'color': random.choice(colores_disponibles)},
        26: {'nombre': 'Zas', 'color': random.choice(colores_disponibles)},
        25: {'nombre': 'Vimianzo', 'color': random.choice(colores_disponibles)},
        73: {'nombre': 'Muxía', 'color': random.choice(colores_disponibles)},
        44: {'nombre': 'Cee', 'color': random.choice(colores_disponibles)},
        58: {'nombre': 'Fisterra', 'color': random.choice(colores_disponibles)},
        49: {'nombre': 'Corcubión', 'color': random.choice(colores_disponibles)},
        55: {'nombre': 'Dumbría', 'color': random.choice(colores_disponibles)},
        66: {'nombre': 'Mazaricos', 'color': random.choice(colores_disponibles)},
        74: {'nombre': 'Carnota', 'color': random.choice(colores_disponibles)},
        74: {'nombre': 'Muros', 'color': random.choice(colores_disponibles)},

    }

    # Crear una nueva columna en el GeoDataFrame para los colores
    mapa_coloreado["color"] = "white"  # Color por defecto para concellos no conquistados

    # Recorrer los nodos del grafo y aplicar los colores basados en el nombre del conquistador
    for node in G.nodes:
        print(G.nodes[node]['nombre'])
        nombre_actual = G.nodes[node]['nombre']
        nombre_original = G.nodes[node]['nombre_original']

        # Buscar el concello en el mapa basado en el nombre original
        concello_mapa = mapa_coloreado[mapa_coloreado['CONCELLO'] == nombre_original]

        if not concello_mapa.empty:
            # Asignar el color basado en el concello conquistador (primer nombre en el string concatenado)
            conquistador = nombre_actual.split("_")[0]
            color = colores.get(conquistador, "grey")  # Color gris si no se encuentra el conquistador
            mapa_coloreado.loc[mapa_coloreado['CONCELLO'] == nombre_original, "color"] = color

    return mapa_coloreado

# Colorear el mapa según las conquistas
mapa_actualizado = colorear_concellos(galicia_map, G)

# Visualizar el mapa actualizado
plt.figure(figsize=(20, 20))
mapa_actualizado.plot(edgecolor="black", color=mapa_actualizado["color"])
plt.title("Mapa de Galicia con Conquistas")
plt.show()

# Simular varios días de conquistas y actualizar el mapa
dias = 5
for dia in range(dias):
    print(f"Día {dia + 1}:")
    G = conquistar_concello(G)

    # Actualizar el mapa según las conquistas
    mapa_actualizado = colorear_concellos(galicia_map, G)

    # Dibujar el mapa actualizado
    plt.figure(figsize=(20, 20))
    mapa_actualizado.plot(edgecolor="black",linewidth=0.1, color=mapa_actualizado["color"])
    plt.title(f"Mapa de Galicia con Conquistas (Día {dia + 1})")
    plt.savefig("mapa_galicia_con_nombres"+str(dia+1)+".png", bbox_inches='tight')  # dpi alto para mayor calidad
    plt.show()
