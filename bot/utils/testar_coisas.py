from requests import get
from utils.categoria import emoji
import json

def format_json(json_string):
    data = json.loads(json_string)

    max_id_length = max(len(str(item['id'])) for item in data)

    formatted_result = ""
    for item in data:
        id_str = str(item['id'])
        spaces = max_id_length - len(id_str)
        formatted_result += f"{' ' * spaces}<code>{id_str}</code>. <strong>{item['nome']}</strong> - {item['obra_nome']}\n"

    return formatted_result

def organizar_numeros(json_data):
    max_id_length = max(len(str(carta['id'])) for carta in json_data)
    def get_emoji(acumulado):
        if acumulado == 1:
            return ""
        elif 2 <= acumulado < 10:
            return "🕐"
        elif 10 <= acumulado < 25:
            return "🕒"
        elif 25 <= acumulado < 50:
            return "🎂"
        elif 50 <= acumulado < 100:
            return "🍰"
        else:
            return "🍽️"

    numeros_formatados = []

    for carta in json_data:
        id = str(carta['id'])
        spaces = max_id_length - len(id)
        emojii = get_emoji(carta['acumulado'])
        nome = carta['nome']
        obra_nome = carta['obra_nome']
        emj = emoji(carta['categoria'])
        numero_formatado = f"{emj}  {' ' * spaces}<code>{id}</code>. <strong>{nome}</strong> {emojii} — {obra_nome}"
        numeros_formatados.append(numero_formatado)

    return numeros_formatados

# para as obras
def organizar_obras(json_data: str) -> dict:
    max_id_length = len(max(json_data.keys(), key=len))

    numeros_formatados = []
    for id, valor in json_data.items():
        aligned_id = id.rjust(max_id_length)
        #ide = aligned_id.replace(" ","")
        nome = get(f"http://localhost:3000/carta/{id}").json()
        nomee = nome['carta']['nome']
        numero_formatado = f"`{aligned_id}`. *{nomee}*"
        numeros_formatados.append(numero_formatado)

    return numeros_formatados

def paginar_lista(lista: dict, itens_por_pagina=15) -> dict:
    paginas = []
    for i in range(0, len(lista), itens_por_pagina):
        paginas.append(lista[i:i+itens_por_pagina])
    return paginas
