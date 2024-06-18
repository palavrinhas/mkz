from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from api.conta import Conta
import httpx

# {
#   "mensagem": {
#     "user_id": "205749220",
#     "giros": 8,
#     "carta_fav": 0,
#     "banido": false,
#     "privado": false,
#     "trocar": false,
#     "premium": false,
#     "admin": false,
#     "moedas": 0,
#     "notificar": true,
#     "bio": "Olá! Eu estou usando a Padocard."
#   }
# }

async def cadastrar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    usuario = context.args[0]
    cadastro = httpx.get(f"http://localhost:3000/cadastrar/usuario/{usuario}").json()
    Conta.inserir_giros(usuario, 10000)
    mensagem = f"Usuário cadastrado.\n\nUser ID: {cadastro['mensagem']['user_id']}\nGiros: 10000"
    await update.message.reply_text(
        text=mensagem,
        parse_mode="HTML"
    )
