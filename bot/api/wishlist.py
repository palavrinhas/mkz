import httpx

class Wishlist:
    def criar_wishlist(user_id, nome):
        header = {"Content-type":"application/json"}
        js = {"nome":str(nome), "user_id":int(user_id)}
        r = httpx.post("http://localhost:3000/cadastrar/wl/", headers=header, json=js).json()
        return r['retorno']

    def inserir_item_wishlist(user_id, wishlist_id, carta_id=1):
        r = httpx.get(f"http://localhost:3000/inserir/wl/{wishlist_id}/{user_id}/{carta_id}").json()
        print(r)

    def remover_item_wishlist(user_id, carta_id):
        return True

    def wishlist_completa(user_id, lista_id):
        return True

    def wishlists_usuario(user_id):
        return True
