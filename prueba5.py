import json

# Lee tu JSON original
with open("concellos_vecinos.json", encoding="utf-8") as f:
    data = json.load(f)

# Abre un fichero donde volcar el diccionario en literal Python
with open("concellos_python.py", "w", encoding="utf-8") as out:
    out.write("concellos = {\n")
    for key_str, info in data.items():
        key = int(key_str)
        nombre = info["nombre"].replace("'", "\\'")
        vecinos = info["vecinos"]
        out.write(
            f"    {key}: {{'nombre': '{nombre}', 'vecinos': {vecinos}}},\n"
        )
    out.write("}\n")