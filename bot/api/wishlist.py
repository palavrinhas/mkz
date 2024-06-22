import httpx

class Wishlist:
    def criar_wishlist(user_id, nome="meu cativeiro!"):
        header = {"Content-type":"application/json"}
        js = {"nome":str(nome)}
        r = httpx.post(f"http://localhost:3000/cadastrar/wl/?user_id={user_id}", headers=header, json=js).json()
        return r

    def inserir_item_wishlist(user_id, wishlist_id, lista_cartas):
        items = []
        for carta in lista_cartas:
            items.append({"user_id":int(user_id), "wishlist_id":int(wishlist_id), "carta_id":int(carta)})
        header = {"Content-Type":"application/json"}
        js = {"items":items}
        r = httpx.post(f"http://localhost:3000/inserir/wl/", headers=header, json=js).json()
        return r

    def remover_item_wishlist(user_id, wishlist_id,carta_id):
        r = httpx.get(f"http://localhost:3000/remover/wl/{wishlist_id}/{user_id}/{carta_id}").json()
        return r

    def wishlist_completa(wishlist_id):
        r = httpx.get(f"http://localhost:3000/wishlist/{wishlist_id}").json()
        return r

    def wishlists_usuario(user_id):
        r = httpx.get(f"http://localhost:3000/wishlists/{user_id}").json()
        return r

    def deletar_wishlist(wishlist_id):
        r = httpx.get(f"http://localhost:3000/delete/wl/{wishlist_id}").json()
        return r
