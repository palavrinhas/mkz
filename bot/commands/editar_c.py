from api.carta import Carta
from telegram.ext import Updater, ContextTypes
from api.conta import Conta

async def editar_carta(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if Conta.admin(update.message.chat.id):
        try:
            txt = update.message.text.split("editarcarta ")[1].split("|")
            conteudo = txt[0]
            tipo = int(txt[1])
            carta_id = txt[2]
            Carta.editar_carta(carta_id, tipo, conteudo)
            await update.message.reply_text(
                "😺 <i><strong>Obra editada com sucesso. Busque pelo ID para ver as mudanças!</strong></i>",
                parse_mode="HTML"
            )
            await update.message.reply_sticker("CAACAgQAAxkBAAEMHs1mRVgRXUkIPxIJwsEsmOlhiBJPrAACYwwAAuU48FM0xv9BCsV2IDUE")
        except:  # noqa: E722
            await update.message.reply_text(
                "⚠️ <i><strong>Epa... Ocorreu um erro. Verifique se está tudo certinho.</strong></i>",
                parse_mode="HTML"
            )
            await update.message.reply_sticker("CAACAgQAAxkBAAEMHs1mRVgRXUkIPxIJwsEsmOlhiBJPrAACYwwAAuU48FM0xv9BCsV2IDUE")
    else:
        return
