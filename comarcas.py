import random

import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib as cm
from distinctipy import distinctipy
from shapely.geometry import Polygon, MultiPolygon
import csv
import os
from shapely.ops import unary_union
import matplotlib.patheffects as path_effects

# Crear los concellos con identificadores únicos y nombres originales
colores_fijos = {}

concellos = {
    0: {'nombre': 'A Barcala', 'vecinos': [14, 17, 10]},
    1: {'nombre': 'A Coruña', 'vecinos': [5, 4, 12]},
    2: {'nombre': 'Arzúa', 'vecinos': [15, 5, 12, 14, 47]},
    3: {'nombre': 'Barbanza', 'vecinos': [11, 10, 44]},
    4: {'nombre': 'Bergantiños', 'vecinos': [12, 17, 16, 1]},
    5: {'nombre': 'Betanzos', 'vecinos': [1, 6, 12, 15, 2, 29]},
    6: {'nombre': 'Eume', 'vecinos': [29, 7, 13, 5]},
    7: {'nombre': 'Ferrol', 'vecinos': [13, 6]},
    8: {'nombre': 'Fisterra', 'vecinos': [16, 17, 9]},
    9: {'nombre': 'Muros', 'vecinos': [10, 17]},
    10: {'nombre': 'Noia', 'vecinos': [9, 17, 0, 14, 11, 3]},
    11: {'nombre': 'O Sar', 'vecinos': [10, 3, 14, 51, 44]},
    12: {'nombre': 'Ordes', 'vecinos': [1, 4, 5, 2, 14, 17]},
    13: {'nombre': 'Ortegal', 'vecinos': [7, 6, 20]},
    14: {'nombre': 'Santiago', 'vecinos': [2, 12, 17, 0, 11, 10, 51, 47]},
    15: {'nombre': 'Terra De Melide', 'vecinos': [5, 2, 47, 22, 24, 29]},
    16: {'nombre': 'Terra De Soneira', 'vecinos': [4, 17, 8]},
    17: {'nombre': 'Xallas', 'vecinos': [4, 8, 9, 10, 0, 14]},
    18: {'nombre': 'A Fonsagrada', 'vecinos': [21, 25, 24, 26]},
    19: {'nombre': 'A Mariña Central', 'vecinos': [20, 21, 25, 29]},
    20: {'nombre': 'A Mariña Occidental', 'vecinos': [13, 19, 29]},
    21: {'nombre': 'A Mariña Oriental', 'vecinos': [19, 18, 25]},
    22: {'nombre': 'A Ulloa', 'vecinos': [24, 23, 47, 15]},
    23: {'nombre': 'Chantada', 'vecinos': [24, 30, 28, 22, 47, 36]},
    24: {'nombre': 'Lugo', 'vecinos': [25, 18, 29, 26, 28, 22, 15]},
    25: {'nombre': 'Meira', 'vecinos': [19, 20, 18, 24, 29]},
    26: {'nombre': 'Os Ancares', 'vecinos': [18, 24, 27, 28]},
    27: {'nombre': 'Quiroga', 'vecinos': [40, 39, 37, 30, 28, 26]},
    28: {'nombre': 'Sarria', 'vecinos': [26, 24, 23, 30, 27]},
    29: {'nombre': 'Terra Chá', 'vecinos': [24, 25, 19, 20, 6, 5, 15]},
    30: {'nombre': 'Terra De Lemos', 'vecinos': [27, 28, 23, 36, 37]},
    31: {'nombre': 'A Limia', 'vecinos': [41, 37, 32, 38, 33]},
    32: {'nombre': 'Allariz-Maceda', 'vecinos': [31, 37, 36, 38]},
    33: {'nombre': 'Baixa Limia', 'vecinos': [38, 31]},
    34: {'nombre': 'O Carballiño', 'vecinos': [35, 36, 47, 51, 23]},
    35: {'nombre': 'O Ribeiro', 'vecinos': [34, 36, 43, 50, 52, 38]},
    36: {'nombre': 'Ourense', 'vecinos': [23, 30, 37, 38, 32, 34, 35]},
    37: {'nombre': 'Terra De Caldelas', 'vecinos': [30, 27, 39, 31, 41, 32, 36]},
    38: {'nombre': 'Terra De Celanova', 'vecinos': [31, 32, 33, 35, 36, 43]},
    39: {'nombre': 'Terra De Trives', 'vecinos': [27, 37, 41, 40, 42]},
    40: {'nombre': 'Valdeorras', 'vecinos': [27, 39, 42]},
    41: {'nombre': 'Verín', 'vecinos': [42, 39, 37, 31]},
    42: {'nombre': 'Viana', 'vecinos': [40, 41, 39]},
    43: {'nombre': 'A Paradanta', 'vecinos': [35, 38, 46, 52]},
    44: {'nombre': 'Caldas', 'vecinos': [3, 11, 49, 50, 51]},
    45: {'nombre': 'O Baixo Miño', 'vecinos': [52, 46]},
    46: {'nombre': 'O Condado', 'vecinos': [43, 45, 52]},
    47: {'nombre': 'Deza', 'vecinos': [51, 2, 14, 15, 22, 23, 34]},
    48: {'nombre': 'O Morrazo', 'vecinos': [50]},
    49: {'nombre': 'O Salnés', 'vecinos': [44, 50]},
    50: {'nombre': 'Pontevedra', 'vecinos': [48, 49, 51, 52, 44, 34, 35]},
    51: {'nombre': 'Tabeirós-Terra De Montes', 'vecinos': [47, 11, 14, 44, 50, 34]},
    52: {'nombre': 'Vigo', 'vecinos': [35, 43, 46, 45, 50]},
}




