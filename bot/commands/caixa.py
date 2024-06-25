from api.conta import Conta
from api.obra import Obra
from telegram.ext import Updater, ContextTypes

# 4. Loja
# 4.1 A partir do comando /caixa ele escolhe entre os seguintes botões*:
# Devolução | Compra de Pedidos | Presentear | Ingredientes na Vitrine
# 4.2 Devolução = Venda de cartas.
# “Não gostou de um ingrediente? A padoca aceita devolução! Envie aqui a lista de IDs dos ingredientes que deseja devolver. Você pode devolver até 10 ingredientes de uma vez, e cada um deles vale uma moeda.”
# O comando deve:
#     → Aceitar somente até 10 IDs para a venda;
#     → Checar se o usuário possui os IDs fornecidos;
#     → Remover as cartas da conta;
#     → Adicionar dinheiro para a conta, equivalente a quantidade de cartas removidas;
# → Após o procedimento, aceitar um novo requisito de venda somente após 30 segundos.

# 4.3 Para a Compra de Pedidos (giros), o bot vai exibir que cada Pedido Novo custa 5 moedas, exibir quantas ela tem e perguntar se ele confirma a compra. A partir disso:
#     → Ele remove a quantidade de moedas da conta;
#     → Depois adiciona 1 giro para a conta.

# 4.4 Presentear = Retirar uma carta da conta do usuário e enviar para outro.
# O comando deve:
#     → Receber o ID inserido pelo usuário;
#     → Checar se o player tem essa carta;
#        → Se False, ele retorna "Você não possui esse ingrediente no seu carrinho... Tente novamente.";
#        → Caso True, ele pedirá o usuário de quem vai presentear;
#     → Perguntar se a pessoa deseja mandar um recado junto ao presente;
#        → Caso não queira, que envie um X. (Ou você cria um botão junto da mensagem que diz "sem recado" pro negócio dar False sozinho, o que for melhor);
#     → Perguntar se o usuário confirma o envio do presente;
#     → Remover a carta da conta;
#     → Remover também 10 moedas;
#     → Adicionar a carta na conta do presenteado;
#     → Notificar o presenteado.

# 4.5 Ingredientes na Vitrine = Cartas pra comprar.
# Ao clicar nesse botão o bot vai:
#     → Exibir as cartas que o bot escolheu pra estarem disponíveis;
#     → Permitir a pessoa a escolher 1 carta e confirmar a compra;
#     → Remover 5 moedas da conta;
#     → Adicionar aquela carta pra coleção.

async def atendente(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    return
