from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from api.doacao import Doacao
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

VALOR_DOADO = range(1)
CHAT_ID_BETA = -1002158336777

def gerar_link_unico(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    novo_link = context.bot.create_chat_invite_link(
        chat_id=CHAT_ID_BETA,
        expire_date=None,
        member_limit=1,
        name="Welcome to the PadoCard!",
    )
    return novo_link

async def doacao(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        await update.message.reply_text("<strong>Espera. Faça isso no privado!</strong>", parse_mode="HTML")
        return ConversationHandler.END
    mensagem = """
😻 <strong>Muita gentileza sua!</strong>

<i>Fazendo uma doação, você ajuda a manter esse projeto de pé — Ou melhor, de patas — e usufrui de benefícios extras nos comandos presentes.</i>

<strong>Sabendo disso, envie o valor que deseja doar.</strong>
Obs: <i>coloque um número inteiro, sem vírgulas ou pontos.</i>
    """
    await update.message.reply_text(
        text=mensagem,
        parse_mode="HTML",
    )
    return VALOR_DOADO

async def check_donate(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    valores = [10, 12, 15, 20]
    if update.message.text.isdigit() != True:
        await update.message.reply_text("<strong>Epa! Isso não é um número...</strong>", parse_mode="HTML")
        return ConversationHandler.END
    elif int(update.message.text) not in valores:
        await update.message.reply_text("<strong>Ei, aceitamos doações somente a partir de</strong> <code>10R$</code>.\n<i>Valores de doações são: 10, 12, 15 e 20.</i>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"Show! Estou gerando o link de pagamento para essa doação de R${update.message.text}!")
        botao = [
        [
            InlineKeyboardButton("💰 Verificar pagamento", callback_data="")
        ], 
        ]
        teclado = InlineKeyboardMarkup(botao)
        doacao = Doacao()
        response_server = doacao.criar_pagamento_livepix(update.message.text)
        mensagem = f"<strong>Eba! Seu pagamento foi gerado. Por favor, acesse o link abaixo, realize o pagamento e aperte em 'Verificar pagamento'. Após isso, será gerado um link para você acessar o grupo de doadores e suas features extras serão liberadas. Pague em até 24h!</strong>\n\nLink: {response_server['data']['redirectUrl']}"
        await update.message.reply_text(
                mensagem,
                parse_mode="HTML",
                reply_markup=teclado
            )
        return ConversationHandler.END