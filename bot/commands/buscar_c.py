from api.carta import Carta
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import f, categoria
import json
from api.obra import Obra

async def buscar_carta(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    usuario = update.message.from_user.id
    txt = texto.split()

    if len(txt) == 2 and txt[1].isdigit():
        nome = texto.split("ing ")[1]
        retorno = Carta.buscar_carta(nome, usuario)
        if "Nenhuma carta" in retorno['message']:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma carta encontrada com esse ID. Se quiser, pode tentar por nome.</strong>", parse_mode="HTML")
        else:
            foto = retorno['carta']['imagem']
            nome = retorno['carta']['nome']
            acumulado = retorno['quantidade_acumulada']
            obra = retorno['carta']['obra_nome']
            cr = retorno['carta']['credito']
            emoji_cativeiro = categoria.get_emoji(acumulado)
            caption_final = f"💳 | <a href='{cr}'>Cr</a>\n\n<code>{retorno['carta']['ID']}</code>. <strong>{nome}</strong> — <i>{obra}</i>\n\n{emoji_cativeiro} (<code>x{acumulado}</code>)"
            if foto.endswith(".gif") or foto.endswith(".mp4"):
                await update.message.reply_animation(foto, caption=caption_final, parse_mode="HTML")
            else:
                await update.message.reply_photo(foto, caption=caption_final, parse_mode="HTML")

    # paginador de cartas pesquisadas goes brrrrrrr
    elif len(txt) >= 3 and context.args[0] == 'i' in txt and isinstance(texto.split("ing i ")[1], str):
        retorno = Carta.buscar_carta_nome_imagem(texto.split("ing i ")[1])
        termo = texto.split("ing i ")[1]

        if "erro" in retorno or len(retorno['cartas']) == 0:
            await update.message.reply_text("<strong>❗️ Erro: nenhum ingrediente encontrado com esse nome.</strong>", parse_mode="HTML")
        else:
            carta_inicial = retorno['cartas'][0]
            pagina_atual = retorno['paginaAtual']
            total_paginas = retorno['totalPaginas']

            foto = carta_inicial['imagem']
            carta_id = carta_inicial['ID']
            nome = carta_inicial['nome']
            obra = Obra.buscar_obra(carta_inicial['obra'])['nome']
            emoji_categoria = categoria.emoji(carta_inicial['categoria'])

            botoes = [
                InlineKeyboardButton("⬅️", callback_data=f"s_anterior_imagem_{pagina_atual - 1}_{usuario}_{termo}"),
                InlineKeyboardButton("➡️", callback_data=f"s_proxima_imagem_{pagina_atual + 1}_{usuario}_{termo}")
            ]

            teclado = InlineKeyboardMarkup([botoes])

            legenda = f"📒 — {pagina_atual}/{total_paginas}\n\n{emoji_categoria} <code>{carta_id}</code>. <strong>{nome}</strong> — <i>{obra}</i>"

            await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML", reply_markup=teclado)
            return

    elif len(txt) >= 2 and isinstance(texto.split("ing ")[1], str):
        retorno = Carta.buscar_carta_nome(texto.split("ing ")[1])
        if "erro" in retorno or len(retorno['cartas']) == 0:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma carta encontrada com esse nome.</strong>", parse_mode="HTML")
        else:
            caption = "<strong>🔎 Sua pesquisa:</strong>\n"
            caption += f.format_json(json.dumps(retorno['cartas']))
            await update.message.reply_text(caption, parse_mode="HTML")
