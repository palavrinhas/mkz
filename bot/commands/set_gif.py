from api.conta import Conta
from api.carta import Carta
from telegram.ext import Updater, ContextTypes, CallbackContext

STATE_WAITING = 1

async def cancelar_gif(context: CallbackContext):
    chat = context.job
    await context.bot.send_message(chat_id=chat.chat_id, text="Bem, como você não me enviou a tempo o gif, eu cancelei a ação. Mas você pode tentar novamente. :)")

async def setar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    card_selected = Carta.buscar_carta(context.args[0], user_id)
    if card_selected['quantidade_acumulada'] < 40:
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i>Infelizmente, você não possui a quantidade de cartas suficientes para ter um gif personalizado. Considere girar/trocar para atingir a meta!</i>", parse_mode="HTML")
        return
    else:
        context.job_queue.run_once(cancelar_gif, 30, update.message.chat_id, chat_id=update.message.chat_id)
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="Ebaa! Você tem o suficiente. Agora, me envie em até <strong>30 segundos</strong> o gif desejado. Lembrando que ele precisa seguir as regras!", parse_mode="HTML")
        return STATE_WAITING

async def processar_gif(context: CallbackContext):
    chat = context.job
    await context.bot.send_message(chat_id=chat.chat_id, text="Gif recebido com sucesso! Aguarde o retorno.")
    return ConversationHandler.END
