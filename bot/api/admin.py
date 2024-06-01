import httpx

class Admin:
    def criar_admin(user_id: str) -> str:
        r = httpx.get(f"http://localhost:3000/cadastrar/admin/{user_id}").json()
        return r['mensagem']

    def remover_admin(user_id: str) -> str:
        # TODO remover admin quando ele fizer coisas feias!!
        return True
