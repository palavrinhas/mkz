from api.carta import Carta
from typing import Union
from api.conta import Conta

class Troca:
    def possui(carta_dada: list[str], carta_recebida: list[str]) -> (bool, Union[str, dict], str):
        # carta_dada: [user_id, carta_id], carta_recebida: [user_id, carta_id]
        if carta_dada[0] == carta_recebida[0]:
            return False, "Se sentindo sozinho? Você precisa trocar com outra pessoa."
        else:
            c_dada = Carta.buscar_carta(carta_dada[1], carta_dada[0])
            c_recebida = Carta.buscar_carta(carta_recebida[1], carta_recebida[0])
            if c_dada['quantidade_acumulada'] < 1:
                return False, f"<strong><i>Não será possível realizar a troca pois você [{carta_dada[0]}] não possui a carta oferecida.</i></strong>"
            elif c_recebida['quantidade_acumulada'] < 1:
                return False, f"<strong><i>Não será possível realizar a troca pois você [{carta_recebida[0]}] não possui a carta oferecida.</i></strong>"
            else:
                return True, {'doador': [carta_dada[0], c_dada['carta']], 'recebedor': [carta_recebida[0], c_recebida['carta']]}

    def formatar_mensagem(troca: list[any], nomes: list[str]) -> (str, dict):
        mensagem = f"""
<i><strong>🛎 Pedido de troca!</strong></i>

<strong>{nomes[0]}</strong> <i>oferece</i>:

<code>{troca['doador'][1]['ID']}</code>. <strong>{troca['doador'][1]['nome']}</strong>

<strong>{nomes[1]}</strong> <i>dá em troca</i>:
<code>{troca['recebedor'][1]['ID']}</code>. <strong>{troca['recebedor'][1]['nome']}</strong>

<i>Por favor, confirme a troca. Ela pode ser recusada/cancelada por qualquer um dos envolvidos.</i>
        """
        return mensagem, troca

    def realizar_troca(trocar: list[any]) -> bool:
        Conta.remover_carta_colecao(trocar['doador'][0], int(trocar['doador'][1]))
        Conta.remover_carta_colecao(trocar['recebedor'][0], int(trocar['recebedor'][1]))
        Conta.adicionar_carta_colecao(trocar['doador'][0], int(trocar['recebedor'][1]))
        Conta.adicionar_carta_colecao(trocar['recebedor'][0], int(trocar['doador'][1]))
        return True
