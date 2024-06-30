import httpx
import json

class Loja:
    def comprar_carta(user_id, carta_id):
        r = httpx.post(f"http://localhost:3000/comprar-carta?user_id={user_id}&carta_id={carta_id}").json()
        if "Compra realizada com sucesso!" in str(r):
            return True, [f"<strong>Compra realizada com sucesso! Aproveite seu novo card.</strong>\n\n<i>Agora você tem <code>{r['userCoins']}</code> moeda(s) restante(s).</i>", r]
        elif "Moedas insuficientes" in str(r):
            return False, ["<strong>Epa! Moedas insuficientes. Você precisa de pelo menos 5 para comprar algo.</strong>"]
        elif "Carta não disponível na loja" in str(r):
            return False, ["<i>Ei.. Essa carta não está disponível. Tente novamente.</i>"]
        elif "Usuário já comprou esta carta" in str(r):
            return False, ["<strong>Epa! Você já comprou essa carta. Você pode comprar todas, porém, apenas <i>1 de cada.</i></strong>"]

    def cartas_disponiveis():
        tabela_cartas = ""
        r = httpx.get("http://localhost:3000/loja").json()
        for carta in r['items']:
            tabela_cartas += f"{carta['emoji']} <code>{carta['carta_id']}</code>. <strong>{carta['nome_carta']}</strong> - <i>{carta['nome_obra']}</i>\n"
        return tabela_cartas, r['items']
