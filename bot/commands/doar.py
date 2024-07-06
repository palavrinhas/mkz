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

VALOR_DOADO = range(1)

async def doacao(update: Updater, context: ContextTypes.DEFAULT_TYPE):
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
    if update.message.text.isdigit() != True:
        await update.message.reply_text("<strong>Epa! Isso não é um número...</strong>", parse_mode="HTML")
        return ConversationHandler.END
    elif float(update.message.text) < 10.00:
        await update.message.reply_text("<strong>Ei, aceitamos doações somente a partir de</strong> <code>10R$</code>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"Show! Estou gerando o link de pagamento para essa doação de R${update.message.text}! Aguarde...")
        return ConversationHandler.END
