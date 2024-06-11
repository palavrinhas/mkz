from api.conta import Conta
from api.carta import Carta
from telegram.ext import Updater, ContextTypes, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json
from utils.file_size import tamanho_arquivo_aceitavel

with open('config.json', 'r') as arquivo:
    dados_json = json.load(arquivo)

async def setar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    card_selected = Carta.buscar_carta(context.args[0], user_id)
    lnk = str(context.args[1])

    if "Nenhuma carta foi encontrada com esse ID." in card_selected['message']:
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="Irmão, essa carta sequer existe. Verifique pesquisando por ela.")
        return
    elif card_selected['quantidade_acumulada'] < 40:
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i>Infelizmente, você não possui a quantidade de cartas suficientes para ter um gif personalizado. Considere girar/trocar para atingir a meta!</i>", parse_mode="HTML")
        return
    else:
        if tamanho_arquivo_aceitavel(lnk):
            try:
                user = update.message.from_user.id
                pedido = Conta.criar_pedido_gif(user, update.message.message_id, card_selected['carta']['ID'], lnk)
                txt = f"Pedido #{pedido['mensagem']['id_pedido']}\n\nUser: {pedido['mensagem']['user_id']}\nCarta ID: {pedido['mensagem']['carta_id']}\nGif Link: {pedido['mensagem']['gif_link']}"
                botoes = [InlineKeyboardButton("✅", callback_data=f"aceitar_pedido_{pedido['mensagem']['id_pedido']}"), InlineKeyboardButton("❌", callback_data=f"recusar_pedido_{pedido['mensagem']['id_pedido']}")]
                teclado = InlineKeyboardMarkup([botoes])
                await update._bot.send_message(chat_id=dados_json['aprovar_gif'], text=txt, reply_markup=teclado)
                await update.message.reply_text(text="Gif recebido com sucesso! Aguarde o retorno.")
                return
            except:
                await update.message.reply_text("Ocorreu um erro na tentativa de criar o pedido. Reporte para a administração ou @crzbyte (De forma detalhada!).")
                return
        else:
            await update.message.reply_text(text="Erro: verifique se o gif atende as regras. Ação cancelada.")
        return
