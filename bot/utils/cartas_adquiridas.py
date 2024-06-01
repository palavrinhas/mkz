from requests import get

# isso aqui de longe é uma forma decente de fazer, mas vai suprir as necessidades por enquanto...
# for dentro de for vtnc kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk

def cartas_ad(obra_id, user_id):
    cartas_adquiridas_obra = 0
    lista_adquiridas = []
    # pega as cartas da colecao kkk
    colecao = get(f"http://localhost:3000/colecao/bruta/{user_id}").json()

    # pega as cartas da obra xddddd
    cartas_obra = get(f"http://localhost:3000/carta/obra/{obra_id}?page=0").json()['cartas']

    # primeiro loop para cada carta na colecao...
    for carta_colecao in colecao:
        # segundo loop para cada carta da obra.....
        for carta_obra in cartas_obra:
            # se um ID da carta da colecao comparada for igual ao ID carta da obra, adiciona +1 porque
            # tem somente aquele ID específico e a lista é somente daquela obra. 
            if int(carta_colecao) == carta_obra["ID"]:
                cartas_adquiridas_obra += 1
                lista_adquiridas.append(carta_obra["ID"])

    # no final ele joga o valor final da comparação
    return cartas_adquiridas_obra, lista_adquiridas
