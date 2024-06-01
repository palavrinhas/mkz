from telegram.ext import ContextTypes, Updater
from api.trocar import Troca
from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # noqa: F811

async def troca(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    cartas = update.message.text.split(" ")
    user_id_doador = update.message.from_user.id
    user_id_recebedor  = update.message.reply_to_message['from']['id']

    if str(user_id_recebedor) == '7051533328':
        await update.message.reply_text("<i>Eu não posso trocar cartas :(</i>", parse_mode="HTML")
        return
    elif user_id_doador == user_id_recebedor:
        await update.message.reply_text("<i>Sentindo-se sozinho? Você precisa trocar com alguém.</i>", parse_mode="HTML")
        return

    nome_recebedor = update.message.reply_to_message['from']['first_name']
    nome_doador = update.message.from_user.first_name

    nomeclaturas = [nome_doador, nome_recebedor]

    carta_id_doador = cartas[1]
    carta_id_recebedor = cartas[2]

    retorno, mensagem = Troca.possui([user_id_doador, carta_id_doador], [user_id_recebedor, carta_id_recebedor])

    if retorno:
        msg, troca = Troca.formatar_mensagem(mensagem, nomeclaturas)
        ac = f"trocar!_{troca['doador'][0]}_{troca['doador'][1]['ID']}_{troca['recebedor'][0]}_{troca['recebedor'][1]['ID']}"
        na = f"nao_trocar_{troca['doador'][0]}_{troca['recebedor'][0]}"
        print(ac, na)
        botao = [
            [
        InlineKeyboardButton("✅", callback_data=ac),
        InlineKeyboardButton("❌", callback_data=na)
            ]
        ]
        teclado = InlineKeyboardMarkup(botao)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=teclado)
    else:
        await update.message.reply_text(mensagem, parse_mode="HTML")
