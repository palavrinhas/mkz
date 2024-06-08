from api.carta import Carta
from telegram.ext import Updater, ContextTypes
from api.conta import Conta

async def adicionar_carta(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if Conta.admin(update.message.chat.id):
        try:
            texto = update.message.text.split("acarta ")[1]
            info = texto.split("|")
            nome = Carta.criar_carta(info[0], info[1], info[2].split(" ")[0], info[3])
            t = f"<strong>✅ Carta criada</strong>\n<strong>ID</strong>: {nome}\n<strong>Nome</strong>: {info[0]}"
            await update.message.reply_text(t, parse_mode="HTML")
        except:  # noqa: E722
            await update.message.reply_text("❗️ <strong>Ocorreu um erro.</strong>\n<i>Leia atentamente a descrição das instruções. Caso em dúvida, contate a administração principal.</i>", parse_mode="HTML")