colores_disponibles = [mcolors.to_hex(rgb) for rgb in distinctipy.get_colors(len(concellos))]

def inicializar_grafo(concellos):
    G = nx.Graph()
    for id_concello, datos in concellos.items():
        G.add_node(id_concello, nombre=datos["nombre"], nombre_original=datos["nombre"])
        for vecino in datos["vecinos"]:
            G.add_edge(id_concello, vecino)
    return G

def preparar_mapa_base(gdf):
    plt.figure(figsize=(20, 20))
    gdf.plot(edgecolor="black", linewidth=0.1, color="white")
    for _, row in gdf.iterrows():
        centroide = row.geometry.centroid
        plt.annotate(row['Comarca'], (centroide.x, centroide.y), ha='center', fontsize=4, color='black', weight='bold')
    plt.title("Comarcas de Galicia")
    plt.savefig("Images/mapa_galicia.png", dpi=300, bbox_inches='tight')
    plt.close()

def obtener_color(conquistador):
    if conquistador not in colores_fijos:
        if not colores_disponibles:
            raise ValueError("Non quedan colores dispoñibles.")
        colores_fijos[conquistador] = colores_disponibles.pop()
    return colores_fijos[conquistador]

def colorear_concellos(gdf, G):
    gdf_copy = gdf.copy()
    gdf_copy["color"] = "white"
    for node in G.nodes:
        nombre = G.nodes[node]['nombre']
        original = G.nodes[node]['nombre_original']
        color = obtener_color(nombre)
        gdf_copy.loc[gdf_copy['Comarca'] == original, 'color'] = color
    return gdf_copy

def dibujar_contorno_exterior(grupo, ax, color, excluir=None):
    if excluir:
        grupo = grupo[grupo['Comarca'] != excluir]
    union = grupo.geometry.union_all()
    geoms = [union] if isinstance(union, Polygon) else union.geoms
    for geom in geoms:
        x, y = geom.exterior.xy
        ax.plot(x, y, color=color, linewidth=2.5, zorder=2.5)

def conquistar_concello(G):
    imperios = list(set(G.nodes[n]['nombre'] for n in G.nodes))
    # Opción 2: ordenar imperios por tamaño descendente (prioriza los grandes)
    imperios.sort(key=lambda imp: -sum(G.nodes[n]['nombre'] == imp for n in G.nodes))
    random.shuffle(imperios)  # Para introducir algo de aleatoriedad

    for imperio in imperios:
        territorios = [n for n in G.nodes if G.nodes[n]['nombre'] == imperio]
        vecinos_posibles = []
        for t in territorios:
            for v in G.neighbors(t):
                if G.nodes[v]['nombre'] != imperio:
                    # Opción 3: calcular "vulnerabilidad" del defensor
                    vecinos_mismos = sum(G.nodes[n]['nombre'] == G.nodes[v]['nombre'] for n in G.neighbors(v))
                    vecinos_posibles.append((vecinos_mismos, t, v))

        if vecinos_posibles:
            # Escoge el más vulnerable (menos vecinos de su mismo imperio)
            vecinos_posibles.sort(key=lambda x: x[0])
            _, atacante_id, defensor_id = vecinos_posibles[0]

            nombre_atacante = G.nodes[atacante_id]['nombre']
            nombre_defensor = G.nodes[defensor_id]['nombre']
            nombre_original_atacado = G.nodes[defensor_id]['nombre_original']

            print(f"A comarca de {nombre_atacante} conquistou a comarca de {nombre_original_atacado}, perteneciente a {nombre_defensor}")

            G.nodes[defensor_id]['nombre'] = nombre_atacante

            eliminado = None
            if not any(G.nodes[n]['nombre'] == nombre_defensor for n in G.nodes):
                eliminado = nombre_defensor
                print(f"¡O imperio '{nombre_defensor}' foi eliminado!")

            return G, atacante_id, defensor_id, nombre_defensor, nombre_atacante, eliminado

    print("Non quedan conquistas posibles.")
    return None

