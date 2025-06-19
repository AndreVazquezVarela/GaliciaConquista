import random
import networkx as nx
import matplotlib.pyplot as plt

# Crear los concellos con identificadores únicos y nombres originales
concellos = {
    1: {"nombre": "Coruña", "vecinos": [2, 4]},
    2: {"nombre": "Lugo", "vecinos": [1, 3]},
    3: {"nombre": "Ourense", "vecinos": [2, 4]},
    4: {"nombre": "Pontevedra", "vecinos": [1, 3]}
}

# Inicializar el grafo
G = nx.Graph()

# Añadir nodos y aristas al grafo, con nombre y nombre_original como atributos
for id_concello, datos in concellos.items():
    G.add_node(id_concello, nombre=datos["nombre"], nombre_original=datos["nombre"])
    for vecino in datos["vecinos"]:
        G.add_edge(id_concello, vecino)

# Función para visualizar el grafo con nombres
def dibujar_mapa(G):
    labels = nx.get_node_attributes(G, 'nombre')
    plt.figure(figsize=(8, 6))
    nx.draw(G, labels=labels, with_labels=True, node_color="skyblue", font_weight="bold", node_size=2000)
    plt.show()

# Dibujar el grafo inicial
dibujar_mapa(G)


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


# Simular varios días de conquistas
dias = 5
for dia in range(dias):
    print(f"Día {dia + 1}:")
    G = conquistar_concello(G)

    # Dibujar el estado actual
    dibujar_mapa(G)


