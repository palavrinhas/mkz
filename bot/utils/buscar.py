from requests import get
import json

def organizar_numeros(json_data):
    # Encontra o comprimento máximo do ID
    max_id_length = len(max(json_data.keys(), key=len))

    # Formata e organiza os números sem ordenação prévia das chaves
    numeros_formatados = []
    for id, valor in json_data.items():
        # Alinha o ID com espaços à esquerda para manter os pontos alinhados
        aligned_id = id.rjust(max_id_length)
        # Formata o número conforme especificado
        ide = aligned_id.replace(" ","")
        nome = get(f"http://localhost:3000/carta/{ide}").json()
        nomee = nome["nome"]
        obra_nome = get(f"http://localhost:3000/obra/{nome["obra"]}").json()["nome"]
        numero_formatado = f"{aligned_id}. {nomee} - {obra_nome} (x{valor})"
        numeros_formatados.append(numero_formatado)

    return numeros_formatados

def get_items_by_page(json_data, page_number):
    items_per_page = 15
    start_index = (page_number - 1) * items_per_page
    end_index = min(start_index + items_per_page, len(json_data))

    items = []

    # Encontrar o comprimento máximo do ID
    max_id_length = len(str(len(json_data)))

    # Alinhar os números
    for i in range(start_index, end_index):
        item = json_data[i]
        item_number = item["ID"]
        item_value = item["nome"]
        obra = item["obra"]

        # Faz a requisição GET para obter os detalhes da carta
        response = get(f"http://localhost:3000/carta/{item_number}")
        obra_nome = get(f"http://localhost:3000/obra/{obra}").json()["nome"]
        carta_data = response.json()
        carta_nome = carta_data["nome"]

        nome_obra = f"*{carta_nome}* — {obra_nome}"

        # Converte o número do item para uma string e preenche com espaços à esquerda para alinhá-lo
        aligned_item_number = str(item_number).rjust(max_id_length)

        # Formata somente o ID e adiciona espaços para alinhar os pontos
        item_str = f"`{aligned_item_number}`. {nome_obra}"
        items.append(item_str)

    return items

def total_de_paginas(colecao, itens_por_pagina=15):
    total_itens = len(colecao)
    return (total_itens + itens_por_pagina - 1)