def mostrar_nombre_imperio(nombre_imperio, mapa, G, ax, color_texto):
    territorios = [n for n in G.nodes if G.nodes[n]['nombre'] == nombre_imperio]
    if not territorios:
        return
    comarcas = [G.nodes[n]['nombre_original'] for n in territorios]
    grupo = mapa[mapa['Comarca'].isin(comarcas)]
    geometria = unary_union(grupo.geometry)
    if not geometria.is_empty:
        centro = geometria.centroid
        txt = ax.annotate(nombre_imperio, (centro.x, centro.y + 0.02), ha='center', fontsize=10, fontstyle='italic', color=color_texto, zorder=10)
        txt.set_path_effects([path_effects.Stroke(linewidth=1.2, foreground='black'),
                              path_effects.Normal()])

def dibujar_mapa_conquista(mapa, mapa_ant, G, G_ant, a_id, d_id, imperio_defensor, imperio_atacante, dia):
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    mapa.plot(ax=ax, edgecolor="black", linewidth=0.1, color=mapa["color"])


    for color, grupo in mapa.groupby("color"):
        union = grupo.geometry.union_all()
        geoms = [union] if isinstance(union, Polygon) else union.geoms
        for geom in geoms:
            x, y = geom.exterior.xy
            ax.plot(x, y, color='black', linewidth=1.0)

    def_geom = mapa[mapa['Comarca'] == G.nodes[d_id]['nombre_original']].geometry.values[0]
    ata_geom = mapa[mapa['Comarca'] == G.nodes[a_id]['nombre_original']].geometry.values[0]

    atacantes = [G.nodes[n]['nombre_original'] for n in G.nodes if G.nodes[n]['nombre'] == imperio_atacante]
    grupo_atacante = mapa[mapa['Comarca'].isin(atacantes)]
    dibujar_contorno_exterior(grupo_atacante, ax, 'lime', excluir=G.nodes[d_id]['nombre_original'])

    color_ant = mapa_ant.loc[mapa_ant['Comarca'] == G.nodes[d_id]['nombre_original'], 'color'].values[0]
    grupo_defensor = mapa_ant[mapa_ant['color'] == color_ant]
    dibujar_contorno_exterior(grupo_defensor, ax, 'red')

    mapa[mapa['Comarca'] == G.nodes[d_id]['nombre_original']].plot(
        ax=ax, edgecolor='red', facecolor='none', hatch='///', linewidth=1.0, zorder=5)

    # Mostrar nombre del imperio atacante usando su geometría antes del ataque
    mostrar_nombre_imperio(imperio_atacante, mapa_ant, G_ant, ax, '#90ee90')

    if any(G.nodes[n]['nombre'] == imperio_defensor for n in G.nodes) and \
       len([n for n in G.nodes if G.nodes[n]['nombre'] == imperio_defensor]) >= 2:
        mostrar_nombre_imperio(imperio_defensor, mapa, G, ax, 'red')

    for geom, nombre in [(def_geom, G.nodes[d_id]['nombre_original'])]:
        centro = geom.centroid
        txt = ax.annotate(nombre, (centro.x, centro.y), ha='center', fontsize=6, fontweight='bold', color='white', zorder=10)
        txt.set_path_effects([path_effects.Stroke(linewidth=1.2, foreground='black'),
                      path_effects.Normal()])


    plt.title(f"Conquista - Día {dia + 1}")
    os.makedirs("Images/imagenes6", exist_ok=True)
    plt.savefig(f"Images/imagenes6/mapa_galicia_con_nombres{dia + 1}.png", bbox_inches='tight', dpi=150)
    plt.close()

