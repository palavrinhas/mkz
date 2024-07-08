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
CHAT_ID_BETA = -1002088676726

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
        await update.message.reply_text(f"Show! Estou gerando o link de pagamento para essa doação de R${update.message.text}.")
        doacao = Doacao()
        response_server = doacao.criar_pagamento_livepix(update.message.text)
        print(response_server)
        mensagem = f"<strong>Eba! Seu pagamento foi gerado. Por favor, acesse o link abaixo, realize o pagamento. Eu irei detectar automaticamente o seu pagamento e já liberar suas features.</strong>\n\nLink: {response_server['data']['redirectUrl']}"
        donate_id = doacao.save_donate_log(update.message.from_user.id, response_server['data']['reference'])
        await update.message.reply_text(
                mensagem,
                parse_mode="HTML",
            )
        return ConversationHandler.END
