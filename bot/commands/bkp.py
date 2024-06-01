from telegram.ext import Updater, ContextTypes
from utils.backup import emissao_data

async def backup_db(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    db = "../padocard.db"
    data_emissao = emissao_data()
    await update.message.reply_document(
        document=db,
        caption=f"✨ <strong>Backup para o dono.</strong>\n<strong>📅 Emissão</strong> <blockquote>{data_emissao}</blockquote>",
        parse_mode="HTML"
    )
