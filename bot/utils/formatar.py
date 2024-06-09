from .categoria import emoji, emoji_categoria_obras
from . import f
import json

class FormatadorMensagem:
    def formatar_filtro_colecao(json_data: str) -> str:
        pagina_atual = json_data['pagina_atual']
        total_paginas = json_data['total_paginas']
        img = json_data['obra']['imagem']
        idee = json_data['content'][0]['obra']
        nome = json_data['obra']['nome']
        categoria = json_data['obra']['categoria']
        emj = emoji(categoria)

        terminado = f.formatar_obras_cartas(json_data["content"])
        
        fmt = f"""
{emj} — <strong>{nome}</strong> [<code>{idee}</code>]
🥘 — <strong>{pagina_atual}/{total_paginas}</strong>

<i><strong>{json_data['total_cartas']}</strong> ingredientes faltantes de <strong>{json_data['total_cartas_obra']}.</strong></i>

{terminado}
        """
        return fmt, img

    def formatar_filtro_possui(json_data: str) -> str:
        pagina_atual = json_data['pagina_atual']
        total_paginas = json_data['total_paginas']
        img = json_data['obra']['imagem']
        idee = json_data['content'][0]['obra']
        nome = json_data['obra']['nome']
        categoria = json_data['obra']['categoria']
        emj = emoji(categoria)

        terminado = f.formatar_obras_cartas(json_data["content"])
        fmt = f"""
{emj} — <strong>{nome}</strong> [<code>{idee}</code>]
🥘 — <strong>{pagina_atual}/{total_paginas}</strong>

<i><strong>{json_data['total_cartas']}</strong> ingredientes encontrados de <strong>{json_data['total_cartas_obra']}.</strong></i>

{terminado}
        """
        return fmt, img

    def formatar_obras_categoria(json_data: str, emoji) -> str:
        pagina_atual = json_data['currentPage']
        total_paginas = json_data['totalPages']
        emj = emoji_categoria_obras(emoji)
        cabecario = f"""{emj} — {pagina_atual}/{total_paginas}\n\n"""
        cabecario += f.formatar_obras_categoria(json_data['obras'])
        return cabecario
