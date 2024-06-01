from api.carta import Carta
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import f
import json

async def buscar_carta(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    usuario = update.message.from_user.id
    txt = texto.split()

    if len(txt) == 2 and txt[1].isdigit():
        nome = texto.split("ing ")[1]
        retorno = Carta.buscar_carta(nome, usuario)
        if "erro" in retorno:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma carta encontrada com esse ID. Se quiser, pode tentar por nome.</strong>", parse_mode="HTML")
        else:
            foto = retorno['carta']['imagem']
            nome = retorno['carta']['nome']
            acumulado = retorno['quantidade_acumulada']
            obra = retorno['carta']['obra_nome']
            cr = retorno['carta']['credito']
            caption_final = f"💳 | <a href='{cr}'>Cr</a>\n\n<code>{retorno['carta']['ID']}</code>. <strong>{nome}</strong> — <i>{obra}</i>\n\n(<code>x{acumulado}</code>)"
            await update.message.reply_photo(foto, caption=caption_final, parse_mode="HTML")

    elif len(txt) >= 2 and isinstance(texto.split("ing ")[1], str):
        retorno = Carta.buscar_carta_nome(texto.split("ing ")[1])
        if "erro" in retorno or len(retorno['cartas']) == 0:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma carta encontrada com esse nome.</strong>", parse_mode="HTML")
        else:
            caption = "<strong>🔎 Sua pesquisa:</strong>\n"
            caption += f.format_json(json.dumps(retorno['cartas']))
            #botoes = [InlineKeyboardButton("⬅️", callback_data="search_carta_anterior"), InlineKeyboardButton("➡️", callback_data="search_carta_proxima")]
            #teclado = InlineKeyboardMarkup([botoes])
            await update.message.reply_text(caption, parse_mode="HTML")
