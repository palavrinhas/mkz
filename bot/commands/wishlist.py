from api.conta import Conta
from api.carta import Carta
from api.wishlist import *
from telegram.ext import (
    Updater,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # noqa: F811

INICIAR, DAR_NOME_WL, CARTAS_PARA_WL = range(3)
APAGAR_WL, QUAL_WL, CONFIRMAR = range(3)
QUAL_WL_ADD, FINALIZAR = range(2)

class Formatar:
    def formatar_lista(json):
        if len(json['wishlistItems']) < 1:
            return "Não há nada nessa lista ou ela sequer existe." 

        pagina_atual = json['page']
        total_paginas = json['totalPages']
        nome_wl = json['wishlistName']
        listagem = f"🔖 | <strong>{nome_wl}</strong>\n📒 | {pagina_atual}/{total_paginas}\n\n"
        for carta in json['wishlistItems']:
            listagem += f"{carta['emoji']} <code>{carta['carta_id']}</code>. <strong>{carta['nome']}</strong>\n"
        return listagem

    def formatar_wishlists(json):
        if len(json['wishlists']) < 1:
            return "<i>Você ainda não tem nenhuma lista. Que tal criar uma com <code>/cwl</code> ?</i>"
        usuario_id = json['wishlists'][0]['user_id']
        total_listas = len(json['wishlists'])
        listagem = f"👤 Usuário: [<code>{usuario_id}</code>]\n🔢 Total: <code>{total_listas}</code>\n\n"
        for lista in json['wishlists']:
            listagem += f"<code>{lista['WishlistID']}</code>. <strong>{lista['nome']}</strong>\n"
        return listagem

async def nomear_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    context.user_data['nome_wl_escolhido'] = update.message.text
    await update.message.reply_text("Nome bonito, nome formoso! Agora, me envie até 30 IDs que você esteja procurando, em formato de lista separado por espaço.\n⚠️ Mas atenção! Apenas 10 deles podem ser de pães que você já tem.")
    return CARTAS_PARA_WL

async def inserir_cartas_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    cartas = update.message.text.split()
    if len(cartas) > 30:
        await update.message.reply_text("Você pode inserir somente 30 ingredientes. Tente novamente!")
        return ConversationHandler.END
    for carta in cartas:
        c = Carta.buscar_carta(carta, user_id)
        if "Nenhuma carta" in c['message']:
            await update.message.reply_text("Tem algum ID aí que não existe. Verifique se está tudo certinho, ok? Você pode tentar novamente.")
            return ConversationHandler.END

    n_id = Wishlist.criar_wishlist(user_id, context.user_data['nome_wl_escolhido'])['retorno']['WishlistID']
    c_inseridas = Wishlist.inserir_item_wishlist(user_id, n_id, cartas)
    await update.message.reply_text(f"😻 Wishlist criada!\n\n🆔 Wishlist ID: <code>{n_id}</code>\n🥞 Ingredientes: <code>{len(cartas)}</code>\n\nVocê pode ver os itens da lista com <code>/wl {n_id}</code>.", parse_mode="HTML")
    return ConversationHandler.END

async def criar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name

    if update.message.chat.type != "private":
        await update.message.reply_text("Você não pode utilizar esse comando aqui. Somente no privado.")
        return

    premium = Conta.buscar_usuario(user_id)['premium']
    quantidade_wl = len(Wishlist.wishlists_usuario(user_id)['wishlists'])

    if premium != True and quantidade_wl >= 1:
        await update.message.reply_text("<i>Infelizmente, o limite de criação de wishlist é 1. Considere fazer uma pequena doação para obter até 5 wishlists!</i>", parse_mode="HTML")
        return
    elif premium and quantidade_wl == 5:
        await update.message.reply_text("<i>Você é doador, não o Papa. Seu limite de wishlist foi atingido.</i>", parse_mode="HTML")
        return

    elif premium and quantidade_wl < 5:
        await update.message.reply_text("😼 Eba, vamos criar uma lista de compras! 📝\nPrimeiro de tudo, preciso que você me envie o nome da wishlist.", parse_mode="HTML")
        return DAR_NOME_WL
    elif premium != True and quantidade_wl < 1:
        await update.message.reply_text("😼 Eba, vamos criar uma lista de compras! 📝\nPrimeiro de tudo, preciso que você me envie o nome da wishlist.", parse_mode="HTML")
        return DAR_NOME_WL

async def buscar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    if len(context.args) < 1:
        await update.message.reply_text("Você precisa me informar um ID de lista.\n\nExe.: <code>/wl 1</code>", parse_mode="HTML")
        return
    resposta = Wishlist.wishlist_completa(context.args[0])
    if resposta['code'] == 500:
        await update.message.reply_text("<strong>Erro</strong>: <i>Wishlist não encontrada.</i>", parse_mode="HTML")
        return
    r = Formatar.formatar_lista(resposta)

    if resposta['totalPages'] > 1:
        botao = [
    [
        InlineKeyboardButton("⬅️", callback_data=f"nwla_{resposta['wishlistItems'][0]['wishlist_id']}_{resposta['page'] - 1}"),
        InlineKeyboardButton("➡️", callback_data=f"nwlp_{resposta['wishlistItems'][0]['wishlist_id']}_{resposta['page'] + 1}")
    ],
    ]
        teclado = InlineKeyboardMarkup(botao)
        await update.message.reply_text(r, parse_mode="HTML", reply_markup=teclado)
    else:
        await update.message.reply_text(r, parse_mode="HTML")

async def listar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    # aqui não precisa paginar graças a Deus 🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏
    listado = Wishlist.wishlists_usuario(user_id)
    txt = Formatar.formatar_wishlists(listado)
    botao = [
    [
        InlineKeyboardButton("➕ Adicionar", callback_data="add_wl"),
        InlineKeyboardButton("➖ Excluir", callback_data="rm_wl")
    ],
    [
        InlineKeyboardButton("🗑 Deletar lista", callback_data="deletar_wl_"),
    ],
    ]
    teclado = InlineKeyboardMarkup(botao)

    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=teclado)

