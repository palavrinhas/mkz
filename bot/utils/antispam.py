from telegram.ext import CallbackContext
import time
from api.obra import Obra
from api.conta import Conta
from telegram import InputMediaPhoto
from utils.f import formatar_obras_categoria, formatar_ids
import api.trocar as trocar_cmd
from utils import f
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import formatar
from requests import get
from utils import categoria
from api.carta import Carta
from utils import cartas_adquiridas

class ButtonHandler:
    def __init__(self, application):
        self.application = application
        self.user_button_interaction_time = {}
        self.ANTI_SPAM_TIME = 5

    @staticmethod
    def apply_anti_spam(func):
        async def wrapper(self, update, context: CallbackContext):
            user_id = update.effective_user.id
            button_id = func.__name__
            if self.anti_spam(user_id, button_id):
                await func(self, update, context)
                self.update_interaction_time(user_id, button_id)
            else:
                await update.callback_query.answer(show_alert=True, text='Espere 5s antes de apertar outro botão.')
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

        cartas_obra = Carta.cartas_da_obra(obra_id, pagina)
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
        txt = f"""<i>Pedido pronto!\nFaça bom proveito.</i>\n\n<code>{carta[0]["ID"]}</code>. <strong>{carta[0]["nome"]}</strong> — {obra["nome"]}\n\n(<code>{quantasTem}x</code>)"""
        await query.edit_message_media(media=InputMediaPhoto(media=carta[0]["imagem"], caption=txt, parse_mode="HTML"))

    @apply_anti_spam
    async def botao_de_sorteio(self, update, context: CallbackContext) -> None:
        query = update.callback_query
        print(query.data)
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
        print(pedido_aceito)

        msg = Conta.aceitar_pedido_gif(pedido_aceito)

        await query.edit_message_text(msg['mensagem'], parse_mode="HTML")

    async def recusar_pedido_gif(self, update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query
        pedido_recusado = data[2]

        msg = Conta.recusar_pedido_gif(pedido_recusado)

        await query.edit_message_text(msg['mensagem'], parse_mode="HTML")
