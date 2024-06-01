import requests

def get_items_by_page(json_data, page_number):
    items_per_page = 15
    start_index = (page_number - 1) * items_per_page
    end_index = min(start_index + items_per_page, len(json_data))

    items = []
    for i in range(start_index, end_index):
        item_number = list(json_data.keys())[i]
        item_value = json_data[item_number]

        response = requests.get(f"http://localhost:3000/carta/{item_number}")
        carta_data = response.json()
        carta_nome = carta_data["nome"]
        item_str = f"`{item_number}`. *{carta_nome}* — (x{item_value})"
        items.append(item_str)
    return items

def total_de_paginas(colecao, itens_por_pagina=15):
    total_itens = len(colecao)
    return (total_itens + itens_por_pagina - 1) // itens_por_pagina
