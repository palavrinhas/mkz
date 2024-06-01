def format_data(data):
    max_length_id = max(len(str(item['id'])) for item in data)

    formatted_data = "```\n"  # Iniciar bloco de código
    for item in data:
        id_str = f"{str(item['id'])}".rjust(max_length_id)
        formatted_data += f"{id_str}. {item['nome']} - {item['obra_nome']}\n"
    formatted_data += "```"  # Fechar bloco de código

    return formatted_data

if __name__ == "__main__":
    json_data = [
        {'acumulado': 1, 'categoria': 'Música', 'id': 1500, 'nome': 'Soyeon', 'obra_nome': '(G)I-DLE'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 1000, 'nome': 'Jaeyun', 'obra_nome': '8TURN'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 78, 'nome': 'Orin Muto', 'obra_nome': 'AKB48'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 5, 'nome': 'JinJin', 'obra_nome': 'ASTRO'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 553, 'nome': 'Moonbin', 'obra_nome': 'ASTRO'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 155, 'nome': 'Jongho', 'obra_nome': 'ATEEZ'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 157, 'nome': 'Seonghwa', 'obra_nome': 'ATEEZ'},
        {'acumulado': 2, 'categoria': 'Música', 'id': 161, 'nome': 'Yeosang', 'obra_nome': 'ATEEZ'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 159, 'nome': 'Yunho', 'obra_nome': 'ATEEZ'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 583, 'nome': 'Ahyeon', 'obra_nome': 'BABYMONSTER'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 577, 'nome': 'Rora', 'obra_nome': 'BABYMONSTER'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 578, 'nome': 'Ruka', 'obra_nome': 'BABYMONSTER'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 109, 'nome': 'Jennie', 'obra_nome': 'BLACKPINK'},
        {'acumulado': 1, 'categoria': 'Música', 'id': 139, 'nome': 'Sungho', 'obra_nome': 'BOYNEXTDOOR'},
        {'acumulado': 10000, 'categoria': 'Música', 'id': 209, 'nome': 'Jungkook', 'obra_nome': 'BTS'}
    ]

    formatted_ids = format_data(json_data)
    print(formatted_ids)
