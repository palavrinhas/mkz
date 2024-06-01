from telegram.ext import Updater, ContextTypes
import json
from api.admin import Admin

with open('config.json', 'r') as arquivo:
    dados_json = json.load(arquivo)

async def dar_adm(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    arm = update.message.chat.id
    if dados_json['dono'] or dados_json['sub_dono'] or dados_json['dev'] == arm:
        r = Admin.criar_admin(update.message.text.split("set_admin ")[1])
        await update.message.reply_text(r)
    else:
        return