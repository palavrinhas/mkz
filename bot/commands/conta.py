from telegram.ext import Updater, ContextTypes
from api.conta import Conta
from api.carta import Carta
from utils import categoria
from typing import Union

def info_conta(user_id: str, nome: str) -> (str, Union[str, None]):
    conta = Conta.buscar_usuario(user_id)
    membro = "Burguês" if conta['premium'] else "Freguês"
    moedas = conta['moedas']
    total_cartas = len(Conta.buscar_colecao_bruta(user_id))

    if conta['carta_fav'] == 0:
        ingrediente_fav = ""
        link = None
    elif Conta.nao_esta_colecao(user_id, conta['carta_fav']) == False:
        Conta.setar_carta_favorita(str(user_id), 0)
        ingrediente_fav = ""
        link = None
    else:
        ifs = Carta.buscar_carta(conta['carta_fav'], user_id)
        ingrediente_fav = f"\n⭐️ Ingrediente favorito:\n<code>{conta['carta_fav']}</code>. <strong>{ifs['carta']['nome']}</strong> {categoria.get_emoji(ifs['quantidade_acumulada'])}\n"
        link = ifs['carta']['imagem']
    bio = conta['bio'] if conta['bio'] != "" else "Bio não definida pelo usuário."
    privado = conta['privado']

    if privado == False:
        texto = f"""
<strong>🪪 Cartão Fidelidade</strong>
<strong>🔖 Nome</strong>: {nome}
<strong>🏷 Membro:</strong> {membro}
{ingrediente_fav}
🛒 <strong>Cardápio:</strong> {total_cartas} <strong>pães</strong>
🛎 <strong>Pedidos:</strong> {conta['giros']} <strong>(Máx)</strong>
💵 <strong>Dinheiro:</strong> {moedas}

🐱 <strong>Bio</strong>: <i>{bio}</i> 
    """
    else:
        texto = f"""
<strong>🪪 Cartão Fidelidade:</strong>

<i>😾 Perfil confidencial!</i>
<strong>🔖 Nome</strong>: {nome}

{ingrediente_fav}
    """
    return texto, link

async def conta_usuario(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    texto, link  = info_conta(user_id, n)
    if link is None:
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text=texto, parse_mode="HTML")
    elif link.endswith(".gif") or link.endswith(".mp4"):
        await update.message.reply_animation(link, reply_to_message_id=update.message.message_id, caption=texto, parse_mode="HTML")
    else:
        await update.message.reply_photo(photo=link, reply_to_message_id=update.message.message_id, caption=texto, parse_mode="HTML")

