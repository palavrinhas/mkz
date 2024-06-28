from api.conta import Conta
from api.carta import Carta
from utils.formatar import emoji
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from collections import Counter
from telegram.ext import  MessageHandler, filters, ConversationHandler, CallbackContext
from utils.antispam import ButtonHandler
from requests import get

VERIFICAR, CONFIRMO, DEVOLVER  = range(3)
CONFIRMAR_COMPRA_GIRO, CONFIRMAR_COMPRA_GIRO = range(2)
RECEBER_ID_PRESENTEADO, RECEBER_MSG_PRESENTE, RECEBER_CONFIRMACAO_PRESENTE, CONFIRMAR_PRESENTE = range(4)

# não tão complexo para criar
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


### mais complexo, preciso mexer na API, deixo por último.
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

    def chat_info(user_id):
        r = get(f"https://api.telegram.org/bot7051533328:AAEDAakd429GO9GtWU3MAVla7B0_lFV4b6Q/getChat?chat_id={user_id}").json()
        if r['ok'] != True:
            return False, "<i>Não encontrei o chat do usuário... Provavelmente ele me bloqueou :(</i>"
        else:
            return True, [r['result']['first_name'], r['result']['id']]

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

async def comprar_pedidos(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    moedas = Conta.buscar_usuario(update.callback_query.from_user.id)
    if moedas['moedas'] < 5:
        await update.message.reply_text("Você não tem moedas suficientes para comprar um pedido. Considere vender cartas para adquirir mais moedas!")
        return ConversationHandler.END
    else:
        context.user_data['usuario'] = update.callback_query.from_user.id
        await update.callback_query.message.reply_text(f"Você tem certeza que deseja comprar o pedido?\n\nVocê ficará com {moedas['giros'] + 1} giros e {moedas['moedas'] - 5} moeda(s).\nSim ou Não?")
        return CONFIRMAR_COMPRA_GIRO

async def finalizar_compra_giro(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "sim":
        Conta.rm_moedas(update.message.from_user.id, 5)
        Conta.inserir_giros(update.message.from_user.id, 1)
        giros_agora = Conta.buscar_usuario(update.message.from_user.id)['giros']
        await update.message.reply_text(f"✅ Compra realizada com sucesso.\nGiros: {giros_agora}")
        return ConversationHandler.END
    else:
        await update.message.reply_text("⚠ Ação cancelada. Não ocorreu nenhuma mudança.")
        return ConversationHandler.END

# nao aguento mais meu Deus do ceu vou morrer
async def iniciar_presente(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("🎁 Vamos enviar um presente! O correio já abriu e estou ansiosa para enviar as correspondências. Me diga, quem terá a sorte de ganhar um card hoje? 👀 Envie-me o ID do usuário que deseja presentear.")
    return RECEBER_ID_PRESENTEADO

async def receber_id_presenteado(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    existe, informacoes = FormatarMSG.chat_info(update.message.text)
    if existe and informacoes[1] != update.message.chat.id:
        await update.message.reply_text(f"💗 Que maravilha! Pesquisei no sistema e descobri que você quer presentear <a href='tg://user?id={informacoes[1]}'>{informacoes[0]}</a>, acertei? Por gentileza, me informe o ID da carta a ser entregue.", parse_mode="HTML")
        context.user_data['usuario_presenteado'] = update.message.text
        return RECEBER_MSG_PRESENTE
    elif informacoes[1] == update.message.chat.id:
        await update.message.reply_text("😾 <i>Espera... Você não pode enviar presentes para si mesmo!</i>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        await update.message.reply_text("😿 <i>Não encontrei o chat... Talvez o usuário me bloqueou.</i>", parse_mode="HTML")
        return ConversationHandler.END

async def receber_msg_presenteado(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['presente_id'] = update.message.text
    await update.message.reply_text("✨ Você quer incluir uma mensagem para o destinatário? Se sim, envie a mensagem - se não, dê /skip. Use sua criatividade!")
    return RECEBER_CONFIRMACAO_PRESENTE

# pula a fase de mandar uma mensagem com (/skip)
async def skip_mensagem(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mensagem"] = "Nada informado!"
    await update.message.reply_text("Sutil, hein? Sem problemas.")
    return RECEBER_CONFIRMACAO_PRESENTE

async def confirmar_presente(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["mensagem"] == "":
        context.user_data['mensagem'] == "Não informada."
    msg_confirma = f"""
<strong>Até agora, essas são as informações:</strong>

🪪 <strong>Usuário:</strong> <code>{context.user_data['usuario_presenteado']}</code>
🎁 <strong>Presente:</strong> <code>{context.user_data['presente_id']}</code>
📄 <strong>Mensagem:</strong> <code>{context.user_data['mensagem']}</code>

Você confirma o envio?
    """
    await update.message.reply_text(msg_confirma, parse_mode="HTML")
    return CONFIRMAR_PRESENTE

async def confirmar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💓 Presente enviado!")
    return ConversationHandler.END