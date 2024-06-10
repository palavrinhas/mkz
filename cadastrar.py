from requests import get, post

with open("obras.txt", "r") as file:
    for line in file:
        params = line.strip().split("|")
        print("ID:", params[0])
        nome = params[1]
        categoria = params[2]
        imagem = params[3]
        data = {"nome":nome, "categoria":categoria, "imagem":imagem}
        h = {"Content-type":"application/json"}
        f = post("http://localhost:3000/cadastrar/obra/", headers=h,json=data).json()
        print(f)
        print()
