from telegram.ext import Updater, ContextTypes
from api.obra import Obra
from utils.formatar import FormatadorMensagem

async def obs_categoria(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.message_id
    retorno = Obra.obras_da_categoria(context.args[0])
    if "erro" in retorno:
        await update.message.reply_text(reply_to_message_id=user_id, text="<i><strong>❌ A categoria fornecida é inválida. Tente novamente com outro indentificador.</strong></i>", parse_mode="HTML")
    else:
        mensagem = FormatadorMensagem.formatar_obras_categoria(retorno, context.args[0])
        await update.message.reply_text(reply_to_message_id=user_id, text=mensagem, parse_mode="HTML")
