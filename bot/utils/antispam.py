from telegram.ext import CallbackContext
from telegram import Update
import time
from api.obra import Obra
from api.conta import Conta
from api.wishlist import Wishlist
from telegram import InputMediaPhoto
from utils.f import formatar_obras_categoria, formatar_ids
import api.trocar as trocar_cmd
from api.loja import Loja
from utils import f
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import formatar
from requests import get
from utils import categoria
from api.carta import Carta
from utils import cartas_adquiridas
from commands.wishlist import Formatar
from api.filtro import ColecaoFiltros
import httpx
import json
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

def create_buttons():
    json_data = httpx.get("http://localhost:3000/loja").json()

    items = json_data["items"]

    formatted_text = "<strong>Bem-vindo(a)! Esses estas são as opções disponíveis hoje:</strong>\n\n⚠️ <i>Lembre-se, você pode adquirir somente 1 de cada!</i>\n\n"
    obra_callbacks = []
    emojis = ["🧁", "🥣", "🥖", "🍞", "🍔", "🥪"] 

    for index, item in enumerate(items, start=1):
        emoji = emojis[index - 1]
        formatted_text += f"{emoji} — <strong>{item['nome_carta']}</strong> (<i>{item['nome_obra']}</i>)\n"
        obra_callbacks.append(InlineKeyboardButton(f"{emoji}", callback_data=f"comprar_{item['carta_id']}"))

    obra_callbacks_divided = [obra_callbacks[i:i+3] for i in range(0, len(obra_callbacks), 3)]

    return formatted_text, obra_callbacks_divided

class ButtonHandler:
    def __init__(self, application):
        self.application = application
        self.user_button_interaction_time = {}
        self.ANTI_SPAM_TIME = 4

    @staticmethod
    def apply_anti_spam(func):
        async def wrapper(self, update, context: CallbackContext):
            user_id = update.effective_user.id
            button_id = func.__name__
            if self.anti_spam(user_id, button_id):
                await func(self, update, context)
                self.update_interaction_time(user_id, button_id)
            else:
                await update.callback_query.answer(show_alert=True, text='Espere 4s antes de apertar outro botão.')
        return wrapper

    def anti_spam(self, user_id, button_id):
        current_time = time.time()
        last_interaction_time = self.user_button_interaction_time.get((user_id, button_id), 0)
        if current_time - last_interaction_time < self.ANTI_SPAM_TIME:
            return False
        else:
            return True

    def update_interaction_time(self, user_id, button_id):
        self.user_button_interaction_time[(user_id, button_id)] = time.time()

    async def pagina_obras_proxima(self, update, context: CallbackContext) -> None:
        query = update.callback_query
        string = "_"
        pagina = int(query.data.split(string)[3])
        pattern = query.data.split(string)[4]
        nova_pagina = Obra.buscar_obra_nome(pattern)

        if pagina > nova_pagina['total_pages']:
            pagina = 1
        nova_pagina = Obra.buscar_obra_nome(pattern, pagina)

        obras = formatar_obras_categoria(nova_pagina['obras'])

        nova_legenda = f"🔎 {nova_pagina['current_page']}|{nova_pagina['total_pages']}\n{obras}"

        botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina - 1}_{pattern}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina + 1}_{pattern}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_text(nova_legenda, reply_markup=teclado, parse_mode="HTML")