def guardar_log_narrado(ruta_csv="logs/log_conquistas3.csv", ruta_txt="logs/log_narrado.txt"):
    with open(ruta_csv, encoding="utf-8") as f_csv, open(ruta_txt, "w", encoding="utf-8") as f_txt:
        reader = csv.DictReader(f_csv)
        for fila in reader:
            dia = fila['Día']
            atacante = fila['Atacante']
            comarca = fila['Concello conquistado']
            antiguo = fila['Pertenecía a']
            eliminado = fila['Eliminado']

            texto = f"Día {dia}: O imperio de {atacante} conquistou á comarca de {comarca}, que pertencía a {antiguo}."
            f_txt.write(texto + "\n")
            if eliminado:
                f_txt.write(f"¡O imperio '{eliminado}' foi eliminado!\n")


def generar_imagen_victoria(G, galicia_map, output="Images/imagenes4/victoria.png"):
    imperios = list(set(G.nodes[n]['nombre'] for n in G.nodes))
    if len(imperios) != 1:
        return  # aún no hay victoria
    vencedor = imperios[0]

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    mapa = colorear_concellos(galicia_map, G)
    mapa.plot(ax=ax, edgecolor="black", linewidth=0.1, color=mapa["color"])

    # contorno general
    grupo_vencedor = mapa[mapa['Comarca'].isin([G.nodes[n]['nombre_original'] for n in G.nodes])]
    dibujar_contorno_exterior(grupo_vencedor, ax, 'gold')

    # nombre en el centro
    mostrar_nombre_imperio(vencedor, mapa, G, ax, color_texto="black")

    # título festivo
    plt.title(f"🎉 ¡{vencedor} conquista toda Galicia! 🌟", fontsize=16, weight='bold')
    plt.savefig(output, bbox_inches='tight', dpi=200)
    plt.close()


    def crear_mapa_interactivo_por_dia(mapa, G, dia, carpeta="mapas_interactivos"):
        import folium
        os.makedirs(carpeta, exist_ok=True)
        m = folium.Map(location=[42.9, -8.2], zoom_start=8, tiles='cartodbpositron')

        for _, row in mapa.iterrows():
            comarca = row["Comarca"]
            geometria = row["geometry"]
            color = row["color"]
            imperio = next(G.nodes[n]['nombre'] for n in G.nodes if G.nodes[n]['nombre_original'] == comarca)

            folium.GeoJson(
                data=geometria.__geo_interface__,
                style_function=lambda x, color=color: {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 0.5,
                    'fillOpacity': 0.7,
                },
                tooltip=folium.Tooltip(f"<strong>{comarca}</strong><br>Imperio: {imperio}")
            ).add_to(m)

        archivo = os.path.join(carpeta, f"mapa_interactivo_dia_{dia + 1}.html")
        m.save(archivo)


def simular_conquistas_2(G, galicia_map):
    mapa = colorear_concellos(galicia_map, G)
    dia = 0

    with open("logs/log_conquistas4.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Día", "Atacante", "Comarca conquistada", "Pertenecía a", "Eliminado"])

    while len(set(G.nodes[n]['nombre'] for n in G.nodes)) > 1:
        mapa_ant = mapa.copy()
        G_ant = G.copy()
        res = conquistar_concello(G)
        if not res:
            break

        G, a_id, d_id, imperio_defensor, imperio_atacante, eliminado = res

        mapa = colorear_concellos(galicia_map, G)

        with open("logs/log_conquistas4.csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([dia + 1, imperio_atacante, G.nodes[d_id]['nombre_original'], imperio_defensor, eliminado or ""])

        mapa.loc[mapa['Comarca'] == G.nodes[d_id]['nombre_original'], 'color'] = \
            mapa_ant.loc[mapa_ant['Comarca'] == G.nodes[d_id]['nombre_original'], 'color'].values[0]

        dibujar_mapa_conquista(mapa, mapa_ant, G, G_ant, a_id, d_id, imperio_defensor, imperio_atacante, dia)

        mapa.loc[mapa['Comarca'] == G.nodes[d_id]['nombre_original'], 'color'] = \
            mapa[mapa['Comarca'] == G.nodes[a_id]['nombre_original']]['color'].values[0]

        crear_mapa_interactivo_por_dia(mapa, G, dia)

        dia += 1

def main():
    G = inicializar_grafo(concellos)
    galicia_map = gpd.read_file("Geographic_data/Comarcas.shp", encoding="utf-8")
    preparar_mapa_base(galicia_map)
    simular_conquistas_2(G, galicia_map)
    guardar_log_narrado()
    generar_imagen_victoria(G, galicia_map)

if __name__ == "__main__":
    main()