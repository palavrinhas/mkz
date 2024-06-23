from requests import post, get
import httpx

class Carta:
    def criar_carta(nome, obra, imagem, creditos):
        js = {"nome":nome, "obra":int(obra), "imagem":imagem, "creditos":creditos}
        h = {"Content-type":"application/json"}
        r = httpx.post("http://localhost:3000/cadastrar/carta", headers=h, json=js).json()
        return r["cartaID"]

    def editar_carta(carta_id, tipo, conteudo):
        match tipo:
            case 1:
                t = "nome"
            case 2:
                t = "imagem"
            case 3:
                t = "creditos"
            case 4:
                t = "obra"
        js = {"tipo":t, "conteudo":conteudo}
        h = {"Content-type":"application/json"}
        r = httpx.post(f"http://localhost:3000/editar/carta/{carta_id}", headers=h, json=js).json()
        return r

    def buscar_carta_nome(nome: str) -> str:
        h = {"Content-type":"application/json"}
        n = {"termos":nome}
        r = httpx.post("http://localhost:3000/carta-nome/", headers=h, json=n).json()
        return r

    def buscar_carta_nome_imagem(nome: str, pagina=1) -> str:
        h = {"Content-type":"application/json"}
        n = {"termos":nome}
        r = httpx.post(f"http://localhost:3000/carta-nome/imagem/?pagina={pagina}", headers=h, json=n).json()
        return r

    def buscar_carta(carta_id, user_id):
        r = httpx.get(f"http://localhost:3000/carta/{carta_id}?user_id={str(user_id)}").json()
        return r

    def cartas_da_obra(obra_id, user_id, pagina=1):
        r = httpx.get(f"http://localhost:3000/carta/obra/{obra_id}?page={pagina}&user_id={user_id}").json()
        return r
