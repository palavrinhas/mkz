import httpx
from typing import Union

class ColecaoFiltros:
    def faltantes(user_id: str, obra_id: str, pagina=1) -> (bool, Union[str, str]):
        retorno = httpx.get(f"http://localhost:3000/colecao/filtrada/{user_id}/{obra_id}?type=f&page={pagina}").json()
        if retorno['total_paginas'] == 0:
            return False, "<i>Parabéns! Você juntou todos os ingredientes e conseguiu terminar sua receita! Humm, que delícia! 🎂</i>", retorno['obra']['imagem']
        else:
            return True, retorno, "Ainda tem kkk"

    def possuo(user_id: str, obra_id: str, pagina=1) -> (bool, Union[str, str]):
        retorno = httpx.get(f"http://localhost:3000/colecao/filtrada/{user_id}/{obra_id}?type=s&page={pagina}").json()
        return True, retorno, retorno['obra']['imagem']
