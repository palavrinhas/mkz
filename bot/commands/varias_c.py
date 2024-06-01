from telegram.ext import Updater, ContextTypes
from api.conta import Conta
from api.carta import Carta

async def varias_cartas(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if Conta.admin(update.message.chat.id):
            relatorio = "Final:\n\n"
            texto = update.message.reply_to_message.text.split("\n")
            for carta in texto:
                try:
                    info = carta.split("|")
                    nome = Carta.criar_carta(info[0], int(info[1]), info[2], info[3])
                    t = f"Carta criada\nID: {nome}\nNome: {info[0]}\n"
                    relatorio += t
                except:  # noqa: E722
                    relatorio += "Oops... Ocorreu um erro ao adicionar a carta. Verifique se as informações estão corretas."
            await update.message.reply_text(relatorio)
