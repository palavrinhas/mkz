from api.obra import Obra
from telegram.ext import Updater, ContextTypes
from utils import categoria, cartas_adquiridas
from requests import get
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import f
import json

async def buscar_obra(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    txt = texto.split()
    usuario = update.message.from_user.id

    if len(txt) == 2 and txt[1].isdigit():
        nome = texto.split("rc ")[1]
        retorno = Obra.buscar_obra(nome)
        if "erro" in retorno:
            await update.message.reply_text("<strong>❗️ Erro: nenhuma obra encontrada com esse ID. Se quiser, pode tentar por nome.</strong>", parse_mode="HTML")
        else:
            categoricamente = categoria.emoji(retorno['categoria'])
            cartas_formatadas = "\n"
            cartas_obra = get(f"http://localhost:3000/carta/obra/{nome}").json()
            nome = Obra.buscar_obra(retorno["ObraID"])["nome"]
            foto = retorno["imagem"]

            if cartas_obra['totalCartasObra'] <= 15:
                cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
                cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno["ObraID"], usuario)

                legenda = f"{categoricamente} —— <strong>{nome}</strong>\n<strong>🃏 —— Total de cartas</strong>: <code>{cartas_obra['totalCartasObra']}</code>\n\nVocê possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>\n\n{cartas_formatadas}"

                await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML")

            else:
                cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
                cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno["ObraID"], usuario)
                botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{retorno['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{retorno['ObraID']}_{cartas_obra['page'] + 1}")]
                teclado = InlineKeyboardMarkup([botoes])
                # eu acho desnecessario colocar o ID da obra, mas né... <code>{retorno['ObraID']}</code>. 
                legenda = f"""
{categoricamente} —— <strong>{nome}</strong>
<strong>🃏 —— Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>
<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>

🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}

{cartas_formatadas}
                """
                await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML", reply_markup=teclado)

    elif len(txt) >= 2 and isinstance(texto.split("rc ")[1], str):
        retorno = Obra.buscar_obra_nome(texto.split("rc ")[1])
        if "erro" in retorno:
            await update.message.reply_text("<i><strong>❗️ Erro: nenhuma obra encontrada com esse nome.</strong></i>", parse_mode="HTML")
        else:
            quantidade_de_obras = len(retorno['obras'])
            formatado = ""
            pagina_atual = retorno['current_page']
            paginas = retorno['total_pages']

            if quantidade_de_obras == 1:
                categoricamente = categoria.emoji(retorno['obras'][0]['categoria'])
                cartas_formatadas = "\n"
                cartas_obra = get(f"http://localhost:3000/carta/obra/{retorno['obras'][0]['ObraID']}").json()
                nome = retorno['obras'][0]['nome']
                foto = retorno['obras'][0]["imagem"]

                if cartas_obra['totalCartasObra'] <= 15:
                    cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
                    cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno["obras"][0]["ObraID"], usuario)
                    legenda = f"{categoricamente} — <strong>{nome}</strong>\n<strong>🃏 — Total de cartas</strong>: <code>{cartas_obra['totalCartasObra']}</code>\nVocê possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>\n{cartas_formatadas}"
                    await update.message.reply_photo(foto, caption=legenda, parse_mode="HTML")
                else:
                    cartas_formatadas = f.formatar_obras_cartas(cartas_obra['cartas'])
                    cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(retorno['obras'][0]["ObraID"], usuario)

                    botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{retorno['obras'][0]['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{retorno['obras'][0]['ObraID']}_{cartas_obra['page'] + 1}")]

                    teclado = InlineKeyboardMarkup([botoes])

                    legenda = f"""
{categoricamente} — <strong>{nome}</strong>
<strong>🃏 — Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>
<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>

🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}

{cartas_formatadas}
                """
                    await update.message.reply_photo(foto, caption=legenda, reply_markup=teclado,parse_mode="HTML")
            else:
                botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina_atual - 1}_{texto.split('rc ')[1]}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina_atual + 1}_{texto.split('rc ')[1]}")]
                formatado += f.format_obras(json.dumps(retorno['obras']))
                texto_final = f"🔎 {pagina_atual}|{paginas}\n{formatado}"
                teclado = InlineKeyboardMarkup([botoes])
                await update.message.reply_text(texto_final, reply_markup=teclado, parse_mode="HTML")
