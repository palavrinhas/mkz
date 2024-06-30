import httpx
import json

class Loja:
    def comprar_carta(user_id, carta_id):
        r = httpx.post(f"http://localhost:3000/comprar-carta?user_id={user_id}&carta_id={carta_id}").json()
        print(r)
        if "Compra realizada com sucesso!" in str(r):
            return True, [f"Compra realizada com sucesso! Aproveite seu novo card.\n\nAgora você tem {r['userCoins']} moeda(s) restante(s)."]
        elif "Moedas insuficientes" in str(r):
            return False, ["Epa! Moedas insuficientes. Você precisa de pelo menos 5 para comprar."]
        elif "Carta não disponível na loja" in str(r):
            return False, ["Ei.. Essa carta não está disponível. Tente novamente."]
        elif "Usuário já comprou esta carta" in str(r):
            return False, ["Epa! Você já comprou essa carta. Você pode comprar todas, porém, apenas 1 de cada."]

    def cartas_disponiveis():
        tabela_cartas = ""
        r = httpx.get("http://localhost:3000/loja").json()
        for carta in r['items']:
            tabela_cartas += f"{carta['emoji']} <code>{carta['carta_id']}</code>. <strong>{carta['nome_carta']}</strong> - <i>{carta['nome_obra']}</i>\n"
        return tabela_cartas, r['items']