async def deletar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("<strong>🕊 Menos uma lista!</strong>\n\nAgora, me envie o ID da lista que deseja apagar completamente.", parse_mode="HTML")
    return QUAL_WL

async def qual_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    wl_id = update.message.text

    r = Wishlist.wishlist_completa(wl_id)
    if r['wishlistItems'][0]['user_id'] != user_id:
        await update.message.reply_text("<i>Essa lista não é sua. Tente novamente :)</i>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        context.user_data['wl_delete'] = wl_id
        await update.message.reply_text("<strong>⚠️ Você confirma essa ação? Ela <i>não</i> terá volta.</strong>\n\n<i>Sim</i> ou <i>Não</i>", parse_mode="HTML")
        return CONFIRMAR

async def confirmar_dl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    confirmacao = update.message.text

    if confirmacao.lower() == "sim":
        Wishlist.deletar_wishlist(context.user_data['wl_delete'])
        await update.message.reply_text("<strong>✅ Lista deletada com sucesso.</strong>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        await update.message.reply_text("<strong>❗️ Parei.</strong>\n<i>A wishlist está intacta. Ação cancelada.</i>", parse_mode="HTML")
        return ConversationHandler.END


async def add_itens_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("<strong>👨‍🍳 Novos ingredientes!</strong>\n\nAgora, me envie ID da lista que quer adicionar os itens.", parse_mode="HTML")
    return QUAL_WL_ADD

async def qual_wl_adicionar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    wl_id = update.message.text
    wl = Wishlist.wishlist_completa(wl_id)

    if wl['code'] == 500 or wl['wishlistItems'][0]['user_id'] != user_id:
        await update.message.reply_text("<i>Essa wishlist não é sua ou ela sequer existe. Tente novamente :)</i>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        context.user_data['qual_wl_add'] = wl_id
        await update.message.reply_text("Certo, envie os IDs que quer adicionar:", parse_mode="HTML")
    return FINALIZAR

async def finalizar_edicao(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.message.from_user.id
    ids = update.message.text

    resposta = Wishlist.inserir_item_wishlist(user_id, context.user_data['qual_wl_add'], ids.split())
    
    if resposta['code'] != 200:
        err = ""
        for erro in resposta['errors']:
            err += f"{erro}\n"
        await update.message.reply_text(f"⚠️ Operação terminada com erros:\n\n{err}\nFora esses erros, todas as outras operações foram concluídas com sucesso.")
        await update.message.reply_text("😸 Edição concluída! ✅")

    return ConversationHandler.END