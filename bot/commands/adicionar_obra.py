from api.conta import Conta
from api.obra import Obra
from telegram.ext import Updater, ContextTypes

async def adicionar_obra(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if Conta.admin(update.message.chat.id):
        try:
            texto = update.message.text.split("aobra ")[1]
            info = texto.split("|")
            nome = Obra.criar_obra(info[0], int(info[1]), info[2])
            t = f"✅ Obra criada\nID: {nome}\nNome: {info[0]}"
            await update.message.reply_text(t, parse_mode="HTML")
        except:  # noqa: E722
            await update.message.reply_text("❗️ Ocorreu um erro.\n<i>Leia atentamente a descrição das instruções. Caso em dúvida, contate a administração principal.</i>", parse_mode="HTML")
