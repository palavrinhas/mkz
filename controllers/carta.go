package internal

import (
	"api/db"
	"api/models"
	"fmt"
	"math"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

/*
 === "Créditos" da arte da carta, porque pode não ser uma arte oficial.

 - Cria uma carta (nome, obra, creditos);
 - Editar a carta (nome, obra, creditos);
*/

// func BuscarCartaPorID(c *fiber.Ctx) error {
// 	cartaID := c.Params("carta_id")
// 	userID := c.Query("user_id")
// 	var carta models.Carta
// 	var colecaoItem models.ColecaoItem
// 	var obra models.Obra

// 	// Busca a carta pelo ID
// 	if err := db.DB.First(&carta, cartaID).Error; err != nil {
// 		if err == gorm.ErrRecordNotFound {
// 			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"message": "Nenhuma carta foi encontrada com esse ID."})
// 		}
// 		return err
// 	}

// 	// Busca a obra associada à carta
// 	if err := db.DB.First(&obra, carta.Obra).Error; err != nil {
// 		if err == gorm.ErrRecordNotFound {
// 			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"message": "Nenhuma obra foi encontrada com esse ID."})
// 		}
// 		return err
// 	}

// 	// Verifica se o usuário possui essa carta na coleção
// 	err := db.DB.Where("user_id = ? AND item_id = ?", userID, cartaID).First(&colecaoItem).Error
// 	if err != nil {
// 		if err == gorm.ErrRecordNotFound {
// 			// Se o usuário não tiver essa carta na coleção, retorna a carta com quantidade acumulada zero
// 			return c.JSON(fiber.Map{
// 				"carta": map[string]interface{}{
// 					"ID":        carta.ID,
// 					"nome":      carta.Nome,
// 					"imagem":    carta.Imagem,
// 					"credito":   carta.Credito,
// 					"obra_id":   carta.Obra,
// 					"obra_nome": obra.Nome,
// 					"categoria": obra.Categoria,
// 				},
// 				"quantidade_acumulada": 0,
// 				"message":              "OK",
// 			})
// 		}
// 		return err
// 	}

// 	// Retorna a carta e a quantidade acumulada na coleção do usuário
// 	return c.JSON(fiber.Map{
// 		"carta": map[string]interface{}{
// 			"ID":        carta.ID,
// 			"nome":      carta.Nome,
// 			"imagem":    carta.Imagem,
// 			"credito":   carta.Credito,
// 			"obra_id":   carta.Obra,
// 			"obra_nome": obra.Nome,
// 			"categoria": obra.Categoria,
// 		},
// 		"quantidade_acumulada": colecaoItem.Acumulado,
// 		"message":              "OK",
// 	})
// }

func BuscarCartaPorID(c *fiber.Ctx) error {
	cartaID := c.Params("carta_id")
	userID := c.Query("user_id")
	var carta models.Carta
	var colecaoItem models.ColecaoItem
	var obra models.Obra

	// Busca a carta pelo ID
	if err := db.DB.First(&carta, cartaID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"message": "Nenhuma carta foi encontrada com esse ID."})
		}
		return err
	}

	// Busca a obra associada à carta
	if err := db.DB.First(&obra, carta.Obra).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"message": "Nenhuma obra foi encontrada com esse ID."})
		}
		return err
	}

	// Verifica se o usuário possui essa carta na coleção
	if err := db.DB.Where("user_id = ? AND item_id = ?", userID, cartaID).First(&colecaoItem).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			// Se o usuário não tiver essa carta na coleção, retorna a carta com quantidade acumulada zero
			return c.JSON(fiber.Map{
				"carta": map[string]interface{}{
					"ID":        carta.ID,
					"nome":      carta.Nome,
					"imagem":    carta.Imagem,
					"credito":   carta.Credito,
					"obra_id":   carta.Obra,
					"obra_nome": obra.Nome,
					"categoria": obra.Categoria,
				},
				"quantidade_acumulada": 0,
				"message":              "OK",
			})
		}
		return err
	}

	// Define a imagem ou o gif baseado no campo PersonalGif na tabela ColecaoItem
	var imagemOuGif string
	if colecaoItem.PersonalGif {
		// Se PersonalGif for verdadeiro, busca o GIF da tabela Gifs
		var gif models.Gifs
		if err := db.DB.Where("user_id = ? AND carta_id = ?", userID, cartaID).First(&gif).Error; err != nil {
			if err != gorm.ErrRecordNotFound {
				return err
			}
		}
		imagemOuGif = gif.GifLink
	} else {
		// Se PersonalGif for falso, usa a imagem da tabela Carta
		imagemOuGif = carta.Imagem
	}

	// Retorna a carta ou o gif e a quantidade acumulada na coleção do usuário
	return c.JSON(fiber.Map{
		"carta": map[string]interface{}{
			"ID":        carta.ID,
			"nome":      carta.Nome,
			"imagem":    imagemOuGif,
			"credito":   carta.Credito,
			"obra_id":   carta.Obra,
			"obra_nome": obra.Nome,
			"categoria": obra.Categoria,
		},
		"quantidade_acumulada": colecaoItem.Acumulado,
		"message":              "OK",
	})
}

