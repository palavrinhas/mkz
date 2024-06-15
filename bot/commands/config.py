from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def configuracoes(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    mensagem = """Opa! Aqui temos as suas configurações do perfil."""
    perfil_privado = True
    notificar_giro = True
    botoes = [
                InlineKeyboardButton("🔒 Perfil Privado | ❌", callback_data="perfil_privado=true"),
                InlineKeyboardButton("🔊 Notificação de giro | ✅", callback_data="perfil_notifica=false")
            ]
    teclado = InlineKeyboardMarkup([botoes])
    await update.message.reply_text(
        text=mensagem,
        parse_mode="HTML",
        reply_markup=teclado
    )