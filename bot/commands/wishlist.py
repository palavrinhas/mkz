from telegram.ext import Updater, ContextTypes
from api.conta import Conta
from api.carta import Carta
from api.wishlist import *

async def criar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name

async def buscar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name

async def listar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
