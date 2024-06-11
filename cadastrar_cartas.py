from requests import get, post
from bot.api.obra import Obra

with open("cartas.txt", "r") as file:
    for line in file:
        params = line.strip().split("|")
        print("ID:", params[0])
        nome = params[1]
        obra = params[2]
        imagem = params[3]
        creditos = params[4]
        categoria = Obra.buscar_obra(params[2])["categoria"]
        data = {"nome":nome, "obra":int(obra), "imagem":imagem, "categoria":categoria, "creditos":creditos}
        h = {"Content-type":"application/json"}
        f = post("http://localhost:3000/cadastrar/carta/", headers=h,json=data).json()
        print(f)
        print()
