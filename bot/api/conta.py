import httpx
from api.carta import Carta

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
        js = {"giros":int(quantidade_giros)}
        h = {"content-type":"application/json"}
        r = httpx.post(f"http://localhost:3000/inserir/giros/{user_id}", headers=h, json=js).json()
        return r

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

    def perfil_privado(conta, privar):
        r = httpx.get(f"http://localhost:3000/usuario/privado/{conta}?privar={privar}").json()
        return r

    def notificar_giro(conta, notificar):
        r = httpx.get(f"http://localhost:3000/usuario/notificar/{conta}?notificar={notificar}").json()
        return r
    
    def definir_bio(conta, texto):
        h = {"Content-type":"application/json"}
        js = {"bio":texto}
        r = httpx.post(f"http://localhost:3000/bio/{conta}", headers=h, json=js).json()
        return r

    def add_moedas(user_id, quantidade):
        r = httpx.get(f"http://localhost:3000/moeda/?tipo=adicionar&quantidade={quantidade}&usuario={user_id}").json()
        return r

    def rm_moedas(user_id, quantidade):
        r = httpx.get(f"http://localhost:3000/moeda/?tipo=remover&quantidade={quantidade}&usuario={user_id}").json()
        return r

    def enviar_presente(remetente, destinatario, presente_id, mensagem="Não informada."):
        Conta.remover_carta_colecao(int(remetente), int(presente_id))
        Conta.adicionar_carta_colecao(int(destinatario), int(presente_id))
        carta = Carta.buscar_carta(presente_id, destinatario)
        retorno = f"""
💝 Eba! Um usuário te mandou um presente:

🎁 {carta['carta']['ID']}. {carta['carta']['nome']} - {carta['carta']['obra_nome']}

💌 Mensagem: {mensagem}
        """
        return retorno