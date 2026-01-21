import os
import random
import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as path_effects
import geopandas as gpd
import folium
from shapely.geometry import Polygon
from shapely.ops import unary_union
from distinctipy import distinctipy
from concellos_python import concellos

# Paths and constants\ nIMAGEN_DIR = "Images/Concellos/imagenes6"
IMAGEN_DIR = "Images/Concellos/imagenes9"
LOG_PATH = "logs/Concellos/log_conquistas9.csv"
MAPA_BASE_PATH = "Images/Concellos/mapa_galicia.png"
VICTORIA_IMG_PATH = "Images/Concellos/imagenes9/victoria.png"
INTERACTIVOS_DIR = "mapas_interactivos/Concellos/"
MAPA_PATH = "Geographic_data/Concellos_IGN.shp"
SAVE_EVERY_N_DAYS = 1
CONQUISTAS_POR_DIA = 1  # Ajusta este valor según lo agresivo que quieras
MAX_PROVINCES = len(concellos)
colores_fijos = {}
colores_disponibles = [mcolors.to_hex(rgb) for rgb in distinctipy.get_colors(MAX_PROVINCES)]

# Build graph from GeoDataFrame
def inicializar_grafo_de_gdf(gdf, id_field='CODCONC', name_field='CONCELLO'):
    G = nx.Graph()
    gdf = gdf.reset_index(drop=True)
    # Add nodes
    for _, row in gdf.iterrows():
        gid = int(row[id_field])
        G.add_node(gid, nombre=row[name_field], nombre_original=row[name_field])
    # Spatial index for adjacencies
    sindex = gdf.sindex
    for idx, row in gdf.iterrows():
        geom = row.geometry
        posibles = list(sindex.intersection(geom.bounds))
        for j in posibles:
            if j <= idx:
                continue
            if geom.touches(gdf.loc[j].geometry):
                a = int(row[id_field])
                b = int(gdf.loc[j, id_field])
                G.add_edge(a, b)
    return G

# Color utility
def obtener_color(conquistador):
    if conquistador in colores_fijos:
        return colores_fijos[conquistador]
    if not colores_disponibles:
        raise RuntimeError("Se acabaron los colores disponibles.")
    color = colores_disponibles.pop()
    colores_fijos[conquistador] = color
    return color

# Prepare base map
def preparar_mapa_base(gdf, output_path=MAPA_BASE_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(20,20))
    gdf.plot(ax=ax, edgecolor='black', linewidth=0.1, color='white')
    for _, row in gdf.iterrows():
        c = row.geometry.centroid
        ax.annotate(row['CONCELLO'], (c.x, c.y), ha='center', fontsize=4, color='black', weight='bold')
    ax.set_title("Concellos de Galicia")
    ax.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

# Color concellos by node id
def colorear_concellos(gdf, G):
    gdf_copy = gdf.copy()
    gdf_copy['color'] = 'white'
    for node, data in G.nodes(data=True):
        color = obtener_color(data['nombre'])
        gdf_copy.loc[gdf_copy['CODCONC']==node, 'color'] = color
    return gdf_copy


def dibujar_contorno_exterior(grupo, ax, color, excluir=None):
    if excluir:
        grupo = grupo[grupo['CONCELLO'] != excluir]
    union = grupo.geometry.union_all()
    geoms = [union] if isinstance(union, Polygon) else union.geoms
    for geom in geoms:
        x, y = geom.exterior.xy
        ax.plot(x, y, color=color, linewidth=2.5, zorder=2.5)


def conquistar_concello(G):
    # 1. Calcular el tamaño de cada imperio
    nombres = nx.get_node_attributes(G, 'nombre')
    imperios_unicos = list(set(nombres.values()))

    if len(imperios_unicos) <= 1:
        return None

    # Contar territorios por imperio
    conteo = {}
    for n in G.nodes:
        imp = nombres[n]
        conteo[imp] = conteo.get(imp, 0) + 1

    # 2. Selección Ponderada Cuadrática (La clave de la velocidad)
    imperios = list(conteo.keys())
    # Elevamos al cuadrado (**2) para acelerar la partida drásticamente.
    # Si quieres que sea un poco más lento, usa (**1.5). Si quieres flash, (**3).
    pesos = [conteo[imp] ** 1.3 for imp in imperios]

    # Intentamos elegir un atacante válido (puede que el elegido no tenga vecinos enemigos)
    for _ in range(20):  # 20 intentos de encontrar un ataque válido
        atacante = random.choices(imperios, weights=pesos, k=1)[0]

        # Buscar todos los nodos de este atacante que tengan vecinos enemigos (frontera)
        nodos_atacante = [n for n in G.nodes if nombres[n] == atacante]
        frontera = []

        for n in nodos_atacante:
            for vecino in G.neighbors(n):
                if nombres[vecino] != atacante:
                    frontera.append((n, vecino))

        # Si este imperio no tiene frontera con enemigos (está rodeado por sí mismo o mar), probamos otro
        if not frontera:
            continue

        # Seleccionar un punto de ataque aleatorio en su frontera
        t_id, v_id = random.choice(frontera)

        defensor = nombres[v_id]
        nombre_original_atacado = G.nodes[v_id]['nombre_original']

        # Ejecutar conquista
        G.nodes[v_id]['nombre'] = atacante

        eliminado = None
        # Verificar si eliminamos al defensor (restamos 1 a su conteo previo)
        if conteo[defensor] - 1 <= 0:
            eliminado = defensor
            print(f"¡O imperio '{defensor}' foi eliminado por {atacante}!")
        else:
            print(f"{atacante} conquista {nombre_original_atacado} (era de {defensor})")

        return G, t_id, v_id, defensor, atacante, eliminado

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

            print(f"O Concello de {nombre_atacante} conquistou o concello  de {nombre_original_atacado}, pertencente a {nombre_defensor}")
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
    grupo = mapa[mapa['CONCELLO'].isin(comarcas)]
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


