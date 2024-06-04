def emoji(categoria):
    match categoria:
        case "Filme":
            emoji = "🧁"
        case "Série":
            emoji = "🥣"
        case "Animação":
            emoji = "🥖"
        case "Música":
            emoji = "🍞"
        case "Jogo":
            emoji = "🍔"
        case "Multi":
            emoji = "🥪"
    return emoji

def emoji_categoria_obras(categoria):
    match categoria:
        case "mu":
            emoji = "🧁"
        case "s":
            emoji = "🥣"
        case "a":
            emoji = "🥖"
        case "p":
            emoji = "🍞"
        case "b":
            emoji = "🍔"
        case "mi":
            emoji = "🥪"
    return emoji

def get_emoji(acumulado):
    if int(acumulado) == 1 or 0:
        return ""
    elif 2 <= int(acumulado) < 10:
        return "😿"
    elif 10 <= int(acumulado) < 25:
        return "😾"
    elif 25 <= int(acumulado) < 50:
        return "😼"
    elif 50 <= int(acumulado) < 100:
        return "😸"
    elif int(acumulado) >= 100:
        return "😻"
    else:
        return ""