func BuscarCartaPorNome(c *fiber.Ctx) error {
	var req struct {
		Termos string `json:"termos"`
	}

	if err := c.BodyParser(&req); err != nil {
		return err
	}

	// Obtenha o número da página da query (?pagina=x)
	pagina, err := strconv.Atoi(c.Query("pagina"))
	if err != nil || pagina < 1 {
		pagina = 1
	}

	// Defina a quantidade de resultados por página
	resultadosPorPagina := 10 // Altere conforme necessário

	var cartas []models.Carta
	var totalCartas int64

	// Consulta para contar o total de cartas que correspondem aos termos de busca
	if err := db.DB.Model(&models.Carta{}).Where("nome ILIKE ?", "%"+req.Termos+"%").Count(&totalCartas).Error; err != nil {
		return err
	}

	// Calcula o deslocamento (offset) com base na página atual
	offset := (pagina - 1) * resultadosPorPagina

	// Consulta para recuperar as cartas da página atual
	if err := db.DB.Where("nome ILIKE ?", "%"+req.Termos+"%").Order("nome ASC").Offset(offset).Limit(resultadosPorPagina).Find(&cartas).Error; err != nil {
		return err
	}

	// Calcula o total de páginas
	totalPaginas := int(math.Ceil(float64(totalCartas) / float64(resultadosPorPagina)))

	// Retorna os resultados paginados junto com o total de páginas e a página atual
	return c.JSON(fiber.Map{
		"cartas":       cartas,
		"totalPaginas": totalPaginas,
		"paginaAtual":  pagina,
	})
}

func CriarCarta(c *fiber.Ctx) error {
	var carta models.Carta

	if err := c.BodyParser(&carta); err != nil {
		return err
	}

	if carta.Nome == "" || carta.Obra == 0 || carta.Imagem == "" || carta.Credito == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"erro": "Campos 'nome', 'Obra', 'Imagem' e 'Credito' são obrigatórios",
		})
	}

	if err := db.DB.Create(&carta).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"mensagem": "Carta criada com sucesso!",
		"cartaID":  carta.ID,
	})
}

func EditarCarta(c *fiber.Ctx) error {
	cartaID := c.Params("carta_id")

	var novosDados struct {
		Tipo     string `json:"tipo"`
		Conteudo string `json:"conteudo"`
	}

	if err := c.BodyParser(&novosDados); err != nil {
		return err
	}

	var carta models.Carta
	if err := db.DB.First(&carta, cartaID).Error; err != nil {
		return err
	}

	switch novosDados.Tipo {
	case "nome":
		carta.Nome = novosDados.Conteudo
	case "obra":
		novoConteudo, err := strconv.Atoi(novosDados.Conteudo)
		if err != nil {
			fmt.Println(err)
		}
		carta.Obra = novoConteudo
	case "imagem":
		carta.Imagem = novosDados.Conteudo
	case "creditos":
		carta.Credito = novosDados.Conteudo
	default:
		return fiber.NewError(fiber.StatusBadRequest, "Tipo de campo inválido")
	}

	if err := db.DB.Save(&carta).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"message": "Carta editada com sucesso",
		"obra":    carta,
	})
}

func SortearCartaPorObraID(c *fiber.Ctx) error {
	var cartas []models.Carta
	obra := c.Params("obra_id")

	if err := db.DB.Where("obra = ?", obra).Order("RANDOM()").Limit(1).Find(&cartas).Error; err != nil {
		return err
	}

	if len(cartas) < 1 {
		return c.JSON(fiber.Map{
			"erro":     404,
			"mensagem": "Opa... Perdão. Não existe nenhuma carta cadastrada (ainda) para a obra selecionada. Você não perdeu giros.",
		})
	}

	return c.JSON(cartas)
}