def dibujar_mapa_conquista(mapa, mapa_ant, G, G_ant, a_id, d_id, imperio_defensor, imperio_atacante, num_secuencia, dia, nombre_concello):
    nombres = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')

    # 1. Mapa base plano
    mapa.plot(ax=ax, edgecolor="black", linewidth=0.1, color=mapa["color"])

    # 2. RESTAURADO: Contornos generales de todos los imperios
    # Esto es lo que da la sensación de "fronteras" entre potencias.
    # Usamos un linewidth medio (1.0) para que se note pero no sea excesivo.
    for color, grupo in mapa.groupby("color"):
        if color == 'white': continue # No dibujar contorno a los neutrales si los hubiera
        union = grupo.geometry.union_all()
        geoms = [union] if isinstance(union, Polygon) else union.geoms
        for geom in geoms:
            x, y = geom.exterior.xy
            ax.plot(x, y, color='black', linewidth=1.0, zorder=2)

    # Geometría de atacante y defensor
    def_comarca = originales[d_id]

    # 3. Resaltar protagonistas: Atacante (Verde Lima)
    atacantes = [originales[n] for n in G.nodes if nombres[n] == imperio_atacante]
    grupo_atacante = mapa[mapa['CONCELLO'].isin(atacantes)]
    # Dibujamos un contorno más grueso (2.5) y de color vivo sobre el negro
    dibujar_contorno_exterior(grupo_atacante, ax, 'lime', excluir=def_comarca)

    # 4. Resaltar protagonistas: Defensor (Rojo) - Usando el mapa anterior
    if imperio_defensor:
        nombres_ant = nx.get_node_attributes(G_ant, 'nombre')
        defensores = [originales[n] for n in G_ant.nodes if nombres_ant[n] == imperio_defensor]
        grupo_defensor = mapa_ant[mapa_ant['CONCELLO'].isin(defensores)]
        dibujar_contorno_exterior(grupo_defensor, ax, 'red')

    # 5. Hachurar la zona de batalla (la "herida")
    mapa[mapa['CONCELLO'] == def_comarca].plot(
        ax=ax, edgecolor='white', facecolor='none', hatch='////', linewidth=0.5, zorder=5
    )

    # 6. Etiquetas y Título
    # Mostrar nombre del atacante
    mostrar_nombre_imperio(imperio_atacante, mapa_ant, G_ant, ax, '#004400')
    # Mostrar nombre del defensor si sigue vivo
    if sum(1 for v in nombres.values() if v == imperio_defensor) >= 1:
        mostrar_nombre_imperio(imperio_defensor, mapa, G, ax, '#440000')

    # Mostrar nombre del concello disputado en pequeño
    geom_concello = mapa[mapa['CONCELLO'] == def_comarca].geometry.values[0]
    centro = geom_concello.centroid
    txt = ax.annotate(def_comarca, (centro.x, centro.y), ha='center', fontsize=6, fontweight='bold', color='white', zorder=10)
    txt.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()])

    # --- NUEVO TÍTULO INFORMATIVO ---
    titulo = f"Día {dia}: {imperio_atacante} conquista {nombre_concello}"
    if imperio_defensor:
        titulo += f" (era de {imperio_defensor})"

    plt.title(titulo, fontsize=14, fontweight='bold', pad=12)

    # Guardar (DPI 120 es un buen compromiso calidad/velocidad)
    filename = f"frame_{num_secuencia:05d}.png"
    plt.savefig(f"{IMAGEN_DIR}/{filename}", bbox_inches='tight', dpi=120)
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

            texto = f"Día {dia}: O imperio de {atacante} conquistou o concello de {comarca}, que pertencía a {antiguo}."
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
    grupo_vencedor = mapa[mapa['CONCELLO'].isin(comarcas)]
    dibujar_contorno_exterior(grupo_vencedor, ax, 'gold')

    # Nombre del imperio en el centro
    mostrar_nombre_imperio(vencedor, mapa, G, ax, color_texto="black")

    # Título festivo
    plt.title(f"¡{vencedor} conquista toda Galicia!", fontsize=16, weight='bold')

    os.makedirs(os.path.dirname(output), exist_ok=True)
    plt.savefig(output, bbox_inches='tight', dpi=200)
    plt.close()


