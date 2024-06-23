import httpx
from telegram import InlineKeyboardButton

class Obra:
    def obras_da_categoria(categoria: str, pagina=1) -> str:
        r = httpx.get(f"http://localhost:3000/obras?categoria={categoria}&page={pagina}").json()
        return r

    def criar_obra(nome, categoria, creditos):
        h = {"Content-type":"application/json"}
        match categoria:
            case 1:
                c = "Filme"
            case 2:
                c = "Série"
            case 3:
                c = "Animação"
            case 4:
                c = "Jogo"
            case 5:
                c = "Música"
            case 6:
                c = "Multi"
            case _:
                c = "Multi"
        js = {"nome":nome, "categoria":c, "imagem":creditos}
        r = httpx.post("http://localhost:3000/cadastrar/obra", headers=h, json=js).json()
        if r["message"]:
            ide = r["ID"]
        return ide

    def editar_obra(obra_id, tipo_dado, dado):
        h = {"Content-type":"application/json"}
        match tipo_dado:
            case 1:
                c = "nome"
            case 2:
                c = "categoria"
            case 3:
                c = "imagem"
        if c == "categoria":
            match dado:
                case "1":
                    cfinal = "Filme"
                case "2":
                    cfinal = "Série"
                case "3":
                    cfinal = "Animação"
                case "4":
                    cfinal = "Jogo"
                case "5":
                    cfinal = "Música"
                case "6":
                    cfinal = "Multi"
        else:
            cfinal = dado

        js = {"tipo":c, "conteudo":cfinal}
        r = httpx.post(f"http://localhost:3000/editar/obra/{obra_id}", headers=h, json=js).json()
        return r

    def buscar_obra(obra_id):
        r = httpx.get(f"http://localhost:3000/obra/{int(obra_id)}").json()
        return r

    def buscar_obra_nome(obra_nome, pagina=1):
        h = {"Content-type":"application/json"}
        js = {"termos":obra_nome}
        r = httpx.post(f"http://localhost:3000/obra-nome?page={pagina}", headers=h, json=js).json()
        return r

    def sortear_obras(categoria):
        r = httpx.get(f"http://localhost:3000/sortear/obras/{categoria}").json()
        print(r)
        if "erro" in r:
            retorno = r["mensagem"]
            print(retorno)
        else:
            formatted_text = ""
            obra_callbacks = []
            emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
            for index, item in enumerate(r, start=1):
                emoji_number = emojis[index - 1]
                formatted_text += f"{emoji_number} — {item['nome']}\n"
                obra_callbacks.append(InlineKeyboardButton(f"{emoji_number}", callback_data=f"obra_{item['ObraID']}"))
            obra_callbacks_divided = [obra_callbacks[i:i+3] for i in range(0, len(obra_callbacks), 3)]

        return formatted_text, obra_callbacks_divided

    def sortear_carta_obra(obra_id):
        r = httpx.get(f"http://localhost:3000/sortear/carta/{obra_id}").json()
        if "erro" in r:
            retorno = r["mensagem"]
        else:
            retorno = r
        return retorno
