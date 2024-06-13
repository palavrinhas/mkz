from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def help(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    mensagem = """
<i>Opa! Você parece meio perdido... Acertei?</i>

<strong>Para verificar minhas funções disponíveis, reclamações e acompanhar as atualizações você pode utilizar os canais abaixo. Divirta-se! Meow 😸</strong> 
    """
    botoes = [
                InlineKeyboardButton("Tutorial Padoca", url="t.me/tutorialPadoca"),
                InlineKeyboardButton("Canal Oficial", url="t.me/padocard")
            ]
    teclado = InlineKeyboardMarkup([botoes])
    await update.message.reply_text(
        text=mensagem,
        parse_mode="HTML",
        reply_markup=teclado
    )
