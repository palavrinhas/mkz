from telegram.ext import Updater, ContextTypes
from api.conta import Conta
from api.carta import Carta
from api.wishlist import *

async def criar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    if update.message.chat.type != "private":
        await update.message.reply_text("Você não pode utilizar esse comando aqui. Somente no privado.")
        return
    # é mais viável consultar e setar todas as infos antes porque evita de fazer múltiplas requisições desnecessárias para a API, economizando recursos.
    premium = Conta.buscar_usuario(user_id)['premium']
    quantidade_wl = len(Wishlist.wishlists_usuario(user_id)['wishlists'])

    if premium != True and quantidade_wl >= 1:
        print(1) # TODO: impedir de criar mais de uma lista, pois, o usuário não é premium.
        await update.message.reply_text("<i>Infelizmente, o limite de criação de wishlist foi atingido. Considere fazer uma pequena doação para obter até 5 wishlists!</i>", parse_mode="HTML")
    if premium and quantidade_wl < 5:
        print(1) # TODO: implementar criar lista para premium com >5 listas
    if premium and quantidade_wl == 5:
        await update.message.reply_text("<i>Você é doador, não o Papa. Seu limite de wishlist foi atingido.</i>", parse_mode="HTML")
        return

async def buscar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name

async def listar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    listado = Wishlist.wishlists_usuario(user_id)
