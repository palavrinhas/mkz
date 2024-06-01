import requests
import json
import random

with open('obras.txt', 'r') as arquivo:
    for linha in arquivo:
        obra = linha.strip().split("|")
        obra_nome = obra[0]
        obra_categoria = obra[1]
        match obra_categoria:
            case 1:
                obra_categoria = "Filme"
            case 2:
                obra_categoria = "Série"
            case 3:
                obra_categoria = "Animação"
            case 4:
                obra_categoria = "Jogo"
            case 5:
                obra_categoria = "Música"
            case 6:
                obra_categoria = "Multi"
        obra_img = obra[2]

        headers = {'Content-type':'application/json'}
        parametros = {"Nome":obra_nome, "Categoria":obra_categoria, "Imagem":obra_img}
        response = requests.post("http://localhost:3000/cadastrar/obra",headers=headers,data=json.dumps(parametros)).text
        print(response)
