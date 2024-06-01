import json

def format_json(json_string):
    data = json.loads(json_string)

    # Encontrar o comprimento máximo do campo 'id' para formatação
    max_id_length = max(len(str(item['id'])) for item in data)

    formatted_result = ""
    for item in data:
        id_str = f"`{item['id']}`"
        formatted_result += f"{id_str.ljust(max_id_length + 2, ' ') + '.'} {item['nome']} - {item['obra_nome']}\n"

    return formatted_result

# Exemplo de uso:
json_string = '''
[
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 264,
      "nome": "Soyeon",
      "obra_nome": "(G)I-DLE"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 369,
      "nome": "Jaeyun",
      "obra_nome": "8TURN"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 781,
      "nome": "Orin Muto",
      "obra_nome": "AKB48"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 551,
      "nome": "JinJin",
      "obra_nome": "ASTRO"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 553,
      "nome": "Moonbin",
      "obra_nome": "ASTRO"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 155,
      "nome": "Jongho",
      "obra_nome": "ATEEZ"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 157,
      "nome": "Seonghwa",
      "obra_nome": "ATEEZ"
    },
    {
      "acumulado": 2,
      "categoria": "Música",
      "id": 161,
      "nome": "Yeosang",
      "obra_nome": "ATEEZ"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 583,
      "nome": "Ahyeon",
      "obra_nome": "BABYMONSTER"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 577,
      "nome": "Rora",
      "obra_nome": "BABYMONSTER"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 578,
      "nome": "Ruka",
      "obra_nome": "BABYMONSTER"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 109,
      "nome": "Jennie",
      "obra_nome": "BLACKPINK"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 139,
      "nome": "Sungho",
      "obra_nome": "BOYNEXTDOOR"
    },
    {
      "acumulado": 10000,
      "categoria": "Música",
      "id": 209,
      "nome": "Jungkook",
      "obra_nome": "BTS"
    },
    {
      "acumulado": 1,
      "categoria": "Música",
      "id": 538,
      "nome": "Suhyeon",
      "obra_nome": "Billlie"
    }
]
'''

formatted_numbers = format_json(json_string)
print(formatted_numbers)
