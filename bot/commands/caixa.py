from api.conta import Conta
from api.carta import Carta
from utils.formatar import emoji
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from collections import Counter
from telegram.ext import  MessageHandler, filters, ConversationHandler, CallbackContext
from utils.antispam import ButtonHandler

VERIFICAR, CONFIRMO, DEVOLVER  = range(3)

# 4. Loja
# 4.1 A partir do comando /caixa ele escolhe entre os seguintes botões*:
# Devolução | Compra de Pedidos | Presentear | Ingredientes na Vitrine

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

class FormatarMSG:
    def confirmar(user_id, json):
        cartas = "Cartas para serem removidas:\n"
        for item in json:
            carta = Carta.buscar_carta(int(item), int(user_id))
            print(carta)
            emoji_ = emoji(carta['carta']['categoria'])
            cartas += f"{emoji_} <code>{carta['carta']['ID']}</code>. <strong>{carta['carta']['nome']}</strong> - <i>{carta['carta']['obra_nome']}</i>\n"
        msg = f"""{cartas}\nVocê tem certeza?\n\nSim ou Não?"""
        return msg

async def atendente(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        await update.message.reply_text("<strong>Esse comando é somente utilizável no privado.</strong>", parse_mode="HTML")
        return
    else:
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
    await update.callback_query.message.reply_text("➖ <strong>Não gostou de um ingrediente? A padoca aceita devolução!</strong>\nEnvie aqui a lista de IDs dos ingredientes que deseja devolver. Você pode devolver até <strong>10 ingredientes <i>de uma vez</i></strong>, e cada um deles vale <strong>1 moeda.</strong> 🪙", parse_mode="HTML")
    return VERIFICAR

# confirma se as cartas sao da pessoa & se tem somente 10 cartas
async def confirmar_devolucao(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    itens = update.message.text.split()
    context.user_data['cartas_vendidas'] = itens
    contador = Counter(itens)

    if any(contador[elemento] > 1 for elemento in contador):
        await update.message.reply_text("Você não pode repetir itens da lista. Ação cancelada.")
        return ConversationHandler.END
    if len(itens) > 10:
        await update.message.reply_text("Você pode enviar apenas 10 itens por venda. Ação cancelada.")
        return ConversationHandler.END
    for item in itens:
        r = Carta.buscar_carta(int(item), int(update.message.from_user.id))
        if r['quantidade_acumulada'] < 1:
            await update.message.reply_text(f"Erro: Você não possui o ingrediente ID {item}. Ação cancelada.")
            return ConversationHandler.END

    mensagem = FormatarMSG.confirmar(update.message.from_user.id, itens)
    await update.message.reply_text(mensagem, parse_mode="HTML")
    return DEVOLVER

# passando do outro, ele remove e da as moedas, enviando quantas ganhou e quantas tem agora
async def devolver(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "sim":
        moedas = len(context.user_data['cartas_vendidas'])
        m = Conta.add_moedas(update.message.from_user.id, moedas)['usuario']['moedas']
        for item in context.user_data['cartas_vendidas']:
            Conta.remover_carta_colecao(int(update.message.from_user.id), int(item))
        await update.message.reply_text(f"Show de bola! Ação concluída com sucesso.\n\nAgora você tem {m} moeda(s).")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"⚠ Ação cancelada. Nada ocorreu!", parse_mode="HTML")
        return ConversationHandler.END
