from requests import get
from api.conta import Conta
from telegram.ext import Updater, ContextTypes

async def start(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if Conta.usuario_existe(user_id):
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i><strong>Seja Bem-vindo(a) de volta! O que temos para hoje?</strong></i>", parse_mode="HTML")
    else:
        get(f"http://localhost:3000/cadastrar/usuario/{user_id}")
        await update.message.reply_text(
            eply_to_message_id=update.message.message_id, 
            text="<i><strong>Seja muito bem-vindo(a) à Padocard! Eu te adicionei na lista de clientes e espero que sua experiência aqui seja magnífica <3</strong></i>",
            parse_mode="html"
        )
