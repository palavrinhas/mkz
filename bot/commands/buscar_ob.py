from api.obra import Obra
from telegram.ext import Updater, ContextTypes
from utils import categoria, cartas_adquiridas
from requests import get
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import f, categoria
import json

async def buscar_obra(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    txt = texto.split()
    usuario = update.message.from_user.id

    if len(txt) == 3 and txt[2].isdigit():
        id_obra = texto.split("rc i ")[1]
        retorno = Obra.buscar_obra(int(id_obra))

        if "erro" in retorno:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma obra encontrada com esse ID. Se quiser, pode tentar pesquisar pelo nome e ver o ID.</strong>", parse_mode="HTML")
            return
        else:
            cartas_obra = get(f"http://localhost:3000/carta/obra/{id_obra}?user_id={usuario}&paginado=false").json()
            cartas = cartas_obra['cartas']

            total_paginas = cartas_obra['totalCartasObra']
            pagina_atual = 1

            obra = cartas_obra['obra']
            nome = cartas[0]['nome']
            carta_id = cartas[0]['ID']
            foto = cartas[0]["imagem"]
            cr = cartas[0]['creditos']
            acumulado = cartas[0]['acumulado']
            emoji_cativeiro = categoria.get_emoji(acumulado)

            botoes = [
                InlineKeyboardButton("⬅️", callback_data=f"anterior_imagem_{pagina_atual - 1}_{id_obra}"), InlineKeyboardButton("➡️", callback_data=f"proxima_imagem_{pagina_atual + 1}_{id_obra}")
            ]

            print(f"anterior_imagem_{pagina_atual - 1}_{id_obra}")

            teclado = InlineKeyboardMarkup([botoes])

            legenda = f"📒 — {pagina_atual}/{total_paginas}\n\n<code>{carta_id}</code>. <strong>{nome}</strong> — <i>{obra}</i>\n\n{emoji_cativeiro} (<code>x{acumulado}</code>)"

            await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML", reply_markup=teclado)
            return

    if len(txt) == 2 and txt[1].isdigit():
        nome = texto.split("rc ")[1]
        retorno = Obra.buscar_obra(nome)

        if "erro" in retorno:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma obra encontrada com esse ID. Se quiser, pode tentar por nome.</strong>", parse_mode="HTML")
            return
        else:
            categoricamente = categoria.emoji(retorno['categoria'])
            cartas_formatadas = ""
            cartas_obra = get(f"http://localhost:3000/carta/obra/{nome}?user_id={usuario}&paginado=true").json()
            nome = Obra.buscar_obra(retorno["ObraID"])["nome"]
            foto = retorno["imagem"]

            if cartas_obra['totalCartasObra'] <= 15:
                cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
                cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno["ObraID"], usuario)

                legenda = f"{categoricamente} — <strong>{nome}</strong> [<code>{retorno['ObraID']}</code>]\n<strong>🃏 — Total de cartas</strong>: <code>{cartas_obra['totalCartasObra']}</code>\n\nVocê possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>\n\n{cartas_formatadas}"

                await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML")
                return
            else:
                cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
                cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno["ObraID"], usuario)
                botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{retorno['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{retorno['ObraID']}_{cartas_obra['page'] + 1}")]
                teclado = InlineKeyboardMarkup([botoes])
                # eu acho desnecessario colocar o ID da obra, mas né... <code>{retorno['ObraID']}</code>. 
                legenda = f"""
{categoricamente} — <strong>{nome}</strong> [<code>{retorno['ObraID']}</code>]
<strong>🃏 — Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>
<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>

🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}

{cartas_formatadas}
                """
                await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML", reply_markup=teclado)
                return

    elif len(txt) >= 2 and isinstance(texto.split("rc ")[1], str):
        retorno = Obra.buscar_obra_nome(texto.split("rc ")[1])
        if "erro" in retorno:
            await update.message.reply_text("<i><strong>❗️ Erro: nenhuma obra encontrada com esse nome.</strong></i>", parse_mode="HTML")
            return
        else:
            quantidade_de_obras = len(retorno['obras'])
            formatado = ""
            pagina_atual = retorno['current_page']
            paginas = retorno['total_pages']

            if quantidade_de_obras == 1:
                categoricamente = categoria.emoji(retorno['obras'][0]['categoria'])
                cartas_formatadas = ""
                cartas_obra = get(f"http://localhost:3000/carta/obra/{retorno['obras'][0]['ObraID']}?user_id={usuario}&paginado=true").json()
                nome = retorno['obras'][0]['nome']
                foto = retorno['obras'][0]["imagem"]

                if cartas_obra['totalCartasObra'] <= 15:
                    cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
                    cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno["obras"][0]["ObraID"], usuario)
                    legenda = f"{categoricamente} — <strong>{nome}</strong> [<code>{retorno['obras'][0]['ObraID']}</code>] \n<strong>🃏 — Total de cartas</strong>: <code>{cartas_obra['totalCartasObra']}</code>\nVocê possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>\n\n{cartas_formatadas}"
                    await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML")
                else:
                    cartas_formatadas = f.formatar_obras_cartas(cartas_obra['cartas'])

                    cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno['obras'][0]["ObraID"], usuario)

                    botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{retorno['obras'][0]['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{retorno['obras'][0]['ObraID']}_{cartas_obra['page'] + 1}")]

                    teclado = InlineKeyboardMarkup([botoes])

                    legenda = f"""
{categoricamente} — <strong>{nome}</strong> [<code>{retorno['obras'][0]['ObraID']}</code>]
<strong>🃏 — Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>
<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>

🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}

{cartas_formatadas}
                """
                    await update.message.reply_photo(foto, caption=legenda, reply_markup=teclado,parse_mode="HTML")
                    return
            else:
                botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina_atual - 1}_{texto.split('rc ')[1]}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina_atual + 1}_{texto.split('rc ')[1]}")]
                formatado += f.formatar_obras_categoria(retorno['obras'])
                texto_final = f"🔎 {pagina_atual}|{paginas}\n{formatado}"
                teclado = InlineKeyboardMarkup([botoes])
                await update.message.reply_text(texto_final, reply_markup=teclado, parse_mode="HTML")