#################################################################################################
    async def obs_categoria_anterior(self, update, context: CallbackContext):
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

    async def obs_categoria_proximo(self, update, context: CallbackContext):
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

    async def possuo_proximo(self, update, context: CallbackContext):
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

    async def possuo_anterior(self, update, context: CallbackContext):
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
    async def aceitar_troca(self, update, context: CallbackContext):
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

    async def nao_trocar(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        ids = [update.callback_query.data.split("_")[2], update.callback_query.data.split("_")[3]]

        if str(user_id) in ids:
            await update.callback_query.edit_message_text(f"<strong><i>A troca foi cancelada pelo usuário [{user_id}] 😿</i></strong>", parse_mode="HTML")
        else:
            await update.callback_query.answer(text="Você não pode fazer isso. Fique na sua.")

    async def faltante_proximo(self, update, context: CallbackContext):
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

    async def faltante_anterior(self, update, context: CallbackContext):
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
    async def proxima_pagina(self, update, context: CallbackContext) -> None:
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
        final  += formatar_ids(conta['colecao'])
        await update.callback_query.edit_message_text(final, reply_markup=teclado, parse_mode="HTML")

    async def pagina_anterior(self, update, context: CallbackContext) -> None:
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
        c = formatar_ids(conta['colecao'])
        final += c
        await update.callback_query.edit_message_text(final, reply_markup=teclado, parse_mode="HTML")

############################### paginar as buscas das obras por nome ###################################
    async def pagina_obra_proxima(self, update, context: CallbackContext) -> None:
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

        cartas_obra = Carta.cartas_da_obra(obra_id, query.from_user.id, pagina)
        nome = obra['nome']
        cartas_que_tenho, adquiridas = cartas_adquiridas.cartas_ad(obra_id, query.from_user.id)

        cartas_formatadas += f.formatar_obras_cartas(cartas_obra['cartas'])
        legenda = f"{categoricamente} — <strong>{nome}</strong>\n<strong>🃏 — Total de cartas:</strong> <code>{cartas_obra['totalCartasObra']}</code>\n<i>Você possui <strong>{cartas_que_tenho}</strong> carta(s) de <strong>{cartas_obra['totalCartasObra']}</strong>.</i>\n\n🥘 | {cartas_obra['page']}/{cartas_obra['totalPages']}\n\n{cartas_formatadas}"
        botoes = [InlineKeyboardButton("⬅️", callback_data=f"obras_anterior_{obra['ObraID']}_{cartas_obra['page'] - 1}"), InlineKeyboardButton("➡️", callback_data=f"proxima_obras_{obra['ObraID']}_{cartas_obra['page'] + 1}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_caption(legenda, reply_markup=teclado, parse_mode="HTML")

    async def pagina_obra_anterior(self, update, context: CallbackContext) -> None:
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
    async def pagina_obras_proxima(self, update, context: CallbackContext) -> None:
        query = update.callback_query
        string = "_"
        pagina = int(query.data.split(string)[3])
        pattern = query.data.split(string)[4]
        nova_pagina = Obra.buscar_obra_nome(pattern)

        if pagina > nova_pagina['total_pages']:
            pagina = 1
        nova_pagina = Obra.buscar_obra_nome(pattern, pagina)

        obras = formatar_obras_categoria(nova_pagina['obras'])

        nova_legenda = f"🔎 {nova_pagina['current_page']}|{nova_pagina['total_pages']}\n{obras}"

        botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina - 1}_{pattern}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina + 1}_{pattern}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_text(nova_legenda, reply_markup=teclado, parse_mode="HTML")

    async def pagina_obras_anterior(self, update, context: CallbackContext) -> None:
        query = update.callback_query
        string = "_"
        pagina = int(query.data.split(string)[3])
        pattern = query.data.split(string)[4]
        nova_pagina = Obra.buscar_obra_nome(pattern)

        if pagina < 1:
            pagina = nova_pagina['total_pages']
        nova_pagina = Obra.buscar_obra_nome(pattern, pagina)
        obras = formatar_obras_categoria(nova_pagina['obras'])
        nova_legenda = f"🔎 {nova_pagina['current_page']}|{nova_pagina['total_pages']}\n{obras}"

        botoes = [InlineKeyboardButton("⬅️", callback_data=f"anterior_search_obras_{pagina - 1}_{pattern}"), InlineKeyboardButton("➡️", callback_data=f"proxima_search_obras_{pagina + 1}_{pattern}")]
        teclado = InlineKeyboardMarkup([botoes])
        await update.callback_query.edit_message_text(nova_legenda, reply_markup=teclado, parse_mode="HTML")

    @apply_anti_spam
    async def sortear_carta_obra(self, update, context: CallbackContext) -> None:
        query = update.callback_query
        obra = query.data.split("obra_")[1]
        carta = Obra.sortear_carta_obra(obra)
        Conta.adicionar_carta_colecao(int(query.from_user.id), carta[0]['ID'])
        obra = Obra.buscar_obra(carta[0]['obra'])
        ide = str(carta[0]["ID"])
        quantasTem = Carta.buscar_carta(ide, int(query.from_user.id))['quantidade_acumulada']
        txt = f"""<i>🛎 Pedido entregue! Aqui está:</i>\n\n<code>{carta[0]["ID"]}</code>. <strong>{carta[0]["nome"]}</strong> — {obra["nome"]}\n\n(<code>{quantasTem}x</code>)"""
        await query.edit_message_media(media=InputMediaPhoto(media=carta[0]["imagem"], caption=txt, parse_mode="HTML"))
        Wishlist.remover_geral(ide, query.from_user.id)

    @apply_anti_spam
    async def botao_de_sorteio(self, update, context: CallbackContext) -> None:
        query = update.callback_query
        match query.data:
            case "Sortear_Filme":
                obras, botoes = Obra.sortear_obras(1)
                teclado = InlineKeyboardMarkup(botoes)
                await query.edit_message_caption(caption=f"📽 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
            case "Sortear_Série":
                obras, botoes = Obra.sortear_obras(2)
                teclado = InlineKeyboardMarkup(botoes)
                await query.edit_message_caption(caption=f"🎞 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
            case "Sortear_Animação":
                obras, botoes = Obra.sortear_obras(3)
                teclado = InlineKeyboardMarkup(botoes)
                await query.edit_message_caption(caption=f"✨ Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
            case "Sortear_Jogo":
                obras, botoes = Obra.sortear_obras(5)
                teclado = InlineKeyboardMarkup(botoes)
                await query.edit_message_caption(caption=f"🎮 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
            case "Sortear_Música":
                obras, botoes = Obra.sortear_obras(4)
                teclado = InlineKeyboardMarkup(botoes)
                await query.edit_message_caption(caption=f"🎶 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)
            case "Sortear_Multi":
                obras, botoes = Obra.sortear_obras(6)
                teclado = InlineKeyboardMarkup(botoes)
                await query.edit_message_caption(caption=f"🤔 Prateleira à mostra! Por favor, confirme qual produto você procura nesta seção.\n\n{obras}", reply_markup=teclado)

    @apply_anti_spam
    async def aceitar_pedido_gif(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query
        pedido_aceito = data[2]

        msg = Conta.aceitar_pedido_gif(pedido_aceito)

        await query.edit_message_text(msg['mensagem'], parse_mode="HTML")

    async def recusar_pedido_gif(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query
        pedido_recusado = data[2]

        msg = Conta.recusar_pedido_gif(pedido_recusado)

        await query.edit_message_text(msg['mensagem'], parse_mode="HTML")

    async def anterior_imagem(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query

        pagina = int(data[2])
        obra = int(data[3])
        usuario = data[4]

        if pagina < 1:
            pagina = httpx.get(f"http://localhost:3000/carta/obra/imagem/{obra}?paginado=true&user_id={usuario}&page={pagina}").json()['totalCartasObra']
        else:
            pagina = pagina

        cartas_obra = httpx.get(f"http://localhost:3000/carta/obra/imagem/{obra}?paginado=true&user_id={usuario}&page={pagina}").json()

        botoes = [
                InlineKeyboardButton("⬅️", callback_data=f"anterior_imagem_{pagina - 1}_{obra}_{usuario}"), InlineKeyboardButton("➡️", callback_data=f"proxima_imagem_{pagina + 1}_{obra}_{usuario}")
            ]

        teclado = InlineKeyboardMarkup([botoes])
        emoji_cativeiro = categoria.get_emoji(cartas_obra['cartas'][0]['acumulado'])

        legenda = f"📒 — {pagina}/{cartas_obra['totalCartasObra']}\n\n<code>{cartas_obra['cartas'][0]['ID']}</code>. <strong>{cartas_obra['cartas'][0]['nome']}</strong> — <i>{cartas_obra['obra']}</i>\n\n{emoji_cativeiro} (<code>x{cartas_obra['cartas'][0]['acumulado']}</code>)"

        await query.edit_message_media(media=InputMediaPhoto(media=cartas_obra['cartas'][0]["imagem"], caption=legenda, parse_mode="HTML"), reply_markup=teclado)

    async def proxima_imagem(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query

        pagina = int(data[2])
        obra = int(data[3])
        usuario = data[4]
        total_paginas = httpx.get(f"http://localhost:3000/carta/obra/imagem/{obra}?paginado=true&user_id={usuario}&page={pagina}").json()['totalCartasObra']

        if pagina > int(total_paginas):
            pagina = 1
        else:
            pagina = pagina

        cartas_obra = httpx.get(f"http://localhost:3000/carta/obra/imagem/{obra}?paginado=true&user_id={usuario}&page={pagina}").json()

        botoes = [
                InlineKeyboardButton("⬅️", callback_data=f"anterior_imagem_{pagina - 1}_{obra}_{usuario}"), InlineKeyboardButton("➡️", callback_data=f"proxima_imagem_{pagina + 1}_{obra}_{usuario}")
            ]

        teclado = InlineKeyboardMarkup([botoes])

        emoji_cativeiro = categoria.get_emoji(cartas_obra['cartas'][0]['acumulado'])

        legenda = f"📒 — {pagina}/{cartas_obra['totalCartasObra']}\n\n<code>{cartas_obra['cartas'][0]['ID']}</code>. <strong>{cartas_obra['cartas'][0]['nome']}</strong> — <i>{cartas_obra['obra']}</i>\n\n{emoji_cativeiro} (<code>x{cartas_obra['cartas'][0]['acumulado']}</code>)"

        await query.edit_message_media(media=InputMediaPhoto(media=cartas_obra['cartas'][0]["imagem"], caption=legenda, parse_mode="HTML"), reply_markup=teclado)

    async def s_proxima_imagem(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query

        pagina = data[3]
        usuario = data[4]
        termo = data[5]

        t = Carta.buscar_carta_nome_imagem(termo)['totalPaginas']
        if int(pagina) > t:
            pagina = 1
        else:
            pagina = pagina
        
        retorno = Carta.buscar_carta_nome_imagem(termo, pagina=pagina)

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

        await query.edit_message_media(media=InputMediaPhoto(media=foto, caption=legenda, parse_mode="HTML"), reply_markup=teclado)

    async def s_anterior_imagem(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query

        pagina = data[3]
        usuario = data[4]
        termo = data[5]

        t = Carta.buscar_carta_nome_imagem(termo)['totalPaginas']

        if int(pagina) < 1:
            pagina = t
        else:
            pagina = pagina

        retorno = Carta.buscar_carta_nome_imagem(termo, pagina=pagina)

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

        await query.edit_message_media(media=InputMediaPhoto(media=foto, caption=legenda, parse_mode="HTML"), reply_markup=teclado)

    @apply_anti_spam
    async def perfil_privado(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query
        privar = query.data.split("_")[2]

        conta = Conta.buscar_usuario(user_id)

        notificar = "✅" if conta['notificar'] else "❌"        

        if privar == "False":
            botao = [
                    [InlineKeyboardButton(f"🔒 Privar Perfil | ✅", callback_data=f"privar_perfil_True")
                    ],
                    [InlineKeyboardButton("💬 Atualizar Bio", callback_data="atualizar_bio")
                    ],
                    [InlineKeyboardButton(f"🔊 Notificação de giro | {notificar}", callback_data=f"notificar_giros_{conta['notificar']}")
                ],
            ]
            teclado = InlineKeyboardMarkup(botao)
            Conta.perfil_privado(user_id, True)
            await query.edit_message_text("Opa! Aqui temos as suas configurações do perfil.", reply_markup=teclado)
        else:
            botao = [
                    [InlineKeyboardButton(f"🔒 Privar Perfil | ❌", callback_data=f"privar_perfil_False")
                    ],
                    [InlineKeyboardButton("💬 Atualizar Bio", callback_data="atualizar_bio")
                    ],
                    [InlineKeyboardButton(f"🔊 Notificação de giro | {notificar}", callback_data=f"notificar_giros_{conta['notificar']}")
                ],
            ]
            teclado = InlineKeyboardMarkup(botao)
            Conta.perfil_privado(user_id, False)
            await query.edit_message_text("Opa! Aqui temos as suas configurações do perfil.", reply_markup=teclado)

    @apply_anti_spam
    async def notificar(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query
        notificar = query.data.split("_")[2]
        conta = Conta.buscar_usuario(user_id)

        privado = "✅" if conta['privado'] else "❌"       

        if notificar == "False":
            botao = [
                    [InlineKeyboardButton(f"🔒 Privar Perfil | {privado}", callback_data=f"privar_perfil_{conta['privado']}")
                    ],
                    [InlineKeyboardButton("💬 Atualizar Bio", callback_data="atualizar_bio")
                    ],
                    [InlineKeyboardButton(f"🔊 Notificação de giro | ✅", callback_data=f"notificar_giros_True")
                ],
            ]

            teclado = InlineKeyboardMarkup(botao)
            await query.edit_message_text("Opa! Aqui temos as suas configurações do perfil.", reply_markup=teclado)
            Conta.notificar_giro(user_id, True)
        else:
            botao = [
                    [InlineKeyboardButton(f"🔒 Privar Perfil | {privado}", callback_data=f"privar_perfil_{conta['privado']}")
                    ],
                    [InlineKeyboardButton("💬 Atualizar Bio", callback_data="atualizar_bio")
                    ],
                    [InlineKeyboardButton(f"🔊 Notificação de giro | ❌", callback_data=f"notificar_giros_False")
                ],
            ]

            teclado = InlineKeyboardMarkup(botao)
            await query.edit_message_text("Opa! Aqui temos as suas configurações do perfil.", reply_markup=teclado)
            Conta.notificar_giro(user_id, False)


######### paginar a wl
    async def wl_p(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query

        wishlist_id = data[1]
        pagina = data[2]

        if int(pagina) > 2:
            pagina = 1
        else:
            pagina = pagina

        resposta = get(f"http://localhost:3000/wishlist/{wishlist_id}?page={pagina}").json()

        f = Formatar.formatar_lista(resposta)

        botao = [
    [
        InlineKeyboardButton("⬅️", callback_data=f"nwla_{resposta['wishlistItems'][0]['wishlist_id']}_{resposta['page'] - 1}"),
        InlineKeyboardButton("➡️", callback_data=f"nwlp_{resposta['wishlistItems'][0]['wishlist_id']}_{resposta['page'] + 1}")
    ],
    ]
        teclado = InlineKeyboardMarkup(botao)

        await query.edit_message_text(f, parse_mode="HTML", reply_markup=teclado)

    async def wl_a(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query

        wishlist_id = data[1]
        pagina = data[2]

        if int(pagina) < 1:
            pagina = 2
        else:
            pagina = pagina

        resposta = get(f"http://localhost:3000/wishlist/{wishlist_id}?page={pagina}").json()

        f = Formatar.formatar_lista(resposta)

        botao = [
    [
        InlineKeyboardButton("⬅️", callback_data=f"nwla_{resposta['wishlistItems'][0]['wishlist_id']}_{resposta['page'] - 1}"),
        InlineKeyboardButton("➡️", callback_data=f"nwlp_{resposta['wishlistItems'][0]['wishlist_id']}_{resposta['page'] + 1}")
    ],
    ]
        teclado = InlineKeyboardMarkup(botao)

        await query.edit_message_text(f, parse_mode="HTML", reply_markup=teclado)

    @apply_anti_spam
    async def mostrar_vitrine(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        query = update.callback_query
        texto_f, botao = create_buttons()
        teclado = InlineKeyboardMarkup(botao)
        await query.edit_message_caption(texto_f, parse_mode="HTML", reply_markup=teclado)

    @apply_anti_spam
    async def comprar_item_vitrine(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        query = update.callback_query
        data = update.callback_query.data.split("_")[1]
        resultado, mensagem = Loja.comprar_carta(update.callback_query.from_user.id, data)
        if resultado:
            final_ = Carta.buscar_carta(int(mensagem[1]['storeItem']['carta_id']), update.callback_query.from_user.id)
            final = f"{mensagem[0]}\n\n<code>{final_['carta']['ID']}</code>. <strong>{final_['carta']['nome']}</strong> — <i>{final_['carta']['obra_nome']}</i> (x<code>{final_['quantidade_acumulada']}</code>)"
            await query.edit_message_caption(final, parse_mode="HTML")
        else:
            await query.edit_message_caption(mensagem[0], parse_mode="HTML")
