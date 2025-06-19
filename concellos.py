import random

import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
data = []
galicia_map = gpd.read_file("Geographic_data/Concellos_IGN.shp", encoding ="utf-8")
#print(galicia_map['CONCELLO'])
for i in range(len(galicia_map['CONCELLO'])):
    data.append(galicia_map['CONCELLO'][i])

print(data)

concellos = {}
for index, concello in enumerate(data, start=1):
    concellos[index] = {"nombre": concello, "vecinos": []}

print(concellos)