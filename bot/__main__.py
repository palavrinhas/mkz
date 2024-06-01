import logging
from requests import get
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PrefixHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update  # noqa: F811
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters  # noqa: F811, F401
from api.conta import Conta
from api.obra import Obra
from api.carta import Carta
from commands import trocar_cmd, conta, start_cmd, giro, ci, buscar_c, buscar_ob, adicionar_carta, adicionar_obra, varias_c, bkp, set_adm, editar_c, editar_ob, set_fav, obras_categoria
from api.filtro import ColecaoFiltros
from utils import cartas_adquiridas
from telegram import InputMediaPhoto
from utils import categoria, formatar, f
from utils.antispam import rate_limited
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

@rate_limited(limit=1, interval=1)
async def button(update: Update, context: CallbackQueryHandler) -> None:
    query = update.callback_query

    match query.data:
        case "Filme":
            obras, botoes = Obra.sortear_obras(1)
            teclado = InlineKeyboardMarkup(botoes)
            await query.edit_message_caption(caption=f"📽 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
        case "Série":
            obras, botoes = Obra.sortear_obras(2)
            teclado = InlineKeyboardMarkup(botoes)
            await query.edit_message_caption(caption=f"🎞 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
        case "Animação":
            obras, botoes = Obra.sortear_obras(3)
            teclado = InlineKeyboardMarkup(botoes)
            await query.edit_message_caption(caption=f"✨ Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
        case "Jogo":
            obras, botoes = Obra.sortear_obras(5)
            teclado = InlineKeyboardMarkup(botoes)
            await query.edit_message_caption(caption=f"🎮 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
        case "Música":
            obras, botoes = Obra.sortear_obras(4)
            teclado = InlineKeyboardMarkup(botoes)
            await query.edit_message_caption(caption=f"🎶 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
        case "Multi":
            obras, botoes = Obra.sortear_obras(6)
            teclado = InlineKeyboardMarkup(botoes)
            await query.edit_message_caption(caption=f"🤔 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)

    if "colecao_proximo_" in query.data:
        await proxima_pagina(update, context)

    if "colecao_anterior_" in query.data:
        await pagina_anterior(update, context)

    if "proxima_obras_" in query.data:
        await pagina_obra_proxima(update, context)
    if "obras_anterior_" in query.data:
        await pagina_obra_anterior(update, context)

    if "obra_" in query.data:
        obra = query.data.split("obra_")[1]
        carta = Obra.sortear_carta_obra(obra)
        Conta.adicionar_carta_colecao(int(query.from_user.id), carta[0]['ID'])
        obra = Obra.buscar_obra(carta[0]['obra'])
        ide = str(carta[0]["ID"])
        quantasTem = Carta.buscar_carta(ide, int(query.from_user.id))['quantidade_acumulada']
        txt = f"""<i>Pagamento realizado com sucesso! Faça bom proveito do seu pedido.</i>\n\n<code>{carta[0]["ID"]}</code>. <strong>{carta[0]["nome"]}</strong> - {obra["nome"]}\n\n(<code>{quantasTem}x</code>)"""
        await query.edit_message_media(media=InputMediaPhoto(media=carta[0]["imagem"], caption=txt, parse_mode="HTML"))

    ############## handlers de paginar a pesquisa das obras ################
    if "proxima_search_obras_" in query.data:
        await pagina_obras_proxima(update, context)

    if "anterior_search_obras_" in query.data:
        await pagina_obras_anterior(update, context)

    ##################### handlers de troca ##########################
    if "trocar!_" in query.data:
        await aceitar_troca(update, context)

    if "nao_trocar_" in query.data:
        await nao_trocar(update, context)

    ################ faltantes e possui #######################
    if "faltantes_proxima_" in query.data:
        await faltante_proximo(update, context)

    if "faltantes_anterior_" in query.data:
        await faltante_anterior(update, context)
    
    if "possuo_proxima_" in query.data:
        await possuo_proximo(update, context)

    if "possuo_anterior_" in query.data:
        await possuo_anterior(update, context)

    ############## paginar as obras das categorias ##################
    if "obs_categoria_anterior_" in query.data:
        await obs_categoria_anterior(update, context)
    
    if "obs_categoria_proximo_" in query.data:
        await obs_categoria_proximo(update, context)

#################################################################################################
async def obs_categoria_anterior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    data = update.callback_query.data.split("_")

    categoria = data[3]
    pagina = data[4]

    if int(pagina) < 1:
        pagina = Obra.obras_da_categoria(categoria)['totalPages']
    else:
        pagina = pagina

    retorno = Obra.obras_da_categoria(categoria, pagina)

    mensagem = formatar.FormatadorMensagem.formatar_obras_categoria(retorno, categoria)
    botoes = [
        InlineKeyboardButton("⬅️", callback_data=f"obs_categoria_anterior_{categoria}_{retorno['currentPage'] - 1}"),
        InlineKeyboardButton("➡️", callback_data=f"obs_categoria_proximo_{categoria}_{retorno['currentPage'] + 1}")
    ]
    teclado = InlineKeyboardMarkup([botoes])
    await update.callback_query.edit_message_text(mensagem, reply_markup=teclado, parse_mode="HTML")

async def obs_categoria_proximo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    data = update.callback_query.data.split("_")
    categoria = data[3]
    pagina = data[4]

    if int(pagina) > Obra.obras_da_categoria(categoria)['totalPages']:
        pagina = 1
    else:
        pagina = pagina

    retorno = Obra.obras_da_categoria(categoria, pagina)

    mensagem = formatar.FormatadorMensagem.formatar_obras_categoria(retorno, categoria)
    botoes = [
        InlineKeyboardButton("⬅️", callback_data=f"obs_categoria_anterior_{categoria}_{retorno['currentPage'] - 1}"),
        InlineKeyboardButton("➡️", callback_data=f"obs_categoria_proximo_{categoria}_{retorno['currentPage'] + 1}")
    ]
    teclado = InlineKeyboardMarkup([botoes])
    await update.callback_query.edit_message_text(mensagem, reply_markup=teclado, parse_mode="HTML")

#################################################################################################

async def possuo_proximo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data.split("_")[2]
    info = [update.callback_query.data.split("_")[2], update.callback_query.data.split("_")[3], update.callback_query.data.split("_")[4], update.callback_query.data.split("_")[5]]

    falta, faltantes_json, msg = ColecaoFiltros.possuo(user_id, info[2], info[1])

    if info[1] > info[3]:
        pagina = 1
        falta, faltantes_json, msg = ColecaoFiltros.possuo(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_possui(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    elif info[1] == 0:
        pagina = info[3]
        falta, faltantes_json = ColecaoFiltros.possuo(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_possui(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    else:
        pagina = info[1]
        falta, faltantes_json, msg = ColecaoFiltros.possuo(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_possui(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, reply_markup=teclado, parse_mode="HTML")

async def possuo_anterior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data.split("_")[2]
    info = [update.callback_query.data.split("_")[2], update.callback_query.data.split("_")[3], update.callback_query.data.split("_")[4], update.callback_query.data.split("_")[5]]

    falta, faltantes_json, msg = ColecaoFiltros.possuo(user_id, info[2], info[1])

    if info[1] > info[3]:
        pagina = 1
        falta, faltantes_json, msg = ColecaoFiltros.possuo(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_possui(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    elif info[1] == 0:
        pagina = faltantes_json['total_paginas']
        print(pagina)
        falta, faltantes_json = ColecaoFiltros.possuo(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_possui(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    else:
        pagina = info[1]
        falta, faltantes_json, msg = ColecaoFiltros.possuo(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_possui(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, reply_markup=teclado, parse_mode="HTML")

##########################  Confirmação/cancelamento de trocas & faltantes ###############################
async def aceitar_troca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    data = update.callback_query.data.split("_")

    doador_id = data[1]
    doador_carta = data[2]
    recebedor_id = data[3]
    recebedor_carta = data[4]

    json = {'doador': [doador_id, doador_carta], 'recebedor':[recebedor_id, recebedor_carta]}
    if str(user_id) == recebedor_id:
        trocar_cmd.Troca.realizar_troca(json)
        await update.callback_query.edit_message_text("<strong><i>✅ Troca efetuada com sucesso. Aproveitem as novas cartas 😸</i></strong>", parse_mode="HTML")
    else:
        await update.callback_query.answer(text="Você não pode fazer isso. Fique na sua.")

async def nao_trocar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    ids = [update.callback_query.data.split("_")[2], update.callback_query.data.split("_")[3]]

    if str(user_id) in ids:
        await update.callback_query.edit_message_text(f"<strong><i>A troca foi cancelada pelo usuário [{user_id}] 😿</i></strong>", parse_mode="HTML")
    else:
        await update.callback_query.answer(text="Você não pode fazer isso. Fique na sua.")

async def faltante_proximo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    info = [update.callback_query.data.split("_")[2], update.callback_query.data.split("_")[3], update.callback_query.data.split("_")[4], update.callback_query.data.split("_")[5]]

    falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], info[1])

    if info[1] > info[3]:
        pagina = 1
        falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    elif info[1] == 0:
        pagina = info[3]
        falta, faltantes_json = ColecaoFiltros.faltantes(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    else:
        pagina = info[1]
        falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, reply_markup=teclado, parse_mode="HTML")

async def faltante_anterior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    info = [update.callback_query.data.split("_")[2], update.callback_query.data.split("_")[3], update.callback_query.data.split("_")[4], update.callback_query.data.split("_")[5]]

    falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], info[1])

    if int(info[1]) <= 0:
        pagina = faltantes_json['total_paginas']
        falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    elif info[1] == 0:
        pagina = info[3]
        falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, parse_mode="HTML", reply_markup=teclado)
    else:
        pagina = info[1]
        falta, faltantes_json, msg = ColecaoFiltros.faltantes(user_id, info[2], pagina)
        novo_texto, img = formatar.FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{user_id}_{faltantes_json['pagina_atual'] - 1}_{info[2]}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{user_id}_{faltantes_json['pagina_atual'] + 1}_{info[2]}_{faltantes_json['total_paginas']}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(novo_texto, reply_markup=teclado, parse_mode="HTML")

######################################## Coleção & Conta ##############################################
async def proxima_pagina(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    final = ""
    query = update.callback_query.data
    usuario_id = query.split("_")[2]
    pagina = query.split("_")[3]
    conta = get(f'http://localhost:3000/colecao/{usuario_id}?pagina={pagina}').json()

    if int(pagina) > conta['total_paginas']:
        pagina = 1

    conta = get(f'http://localhost:3000/colecao/{usuario_id}?pagina={pagina}').json()

    final = f"🥞 | {conta['pagina_atual']}/{conta['total_paginas']}\n\n"
    ir = InlineKeyboardButton("➡️", callback_data=f"colecao_proximo_{usuario_id}_{conta['pagina_atual'] + 1}")
    voltar = InlineKeyboardButton("⬅️", callback_data=f"colecao_anterior_{usuario_id}_{conta['pagina_atual'] - 1}")
    botoes = [voltar, ir]
    teclado = InlineKeyboardMarkup([botoes])
    final  += f.formatar_ids(conta['colecao'])
    await update.callback_query.edit_message_text(final, reply_markup=teclado, parse_mode="HTML")

async def pagina_anterior(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    final = ""
    query = update.callback_query.data
    usuario_id = query.split("_")[2]
    pagina = query.split("_")[3]
    conta = get(f'http://localhost:3000/colecao/{usuario_id}').json()

    if int(pagina) < 1:
        pagina = conta['total_paginas']
    elif int(pagina) > conta['total_paginas']:
        pagina = 1

    conta = get(f'http://localhost:3000/colecao/{usuario_id}?pagina={pagina}').json()

    final = f"🥞 | {conta['pagina_atual']}/{conta['total_paginas']}\n\n"
    ir = InlineKeyboardButton("➡️", callback_data=f"colecao_proximo_{usuario_id}_{conta['pagina_atual'] + 1}")
    voltar = InlineKeyboardButton("⬅️", callback_data=f"colecao_anterior_{usuario_id}_{conta['pagina_atual'] - 1}")
    botoes = [voltar, ir]
    teclado = InlineKeyboardMarkup([botoes])
    c = f.formatar_ids(conta['colecao'])
    final += c
    await update.callback_query.edit_message_text(final, reply_markup=teclado, parse_mode="HTML")

############################### paginar as buscas das obras por nome ###################################
async def pagina_obra_proxima(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    cartas_formatadas = ""
    obra_id = query.data.split("_")[2]
    pagina = query.data.split("_")[3]
    obra = Obra.buscar_obra(obra_id)
    categoricamente = categoria.emoji(obra['categoria'])
    cartas_obra = Carta.cartas_da_obra(obra_id, pagina)

    if int(pagina) > cartas_obra['totalPages']:
        pagina = 1
    else:
        pagina = pagina

    cartas_obra = Carta.cartas_da_obra(obra_id, pagina)
    nome = obra['nome']
    cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(obra_id, query.from_user.id)

    cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
    legenda = f"{categoricamente} — <strong>{nome}</strong>\n<strong>🃏 — Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>\n<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>\n\n🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}\n\n{cartas_formatadas}"
    botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{obra['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{obra['ObraID']}_{cartas_obra['page'] + 1}")]
    teclado = InlineKeyboardMarkup([botoes])
    await update.callback_query.edit_message_caption(legenda, reply_markup=teclado, parse_mode="HTML")

async def pagina_obra_anterior(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    cartas_formatadas = ""
    obra_id = query.data.split("_")[2]
    pagina = query.data.split("_")[3]
    obra = Obra.buscar_obra(obra_id)
    categoricamente = categoria.emoji(obra['categoria'])
    cartas_obra = Carta.cartas_da_obra(obra_id, pagina)

    if int(pagina) < 1:
        pagina = cartas_obra['totalPages']
    else:
        pagina = pagina

    cartas_obra = Carta.cartas_da_obra(obra_id, pagina)
    nome = obra['nome']
    cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(obra_id, query.from_user.id)
    cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
    legenda = f"{categoricamente} — <strong>{nome}</strong>\n<strong>🃏 — Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>\n<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>\n\n🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}\n\n{cartas_formatadas}"
    botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{obra['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{obra['ObraID']}_{cartas_obra['page'] + 1}")]
    teclado = InlineKeyboardMarkup([botoes])
    await update.callback_query.edit_message_caption(legenda, reply_markup=teclado, parse_mode="html")

############################### paginar as buscas das cartas por nome ###############################
async def pagina_obras_proxima(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    string = "_"
    pagina = int(query.data.split(string)[3])
    pattern = query.data.split(string)[4]
    nova_pagina = Obra.buscar_obra_nome(pattern)

    if pagina > nova_pagina['total_pages']:
        pagina = 1
    nova_pagina = Obra.buscar_obra_nome(pattern, pagina)

    obras = f.format_obras(json.dumps(nova_pagina['obras']))

    nova_legenda = f"🔎 {nova_pagina['current_page']}|{nova_pagina['total_pages']}\n{obras}"

    botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina - 1}_{pattern}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina + 1}_{pattern}")]
    teclado = InlineKeyboardMarkup([botoes])
    await update.callback_query.edit_message_text(nova_legenda, reply_markup=teclado, parse_mode="HTML")

async def pagina_obras_anterior(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    string = "_"
    pagina = int(query.data.split(string)[3])
    pattern = query.data.split(string)[4]
    nova_pagina = Obra.buscar_obra_nome(pattern)

    if pagina < 1:
        pagina = nova_pagina['total_pages']
    nova_pagina = Obra.buscar_obra_nome(pattern, pagina)
    obras = f.format_obras(json.dumps(nova_pagina['obras']))
    nova_legenda = f"🔎 {nova_pagina['current_page']}|{nova_pagina['total_pages']}\n{obras}"

    botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina - 1}_{pattern}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina + 1}_{pattern}")]
    teclado = InlineKeyboardMarkup([botoes])
    await update.callback_query.edit_message_text(nova_legenda, reply_markup=teclado, parse_mode="HTML")

if __name__ == '__main__':
    prefixos = ["!","/","."]

    #application = ApplicationBuilder().token('6975062896:AAHT_GqFRIWifT3JGFZ9_UCXCtmIacwvlzs').build()
    application = ApplicationBuilder().token("7051533328:AAFiEX6Zc963hIKB768UEOkDZ5qmAzYReR8").build()

    start_handler = CommandHandler('start', start_cmd.start)
    girar_handler = PrefixHandler(prefixos, 'assar', giro.girar_handler)
    conta_handler = PrefixHandler(prefixos, 'conta', conta.conta_usuario)
    troca_handler = PrefixHandler(prefixos, 'troca', trocar_cmd.troca)
    colecao_handler = PrefixHandler(prefixos, 'ci', ci.colecao)
    set_fav_handler = PrefixHandler(prefixos, 'fav', set_fav.setar)

    # handlers de busca de obras e cartas por nome e IDs
    procurar_obra = PrefixHandler(prefixos, 'rc', buscar_ob.buscar_obra)
    procurar_carta = PrefixHandler(prefixos, 'ing', buscar_c.buscar_carta)
    obras_categoria_handler = PrefixHandler(prefixos, 'p', obras_categoria.obs_categoria)

    # handlers de cadastro de obras e cartas
    add_obra = PrefixHandler(prefixos, 'aobra', adicionar_obra.adicionar_obra)
    add_carta = PrefixHandler(prefixos, 'acarta', adicionar_carta.adicionar_carta)
    varias_carta = PrefixHandler(prefixos, 'variascartas', varias_c.varias_cartas)

    # handlers de edição
    editar_c = PrefixHandler(prefixos, 'editarcarta', editar_c.editar_carta)
    editar_o = PrefixHandler(prefixos, 'editarobra', editar_ob.editar_obra)

    # handlers do dono
    adm = PrefixHandler(prefixos, 'set_admin', set_adm.dar_adm)
    bkp = PrefixHandler(prefixos, 'bkp', bkp.backup_db)

    # nhe, aqui é só para cadastrar os handlers, eu deixo embaralhado pq é meio foda-se mesmo
    application.add_handler(troca_handler)
    application.add_handler(obras_categoria_handler)
    application.add_handler(varias_carta)
    application.add_handler(bkp)
    application.add_handler(editar_o)
    application.add_handler(adm)
    application.add_handler(editar_c)
    application.add_handler(procurar_carta)
    application.add_handler(procurar_obra)
    application.add_handler(girar_handler)
    application.add_handler(start_handler)
    application.add_handler(conta_handler)
    application.add_handler(colecao_handler)
    application.add_handler(add_obra)
    application.add_handler(add_carta)
    application.add_handler(set_fav_handler)

    callback_tudo = CallbackQueryHandler(button)

    application.add_handler(callback_tudo)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
