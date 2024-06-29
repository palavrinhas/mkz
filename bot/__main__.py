import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PrefixHandler
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackContext
from commands import trocar_cmd, conta, start_cmd, giro, ci, buscar_c, buscar_ob, adicionar_carta, adicionar_obra, varias_c, set_adm, editar_c, editar_ob, set_fav, obras_categoria, set_gif, ajuda, config, criar_user, wishlist, caixa
from commands.wishlist import INICIAR, DAR_NOME_WL, CARTAS_PARA_WL, APAGAR_WL, QUAL_WL, CONFIRMAR, QUAL_WL_ADD, FINALIZAR, QUAL_WL_DL, CONFIRMAR_DL
from commands.caixa import VERIFICAR, CONFIRMO, DEVOLVER, CONFIRMAR_COMPRA_GIRO, RECEBER_ID_PRESENTEADO, RECEBER_MSG_PRESENTE, RECEBER_CONFIRMACAO_PRESENTE, CONFIRMAR_PRESENTE
from utils.antispam import ButtonHandler
from api.conta import Conta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

RECEBER = 1

async def atualizar_biografia(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user.id
        data = update.callback_query.data.split("_")
        query = update.callback_query
        await query.edit_message_text("Viva! Uma biografia. Agora, me envie o texto que deseja colocar, ele não pode ultrapassar 72 caracteres.")
        return RECEBER

async def receber_biografia(update: Update, context: CallbackContext):
        if len(update.message.text) > 72:
            await update.message.reply_text(reply_to_message_id=update.message.message_id, text="Perdão, sua bio ultrapassa 72 caracteres. Ação cancelada.")
            return ConversationHandler.END
        else:
            r = Conta.definir_bio(update.message.from_user.id, update.message.text)
            await update.message.reply_text(f"✅ Sua bio agora é: {update.message.text}")
            return ConversationHandler.END

if __name__ == '__main__':

    prefixos = ["!","/","."]
    #application = ApplicationBuilder().token('6975062896:AAHT_GqFRIWifT3JGFZ9_UCXCtmIacwvlzs').build()
    application = ApplicationBuilder().token("7051533328:AAEDAakd429GO9GtWU3MAVla7B0_lFV4b6Q").build()

    button_handler = ButtonHandler(application)

    # handlers básicos
    start_handler = CommandHandler('start', start_cmd.start)
    girar_handler = PrefixHandler(prefixos, 'pedido', giro.girar_handler)
    conta_handler = PrefixHandler(prefixos, 'conta', conta.conta_usuario)
    troca_handler = PrefixHandler(prefixos, 'troca', trocar_cmd.troca)
    colecao_handler = PrefixHandler(prefixos, 'ci', ci.colecao)
    set_fav_handler = PrefixHandler(prefixos, 'fav', set_fav.setar)
    help_handler = PrefixHandler(prefixos, 'help', ajuda.help)
    config_handler = PrefixHandler(prefixos, 'config', config.configuracoes)
    cadastrar_user_handler = PrefixHandler(prefixos, 'cadbeta', criar_user.cadastrar)
    set_gif_handler = PrefixHandler(prefixos, 'sgif', set_gif.setar)
    wl_user = PrefixHandler(prefixos, 'wls', wishlist.listar_wl)
    caixa_handler = PrefixHandler(prefixos, 'caixa', caixa.atendente)

    criar_wl_handler = ConversationHandler(
        entry_points=[CommandHandler("cwl", wishlist.criar_wl)],
        states={
            DAR_NOME_WL: [MessageHandler(filters.TEXT, wishlist.nomear_wl)],
            CARTAS_PARA_WL: [MessageHandler(filters.TEXT, wishlist.inserir_cartas_wl)]
        },
        fallbacks=[],
    )

    buscar_wl_handler = PrefixHandler(prefixos, 'wl', wishlist.buscar_wl)

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

    # nhe, aqui é só para cadastrar os handlers, eu deixo embaralhado pq é meio foda-se mesmo
    application.add_handler(config_handler)
    application.add_handler(wl_user)
    application.add_handler(cadastrar_user_handler)
    application.add_handler(set_gif_handler)
    application.add_handler(help_handler)
    application.add_handler(troca_handler)
    application.add_handler(obras_categoria_handler)
    application.add_handler(varias_carta)
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
    application.add_handler(criar_wl_handler)
    application.add_handler(buscar_wl_handler)
    application.add_handler(caixa_handler)

    application.add_handler(CallbackQueryHandler(button_handler.pagina_obras_proxima, pattern="^proxima_search_obras_"))
    application.add_handler(CallbackQueryHandler(button_handler.pagina_obras_anterior, pattern="^anterior_search_obras_"))

    application.add_handler(CallbackQueryHandler(button_handler.obs_categoria_anterior, pattern="^obs_categoria_anterior_"))
    application.add_handler(CallbackQueryHandler(button_handler.obs_categoria_proximo, pattern="^obs_categoria_proximo_"))

    application.add_handler(CallbackQueryHandler(button_handler.faltante_anterior, pattern="^faltantes_anterior_"))
    application.add_handler(CallbackQueryHandler(button_handler.faltante_proximo, pattern="^faltantes_proxima_"))

    application.add_handler(CallbackQueryHandler(button_handler.proxima_pagina, pattern="^colecao_proximo_"))
    application.add_handler(CallbackQueryHandler(button_handler.pagina_anterior, pattern="^colecao_anterior_"))

    application.add_handler(CallbackQueryHandler(button_handler.pagina_obra_proxima, pattern="^proxima_obras_"))
    application.add_handler(CallbackQueryHandler(button_handler.pagina_obra_anterior, pattern="^obras_anterior_"))

    application.add_handler(CallbackQueryHandler(button_handler.possuo_proximo, pattern="^possuo_proxima_"))
    application.add_handler(CallbackQueryHandler(button_handler.possuo_anterior, pattern="^possuo_anterior_"))

    application.add_handler(CallbackQueryHandler(button_handler.nao_trocar, pattern="^nao_trocar_"))
    application.add_handler(CallbackQueryHandler(button_handler.aceitar_troca, pattern="^trocar!_"))

    application.add_handler(CallbackQueryHandler(button_handler.sortear_carta_obra, pattern="^obra_"))
    application.add_handler(CallbackQueryHandler(button_handler.botao_de_sorteio, pattern="^Sortear_"))
    application.add_handler(CallbackQueryHandler(button_handler.aceitar_pedido_gif, pattern="^aceitar_pedido_"))
    application.add_handler(CallbackQueryHandler(button_handler.recusar_pedido_gif, pattern="^recusar_pedido_"))

    application.add_handler(CallbackQueryHandler(button_handler.anterior_imagem, pattern="^anterior_imagem_"))
    application.add_handler(CallbackQueryHandler(button_handler.proxima_imagem, pattern="^proxima_imagem_"))

    application.add_handler(CallbackQueryHandler(button_handler.s_proxima_imagem, pattern="^s_proxima_imagem"))
    application.add_handler(CallbackQueryHandler(button_handler.s_anterior_imagem, pattern="^s_anterior_imagem"))

    application.add_handler(CallbackQueryHandler(button_handler.perfil_privado, pattern="^privar_perfil_"))
    application.add_handler(CallbackQueryHandler(button_handler.notificar, pattern="^notificar_giros_"))
    application.add_handler(CallbackQueryHandler(button_handler.wl_p, pattern="^nwlp_"))
    application.add_handler(CallbackQueryHandler(button_handler.wl_a, pattern="^nwla_"))

    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(atualizar_biografia, pattern='^atualizar_bio')],
        states={
            RECEBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_biografia)]
        },
        fallbacks=[],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(wishlist.deletar_wl, pattern='^deletar_wl_')],
        states={
            QUAL_WL: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishlist.qual_wl)],
            CONFIRMAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishlist.confirmar_dl)]
        },
        fallbacks=[],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(wishlist.add_itens_wl, pattern='^add_wl')],
        states={
            QUAL_WL_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishlist.qual_wl_adicionar)],
            FINALIZAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishlist.finalizar_edicao)]
        },
        fallbacks=[],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(caixa.comprar_pedidos, pattern='^adquirir_pedidos')],
        states={
            CONFIRMAR_COMPRA_GIRO: [MessageHandler(filters.TEXT, caixa.finalizar_compra_giro)],
        },
        fallbacks=[],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(wishlist.qual_wl_dl, pattern='^rm_wl')],
        states={
            QUAL_WL_DL: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishlist.qual_wl_remover)],
            CONFIRMAR_DL: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishlist.finalizar_edicao_del)]
        },
        fallbacks=[],
    ))

########################################## handlers da loja (FINALMENTE. *sticker de fogos*)
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(caixa.iniciar_devolucao, pattern='^iniciar_devolucao')],
        states={
            VERIFICAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, caixa.confirmar_devolucao)],
            CONFIRMO: [MessageHandler(filters.TEXT, caixa.devolver)],
            DEVOLVER: [MessageHandler(filters.TEXT, caixa.devolver)]
        },
        fallbacks=[],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(caixa.iniciar_presente, pattern='^presentear')],
        states={
            RECEBER_ID_PRESENTEADO: [MessageHandler(filters.TEXT, caixa.receber_id_presenteado)],
            RECEBER_MSG_PRESENTE: [
                MessageHandler(filters.TEXT, caixa.receber_msg_presenteado),
                CommandHandler("skip", caixa.skip_mensagem),
            ],
            RECEBER_CONFIRMACAO_PRESENTE: [MessageHandler(filters.TEXT, caixa.confirmar_presente)],
            CONFIRMAR_PRESENTE: [MessageHandler(filters.TEXT, caixa.confirmar)],
        },
        fallbacks=[],
    ))

    application.add_handler(CallbackQueryHandler(button_handler.mostrar_vitrine, pattern="^vitrine"))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
