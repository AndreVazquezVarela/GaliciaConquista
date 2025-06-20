import os
import random
import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as path_effects
import geopandas as gpd
import folium
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from distinctipy import distinctipy
from collections import Counter







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


IMAGEN_DIR = "Images/imagenes6"
LOG_PATH = "logs/log_conquistas5.csv"
MAPA_BASE_PATH = "Images/mapa_galicia.png"
VICTORIA_IMG_PATH = "Images/imagenes6/victoria.png"
INTERACTIVOS_DIR = "mapas_interactivos"
MAPA_PATH = "Geographic_data/Comarcas.shp"
SAVE_EVERY_N_DAYS = 1
MAX_PROVINCES = len(concellos)
# Crear los concellos con identificadores únicos y nombres originales
colores_fijos = {}
colores_disponibles = [mcolors.to_hex(rgb) for rgb in distinctipy.get_colors(MAX_PROVINCES)]

def inicializar_grafo(concellos):
    G = nx.Graph()

    for id_concello, datos in concellos.items():
        # Añadir nodo con nombre y nombre original
        G.add_node(id_concello, nombre=datos["nombre"], nombre_original=datos["nombre"])

        # Añadir aristas a vecinos (asegura que no se repiten aunque esté en ambos sentidos)
        for vecino in datos["vecinos"]:
            if not G.has_edge(id_concello, vecino):
                G.add_edge(id_concello, vecino)

    return G



