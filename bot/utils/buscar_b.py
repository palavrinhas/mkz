from requests import get
import json

def get_items_by_page(json_data, page_number):
    items_per_page = 15
    start_index = (page_number - 1) * items_per_page
    end_index = min(start_index + items_per_page, len(json_data))

    items = []
    for i in range(start_index, end_index):
        item = json_data[i]
        item_number = item["ObraID"]
        item_value = item["nome"]

        response = get(f"http://localhost:3000/obra/{item_number}")

        carta_nome = item["nome"]
        item_n = f"`{item_number:4d}`."
        nome_obra = f"*{carta_nome}*"
        item_str = f"{item_n} {nome_obra}"
        items.append(item_str)

    return items

def total_de_paginas(colecao, itens_por_pagina=15):
    total_itens = len(colecao)
    return (total_itens + itens_por_pagina - 1)