def crear_mapa_interactivo(mapa, G, dia, carpeta=INTERACTIVOS_DIR):
    # Asegura CRS correcto para folium
    if mapa.crs is None:
        mapa.set_crs(epsg=25829, inplace=True)
    if mapa.crs.to_epsg() != 4326:
        mapa = mapa.to_crs(epsg=4326)

    # Preparar atributos
    nombres = nx.get_node_attributes(G, 'nombre')
    originales = nx.get_node_attributes(G, 'nombre_original')

    mapa["Imperio"] = mapa["CONCELLO"].map({originales[n]: nombres[n] for n in G.nodes})
    mapa["color"] = mapa["CONCELLO"].map({originales[n]: obtener_color(nombres[n]) for n in G.nodes})

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
            fields=["CONCELLO", "Imperio"],
            aliases=["CONCELLO:", "Controlada por:"],
            sticky=True
        )
    ).add_to(m)

    # Guardar
    os.makedirs(carpeta, exist_ok=True)
    output_path = os.path.join(carpeta, f"mapa_interactivo_dia_{dia + 1}.html")
    m.save(output_path)


def simular_conquistas_2(G, galicia_map):
    # Colorear inicial
    mapa = colorear_concellos(galicia_map, G)

    dia = 1
    total_conquistas = 1  # Contador global para los frames

    # Preparar CSV
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Día", "Atacante", "Comarca", "Antiguo Dueño", "Eliminado"])

    while len(set(nx.get_node_attributes(G, 'nombre').values())) > 1:

        conquistas_hoy = 0
        while conquistas_hoy < CONQUISTAS_POR_DIA:

            # Guardar estados anteriores para la visualización
            mapa_ant = mapa.copy()
            G_ant = G.copy()

            resultado = conquistar_concello(G)

            if not resultado:
                break # Fin del juego

            G, a_id, d_id, imp_defensor, imp_atacante, eliminado = resultado
            nombre_concello = G.nodes[d_id]['nombre_original']

            # Actualizar visualmente el mapa principal
            nuevo_color = obtener_color(imp_atacante)
            mapa.loc[mapa['CONCELLO'] == nombre_concello, 'color'] = nuevo_color

            # Guardar Log
            with open(LOG_PATH, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([total_conquistas, dia, imp_atacante, nombre_concello, imp_defensor, eliminado or ""])

            # DIBUJAR: Pasamos los datos necesarios para el título
            dibujar_mapa_conquista(
                mapa, mapa_ant, G, G_ant, a_id, d_id,
                imp_defensor, imp_atacante,
                total_conquistas,
                dia,            # <--- Nuevo parámetro
                nombre_concello # <--- Nuevo parámetro
            )

            total_conquistas += 1
            conquistas_hoy += 1

            # Chequeo de victoria rápida
            if len(set(nx.get_node_attributes(G, 'nombre').values())) == 1:
                break

        print(f"--- Fin del Día {dia} (Frame {total_conquistas-1}) ---")
        dia += 1


def main():
    random.seed(33)
    # Load map
    galicia_map = gpd.read_file(MAPA_PATH, encoding='utf-8')
    if galicia_map.crs is None:
        galicia_map.set_crs(epsg=25829, inplace=True)
    else:
        galicia_map = galicia_map.to_crs(epsg=25829)
    # Init graph
    G = inicializar_grafo_de_gdf(galicia_map, id_field='CODCONC', name_field='CONCELLO')

    id_illa = None
    id_vilanova = None
    for n, data in G.nodes(data=True):
        if "Arousa" in data['nombre'] and "Illa" in data['nombre']:
            id_illa = n
        if "Vilanova de Arousa" in data['nombre']:
            id_vilanova = n

    if id_illa and id_vilanova:
        G.add_edge(id_illa, id_vilanova)
        print(f"Conexión artificial establecida entre {id_illa} y {id_vilanova}")

    # Directories
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    os.makedirs(IMAGEN_DIR, exist_ok=True)
    os.makedirs(INTERACTIVOS_DIR, exist_ok=True)
    # Base map
    preparar_mapa_base(galicia_map)
    # Run simulation
    simular_conquistas_2(G, galicia_map)
    # Export logs and victory image
    guardar_log_narrado()
    generar_imagen_victoria(G, galicia_map)

if __name__=='__main__':
    main()