def preparar_mapa_base(gdf, output_path="Images/mapa_galicia.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(20, 20))
    gdf.plot(ax=ax, edgecolor="black", linewidth=0.1, color="white")

    for _, row in gdf.iterrows():
        centroide = row.geometry.centroid
        ax.annotate(
            row['Comarca'],
            (centroide.x, centroide.y),
            ha='center',
            fontsize=4,
            color='black',
            weight='bold'
        )

    ax.set_title("Comarcas de Galicia")
    ax.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def obtener_color(conquistador):
    color = colores_fijos.get(conquistador)
    if color:
        return color

    if not colores_disponibles:
        raise RuntimeError("Non quedan cores dispoñibles para asignar a novos imperios.")

    novo_color = colores_disponibles.pop()
    colores_fijos[conquistador] = novo_color
    return novo_color


def colorear_concellos(gdf, G):
    gdf_copy = gdf.copy()
    gdf_copy["color"] = "white"
    nombres_actuales = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')
    for node in G.nodes:
        color = obtener_color(nombres_actuales[node])
        gdf_copy.loc[gdf_copy['Comarca'] == originales[node], 'color'] = color
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

    # Caso especial: solo quedan 2 imperios
    if len(imperios) == 2:
        imp1, imp2 = imperios
        tam1 = sum(G.nodes[n]['nombre'] == imp1 for n in G.nodes)
        tam2 = sum(G.nodes[n]['nombre'] == imp2 for n in G.nodes)

        # Determinar quién ataca este turno, ponderado por tamaño
        total = tam1 + tam2
        prob_imp1 = tam1 / total
        atacante = imp1 if random.random() < prob_imp1 else imp2
        defensor = imp2 if atacante == imp1 else imp1

        # Buscar un nodo atacante con vecino enemigo
        territorios = [n for n in G.nodes if G.nodes[n]['nombre'] == atacante]
        random.shuffle(territorios)
        for t in territorios:
            vecinos = list(G.neighbors(t))
            random.shuffle(vecinos)
            for v in vecinos:
                if G.nodes[v]['nombre'] == defensor:
                    G.nodes[v]['nombre'] = atacante
                    print(f"(2 imperios) {atacante} conquistou a comarca de {G.nodes[v]['nombre_original']}")

                    eliminado = None
                    if not any(G.nodes[n]['nombre'] == defensor for n in G.nodes):
                        eliminado = defensor
                        print(f"¡O imperio '{defensor}' foi eliminado!")

                    return G, t, v, defensor, atacante, eliminado

        print("Non quedan opcións de conquista entre os dous imperios.")
        return None

    # Comportamiento normal con más de 2 imperios
    imperios.sort(key=lambda imp: -sum(G.nodes[n]['nombre'] == imp for n in G.nodes))
    random.shuffle(imperios)

    for imperio in imperios:
        territorios = [n for n in G.nodes if G.nodes[n]['nombre'] == imperio]
        vecinos_posibles = []
        for t in territorios:
            for v in G.neighbors(t):
                if G.nodes[v]['nombre'] != imperio:
                    vecinos_mismos = sum(G.nodes[n]['nombre'] == G.nodes[v]['nombre'] for n in G.neighbors(v))
                    vecinos_posibles.append((vecinos_mismos, t, v))

        if vecinos_posibles:
            vecinos_posibles.sort(key=lambda x: x[0])
            _, atacante_id, defensor_id = vecinos_posibles[0]

            nombre_atacante = G.nodes[atacante_id]['nombre']
            nombre_defensor = G.nodes[defensor_id]['nombre']
            nombre_original_atacado = G.nodes[defensor_id]['nombre_original']

            print(f"A comarca de {nombre_atacante} conquistou a comarca de {nombre_original_atacado}, pertencente a {nombre_defensor}")
            G.nodes[defensor_id]['nombre'] = nombre_atacante

            eliminado = None
            if not any(G.nodes[n]['nombre'] == nombre_defensor for n in G.nodes):
                eliminado = nombre_defensor
                print(f"¡O imperio '{nombre_defensor}' foi eliminado!")

            return G, atacante_id, defensor_id, nombre_defensor, nombre_atacante, eliminado

    print("Non quedan conquistas posibles.")
    return None


def mostrar_nombre_imperio(nombre_imperio, mapa, G, ax, color_texto):
    nombres = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')

    territorios = [n for n, val in nombres.items() if val == nombre_imperio]
    if not territorios:
        return

    comarcas = [originales[n] for n in territorios]
    grupo = mapa[mapa['Comarca'].isin(comarcas)]
    if grupo.empty:
        return

    geometria = unary_union(grupo.geometry)
    if not geometria.is_empty:
        centro = geometria.centroid
        txt = ax.annotate(
            nombre_imperio,
            (centro.x, centro.y + 0.02),  # Puedes parametrizar este offset si lo prefieres
            ha='center',
            fontsize=10,
            fontstyle='italic',
            color=color_texto,
            zorder=10
        )
        txt.set_path_effects([
            path_effects.Stroke(linewidth=1.2, foreground='black'),
            path_effects.Normal()
        ])

def dibujar_mapa_conquista(mapa, mapa_ant, G, G_ant, a_id, d_id, imperio_defensor, imperio_atacante, dia):
    nombres = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    # Colorear comarcas
    mapa.plot(ax=ax, edgecolor="black", linewidth=0.1, color=mapa["color"])

    # Contornos generales de todos los colores
    for color, grupo in mapa.groupby("color"):
        union = grupo.geometry.union_all()
        geoms = [union] if isinstance(union, Polygon) else union.geoms
        for geom in geoms:
            x, y = geom.exterior.xy
            ax.plot(x, y, color='black', linewidth=1.0)

    # Geometría de atacante y defensor
    def_comarca = originales[d_id]
    ata_comarca = originales[a_id]
    def_geom = mapa[mapa['Comarca'] == def_comarca].geometry.values[0]

    # Contorno del imperio atacante (sin incluir la zona recién conquistada)
    atacantes = [originales[n] for n in G.nodes if nombres[n] == imperio_atacante]
    grupo_atacante = mapa[mapa['Comarca'].isin(atacantes)]
    dibujar_contorno_exterior(grupo_atacante, ax, 'lime', excluir=def_comarca)

    # Contorno del imperio defensor (color antiguo)
    color_ant = mapa_ant.loc[mapa_ant['Comarca'] == def_comarca, 'color'].values[0]
    grupo_defensor = mapa_ant[mapa_ant['color'] == color_ant]
    dibujar_contorno_exterior(grupo_defensor, ax, 'red')

    # Hachurar zona conquistada
    mapa[mapa['Comarca'] == def_comarca].plot(
        ax=ax, edgecolor='red', facecolor='none', hatch='///', linewidth=1.0, zorder=5
    )

    # Mostrar nombres de imperios
    mostrar_nombre_imperio(imperio_atacante, mapa_ant, G_ant, ax, '#90ee90')
    if sum(1 for v in nombres.values() if v == imperio_defensor) >= 2:
        mostrar_nombre_imperio(imperio_defensor, mapa, G, ax, 'red')

    # Mostrar nombre de la comarca conquistada
    centro = def_geom.centroid
    txt = ax.annotate(def_comarca, (centro.x, centro.y), ha='center', fontsize=6, fontweight='bold', color='white', zorder=10)
    txt.set_path_effects([
        path_effects.Stroke(linewidth=1.2, foreground='black'),
        path_effects.Normal()
    ])

    # Guardar imagen
    os.makedirs(IMAGEN_DIR, exist_ok=True)
    plt.title(f"Conquista - Día {dia + 1}")
    plt.savefig(f"{IMAGEN_DIR}/mapa_galicia_con_nombres{dia + 1}.png", bbox_inches='tight', dpi=150)
    plt.close()


def guardar_log_narrado(ruta_csv=LOG_PATH, ruta_txt="logs/log_narrado.txt"):
    os.makedirs(os.path.dirname(ruta_txt), exist_ok=True)

    with open(ruta_csv, encoding="utf-8") as f_csv, open(ruta_txt, "w", encoding="utf-8") as f_txt:
        reader = csv.DictReader(f_csv)
        for fila in reader:
            dia = fila.get('Día', '').strip()
            atacante = fila.get('Atacante', '').strip()
            comarca = fila.get('Concello conquistado', '').strip()
            antiguo = fila.get('Pertenecía a', '').strip()
            eliminado = fila.get('Eliminado', '').strip()

            if not dia or not atacante or not comarca or not antiguo:
                continue  # línea malformada

            texto = f"Día {dia}: O imperio de {atacante} conquistou á comarca de {comarca}, que pertencía a {antiguo}."
            f_txt.write(texto + "\n")

            if eliminado:
                f_txt.write(f"¡O imperio '{eliminado}' foi eliminado!\n")



def generar_imagen_victoria(G, galicia_map, output=VICTORIA_IMG_PATH):
    nombres = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')

    imperios = set(nombres.values())
    if len(imperios) != 1:
        return  # Aún no hay victoria

    vencedor = next(iter(imperios))
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    mapa = colorear_concellos(galicia_map, G)
    mapa.plot(ax=ax, edgecolor="black", linewidth=0.1, color=mapa["color"])

    # Contorno del vencedor
    comarcas = [originales[n] for n in G.nodes]
    grupo_vencedor = mapa[mapa['Comarca'].isin(comarcas)]
    dibujar_contorno_exterior(grupo_vencedor, ax, 'gold')

    # Nombre del imperio en el centro
    mostrar_nombre_imperio(vencedor, mapa, G, ax, color_texto="black")

    # Título festivo
    plt.title(f"¡{vencedor} conquista toda Galicia!", fontsize=16, weight='bold')

    os.makedirs(os.path.dirname(output), exist_ok=True)
    plt.savefig(output, bbox_inches='tight', dpi=200)
    plt.close()


def crear_mapa_interactivo(mapa, G, dia, carpeta="mapas_interactivos"):
    # Asegura CRS correcto para folium
    if mapa.crs is None:
        mapa.set_crs(epsg=25829, inplace=True)
    if mapa.crs.to_epsg() != 4326:
        mapa = mapa.to_crs(epsg=4326)

    # Preparar atributos
    nombres = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')

    mapa["Imperio"] = mapa["Comarca"].map({originales[n]: nombres[n] for n in G.nodes})
    mapa["color"] = mapa["Comarca"].map({originales[n]: obtener_color(nombres[n]) for n in G.nodes})

    # Crear mapa base
    centro = mapa.geometry.union_all().centroid
    m = folium.Map(location=[centro.y, centro.x], zoom_start=8, tiles=None)

    # Añadir regiones con estilos
    folium.GeoJson(
        mapa,
        style_function=lambda feature: {
            'fillColor': feature['properties']['color'],
            'color': 'black',
            'weight': 0.8,
            'fillOpacity': 0.9,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Comarca", "Imperio"],
            aliases=["Comarca:", "Controlada por:"],
            sticky=True
        )
    ).add_to(m)

    # Guardar
    os.makedirs(carpeta, exist_ok=True)
    output_path = os.path.join(carpeta, f"mapa_interactivo_dia_{dia + 1}.html")
    m.save(output_path)



def simular_conquistas_2(G, galicia_map):
    mapa = colorear_concellos(galicia_map, G)
    dia = 0

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Día", "Atacante", "Comarca conquistada", "Pertenecía a", "Eliminado"])

    while len(set(nx.get_node_attributes(G, 'nombre').values())) > 1:
        mapa_ant = mapa.copy()
        G_ant = G.copy()

        resultado = conquistar_concello(G)
        if not resultado:
            break

        G, a_id, d_id, imperio_defensor, imperio_atacante, eliminado = resultado

        nombre_original = G.nodes[d_id]['nombre_original']
        nuevo_color = obtener_color(imperio_atacante)

        # Actualizar colores en el mapa
        mapa = colorear_concellos(galicia_map, G)

        # Log de conquista
        with open(LOG_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([dia + 1, imperio_atacante, nombre_original, imperio_defensor, eliminado or ""])

        # Hacer que el cambio de color sea visualmente transitorio para destacar la conquista
        mapa.loc[mapa['Comarca'] == nombre_original, 'color'] = mapa_ant.loc[mapa_ant['Comarca'] == nombre_original, 'color'].values[0]
        dibujar_mapa_conquista(mapa, mapa_ant, G, G_ant, a_id, d_id, imperio_defensor, imperio_atacante, dia)
        mapa.loc[mapa['Comarca'] == nombre_original, 'color'] = nuevo_color

        # Guardar HTML interactivo cada SAVE_EVERY_N_DAYS (o siempre)
        if (dia + 1) % SAVE_EVERY_N_DAYS == 0:
            crear_mapa_interactivo(mapa, G, dia)

        dia += 1


def main():
    random.seed(33)
    # Cargar grafo y mapa
    G = inicializar_grafo(concellos)

    galicia_map = gpd.read_file(MAPA_PATH, encoding="utf-8")
    if galicia_map.crs is None:
        galicia_map.set_crs(epsg=25829, inplace=True)
    else:
        galicia_map = galicia_map.to_crs(epsg=25829)

    # Crear directorios si no existen
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    os.makedirs(IMAGEN_DIR, exist_ok=True)
    os.makedirs(INTERACTIVOS_DIR, exist_ok=True)

    # Crear mapa base
    preparar_mapa_base(galicia_map)

    # Ejecutar simulación
    simular_conquistas_2(G, galicia_map)

    # Exportar resultados
    guardar_log_narrado()
    generar_imagen_victoria(G, galicia_map)


if __name__ == "__main__":
    main()