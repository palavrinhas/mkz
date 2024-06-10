from requests import get
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from api.obra import Obra
from api.filtro import ColecaoFiltros
from utils.formatar import FormatadorMensagem
from utils.f import formatar_ids

async def colecao(update: Updater, context: ContextTypes.DEFAULT_TYPE) -> None:
    usuario_id = update.message.from_user.id
    args = context.args

    if  len(args) == 0:
        conta = get(f"http://localhost:3000/colecao/{usuario_id}").json()

        if len(conta['colecao']) < 1:
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<strong>Você não tem cartas. Que tal girar e ganhar para começar a colecionar algumas?</strong>",parse_mode="HTML")
        else:
            final = f"🥞 | {conta['pagina_atual']}/{conta['total_paginas']}\n\n"
            voltar = InlineKeyboardButton("⬅️", callback_data=f'colecao_anterior_{usuario_id}_{conta["pagina_atual"] - 1}')
            ir = InlineKeyboardButton("➡️", callback_data=f'colecao_proximo_{usuario_id}_{conta["pagina_atual"] + 1}')
            botoes = [voltar, ir]
            teclado = InlineKeyboardMarkup([botoes])
            c = formatar_ids(conta['colecao'])
            final += f"{c}"
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text=final, reply_markup=teclado, parse_mode="HTML")

    elif args[0] == "f":
        obra = Obra.buscar_obra_nome(update.message.text.split("ci f ")[1])
        if "erro" in obra:
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i>Não encontrei nada. Tente outro nome.</i>", parse_mode="HTML")
            return
        else:
            obra_filtrada = obra['obras'][0]['ObraID']
            falta, faltantes_json, img = ColecaoFiltros.faltantes(usuario_id, obra_filtrada)
            if falta and faltantes_json['total_cartas'] <= 15:
                formatado, img = FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
                await update.message.reply_photo(reply_to_message_id=update.message.message_id, photo=img, caption=formatado, parse_mode="HTML")
            elif falta and faltantes_json['total_cartas'] > 15:

                botoes = [InlineKeyboardButton("⬅️", callback_data=f"faltantes_anterior_{usuario_id}_{faltantes_json['pagina_atual'] - 1}_{obra_filtrada}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"faltantes_proxima_{usuario_id}_{faltantes_json['pagina_atual'] + 1}_{obra_filtrada}_{faltantes_json['total_paginas']}")]
                teclado = InlineKeyboardMarkup([botoes])

                formatado, img = FormatadorMensagem.formatar_filtro_colecao(faltantes_json)
                await update.message.reply_photo(reply_to_message_id=update.message.message_id, photo=img, caption=formatado, parse_mode="HTML", reply_markup=teclado)
            else:
                await update.message.reply_photo(reply_to_message_id=update.message.message_id, photo=img, caption=faltantes_json, parse_mode="HTML")

    # aqui já é o filtro de que a pessoa possui
    elif args[0] == "s":
        obra = Obra.buscar_obra_nome(update.message.text.split("ci s ")[1])
        if "erro" in obra:
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i>Não encontrei nada. Tente outro nome.</i>", parse_mode="HTML")
            return
        else:
            obra_filtrada = obra['obras'][0]['ObraID']
            falta, possuo_json, img = ColecaoFiltros.possuo(usuario_id, obra_filtrada)
            if possuo_json['total_cartas'] == 0:
                await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<strong>😿 Você ainda não tem nenhuma carta!</strong>\nProcure usar o comando <code>/pedido</code> no privado para ganhar novas cartas.", parse_mode="HTML")
                return
            if falta and possuo_json['total_cartas'] <= 15:
                formatado, img = FormatadorMensagem.formatar_filtro_possui(possuo_json)
                await update.message.reply_photo(reply_to_message_id=update.message.message_id, photo=img, caption=formatado, parse_mode="HTML")
            elif falta and possuo_json['total_cartas'] > 15:
                botoes = [InlineKeyboardButton("⬅️", callback_data=f"possuo_anterior_{usuario_id}_{possuo_json['pagina_atual'] - 1}_{obra_filtrada}_{faltantes_json['total_paginas']}"), InlineKeyboardButton("➡️", callback_data=f"possuo_proxima_{usuario_id}_{possuo_json['pagina_atual'] + 1}_{obra_filtrada}_{possuo_json['total_paginas']}")]
                teclado = InlineKeyboardMarkup([botoes])
                formatado, img = FormatadorMensagem.formatar_filtro_possui(possuo_json)
                await update.message.reply_photo(reply_to_message_id=update.message.message_id, photo=img, caption=formatado, parse_mode="HTML", reply_markup=teclado)
            else:
                await update.message.reply_photo(reply_to_message_id=update.message.message_id, photo=img,caption=possuo_json, parse_mode="HTML")
