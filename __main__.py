import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PrefixHandler
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackContext
from commands import trocar_cmd, conta, start_cmd, giro, ci, buscar_c, buscar_ob, adicionar_carta, adicionar_obra, varias_c, bkp, set_adm, editar_c, editar_ob, set_fav, obras_categoria, set_gif
from utils.antispam import ButtonHandler
from api.conta import Conta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    prefixos = ["!","/","."]
    #application = ApplicationBuilder().token('6975062896:AAHT_GqFRIWifT3JGFZ9_UCXCtmIacwvlzs').build()
    application = ApplicationBuilder().token("7051533328:AAFiEX6Zc963hIKB768UEOkDZ5qmAzYReR8").build()

    button_handler = ButtonHandler(application)

    start_handler = CommandHandler('start', start_cmd.start)
    girar_handler = PrefixHandler(prefixos, 'pedido', giro.girar_handler)
    conta_handler = PrefixHandler(prefixos, 'conta', conta.conta_usuario)
    troca_handler = PrefixHandler(prefixos, 'troca', trocar_cmd.troca)
    colecao_handler = PrefixHandler(prefixos, 'ci', ci.colecao)
    set_fav_handler = PrefixHandler(prefixos, 'fav', set_fav.setar)


    STATE_WAITING = 1
    set_gif_handler = ConversationHandler(
        entry_points=[PrefixHandler(prefixos, 'sgif', set_gif.setar)],
        states={
            STATE_WAITING: [MessageHandler(filters.Entity("url"), set_gif.processar_gif)]
        },
        fallbacks=[]
    )

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
    application.add_handler(set_gif_handler)
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

    application.run_polling(allowed_updates=Update.ALL_TYPES)
