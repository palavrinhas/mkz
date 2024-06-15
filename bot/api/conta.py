import httpx

class Conta:
    def usuario_existe(user_id: str) -> bool:
        r = httpx.get(f"http://localhost:3000/usuario/{user_id}").text
        if "erro" in r:
            retorno = False
        else:
            retorno = True
        return retorno

    def admin(user_id: str) -> bool:
        r = httpx.get(f"http://localhost:3000/usuario/{user_id}").json()
        return r["admin"]

    def buscar_usuario(user_id: str) -> str:
        r = httpx.get(f"http://localhost:3000/usuario/{user_id}").json()
        return r

    def inserir_giros(user_id: str, quantidade_giros: int) -> bool:
        return True

    def remover_giro(user_id: str) -> True:
        httpx.get(f"http://localhost:3000/giros/remover/{user_id}")
        return True

    def adicionar_carta_colecao(user_id: str, carta_id) -> str:
        data = {'item_id':carta_id}
        h = {'Content-Type':'application/json'}
        r = httpx.post(f"http://localhost:3000/colecao/{user_id}/adicionar", headers=h, json=data).json()
        return r

    def remover_carta_colecao(user_id: str, carta_removida: str) -> bool:
        data = {'item_id':carta_removida}
        #h = {'Content-Type':'application/json'}
        httpx.post(f"http://localhost:3000/colecao/{user_id}/remover", json=data).json()
        return True

    def buscar_colecao(user_id: str) -> str:
        r = httpx.get(f"http://localhost:3000/colecao/{user_id}").json()
        return r

    def buscar_colecao_bruta(user_id: str) -> str:
        r = httpx.get(f"http://localhost:3000/colecao/bruta/{user_id}").json()
        return r

    def carta_existe(carta_id: str) -> bool:
        r = httpx.get(f"http://localhost:3000/carta/{carta_id}").text
        if "nenhuma carta foi encontrada com esse ID." in r:
            retorno = False
        else:
            retorno = True
        return retorno

    def nao_esta_colecao(user_id: str, carta_id: str) -> bool:
        r1 = httpx.get(f"http://localhost:3000/colecao/{user_id}").text
        if f'"{carta_id}"' in r1:
            retorno = False
        else:
            retorno = True
        return retorno

    def setar_carta_favorita(user_id: str, carta_id: int) -> str:
        data = {'user':user_id, 'carta_fav':carta_id}
        h = {'Content-Type':'application/json'}
        retorno = httpx.post("http://localhost:3000/set-fav/", headers=h, json=data).json()
        if "Carta não encontrada" in retorno['message']:
            return "<strong>Carta não encontrada na sua coleção!</strong>"
        elif "Carta favorita atualizada com sucesso" in retorno['message']:
            return "<strong>Carta favorita setada com sucesso!</strong>"

    def criar_pedido_gif(user_id, msgid, carta_id, link):
        he = {"Content-Type":"application/json"}
        js = {"link":link}
        r = httpx.post(f"http://localhost:3000/criar-pedido/{user_id}/{msgid}/{carta_id}", headers=he, json=js).json()
        return r

    def aceitar_pedido_gif(pedido_id):
        r = httpx.get(f"http://localhost:3000/aceitar-pedido/{pedido_id}").json()
        return r

    def recusar_pedido_gif(pedido_id):
        r = httpx.get(f"http://localhost:3000/recusar-pedido/{pedido_id}").json()
        return r
