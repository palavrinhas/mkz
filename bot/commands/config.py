from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from api.conta import Conta

async def configuracoes(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    mensagem = """Opa! Aqui temos as suas configurações do perfil."""
    conta = Conta.buscar_usuario(update.message.from_user.id)

    perfil_privado = "✅" if conta['privado'] else "❌"
    notificar_giro = "✅" if conta['notificar'] else "❌"

    botao = [
    [
        InlineKeyboardButton(f"🔒 Privar Perfil | {perfil_privado}", callback_data=f"privar_perfil_{conta['privado']}")
    ],
    [
        InlineKeyboardButton("💬 Atualizar Bio", callback_data="atualizar_bio")
    ],
    [
        InlineKeyboardButton(f"🔊 Notificação de giro | {notificar_giro}", callback_data=f"notificar_giros_{conta['notificar']}")
    ],
    ]

    teclado = InlineKeyboardMarkup(botao)
    await update.message.reply_text(
        text=mensagem,
        parse_mode="HTML",
        reply_markup=teclado
    )