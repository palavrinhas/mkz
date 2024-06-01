from telegram.ext import Updater, ContextTypes
from api.conta import Conta

async def setar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    ctx = context.args

    if update.message.chat.type != "private":
        return
    else:
        if len(ctx) < 1:
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<strong>Você precisa me informar a carta favorita. Tente:</strong> <code>/fav 1</code>", parse_mode="HTML")
        elif ctx[0] == "0":
            Conta.setar_carta_favorita(str(user_id), 0)
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i>Ok! Não há mais carta favoritada em seu perfil.</i>", parse_mode="HTML")
        else:
            r = Conta.setar_carta_favorita(str(user_id), int(ctx[0]))
            await update.message.reply_text(r, parse_mode="HTML")
