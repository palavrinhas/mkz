import json
from utils.categoria import emoji, get_emoji

def format_json(json_string):
    f = ""
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return "", str(e)
    
    if not isinstance(data, list):
        return "", "Formato de JSON não suportado."

    # Obter os comprimentos máximos dos IDs para alinhamento
    max_id_length = max(len(str(item["ID"])) for item in data)

    formatted_output = []
    for item in data:
        id = str(item.get("ID", ""))
        nome = item.get("nome", "")
        spaces = max_id_length - len(id)
        formatted_output.append(f"{' ' * spaces}<code>{id}</code>. <strong>{nome}</strong>")
    
    for carta in formatted_output:
        f += f"\n{carta}"

    return f

####################### FUNCAO ABENCOADA POR >>>>>>>>>>>>>>>DEUS<<<<<<<<<<<<<< ################
def formatar_ids(data):
    max_length_id = max(len(str(item['id'])) for item in data)

    formatted_data = ""
    print(data)
    for item in data:
        id_str = str(item['id'])
        emj = emoji(item['categoria'])
        emoji_cat = get_emoji(item['acumulado'])
        padding_spaces = ' ' * (max_length_id - len(id_str))
        formatted_data += f"\n{emj}     <code>{padding_spaces}</code><code>{id_str}</code>. <strong>{item['nome']}</strong> {emoji_cat} — <i>{item['obra_nome']}</i>"
    return formatted_data

def formatar_obras_cartas(data):
    max_length_id = max(len(str(item['ID'])) for item in data)
    formatted_data = []
    for item in data:
        emoji_cat = get_emoji(item['acumulado'])
        id_str = str(item['ID'])
        padding_spaces = ' ' * (max_length_id - len(id_str))
        formatted_data.append(f"<code>{padding_spaces}</code><code>{id_str.rjust(len(id_str))}</code>. <strong>{item['nome']}</strong> {emoji_cat}")
    return "\n".join(formatted_data)

def formatar_obras_categoria(data):
    max_length_id = max(len(str(item['ObraID'])) for item in data)
    formatted_data = []

    for item in data:
        id_str = str(item['ObraID'])
        padding_spaces = ' ' * (max_length_id - len(id_str))
        formatted_data.append(f"<code>{padding_spaces}</code><code>{id_str.rjust(len(id_str))}</code>. <strong>{item['nome']}</strong>")
    return "\n".join(formatted_data)