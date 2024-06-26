from api.conta import Conta
from api.obra import Obra
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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

# retorna a mensagem de loja
async def atendente(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    mensagem = """
Opa! Aqui é o caixa!

O que gostaria de realizar?
    """

    botao = [
    [
        InlineKeyboardButton("🔄 Devolução", callback_data="iniciar_devolucao")
    ],
    [
        InlineKeyboardButton("🛍 Adquirir pedidos", callback_data="adquirir_pedidos")
    ],
    [
        InlineKeyboardButton("🎁 Presentear", callback_data="presentear")
    ],
    [
        InlineKeyboardButton("🫙 Ingredientes na vitrine", callback_data="ingredientes_vitrine")
    ]
    ]

    teclado = InlineKeyboardMarkup(botao)
    photo = "https://i.pinimg.com/originals/f2/82/08/f28208cdccf656bd4b800d065863c7e3.jpg"
    await update.message.reply_photo(photo, caption=mensagem, reply_markup=teclado)

# pergunta quais cartas quer remover
async def iniciar_devolucao(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    print("Blz pae, quais cartas?")
    return

# confirma se as cartas sao da pessoa
# manda uma msg de confirmacao para remover
async def confirmar_devolucao(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    # sim -> print("blz cara mas nao tem uma carta ai que nao ta na tua conta nao kkk melhore pf")
    # nao -> print("blz, bora, la, so confirma para mim se ta tudo ok.")
    return

# passando do outro, ele remove e da as moedas, enviando quantas ganhou e quantas tem agora
async def devolver(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    print("nao cara, pode crer, vou remover aqui e te dou essas migalhas aq pdp?")
    return
