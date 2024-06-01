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

// 	if err := db.DB.Find(&carta, cartaID).Error; err != nil {
// 		if err == gorm.ErrRecordNotFound {
// 			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "Nenhuma carta foi encontrada com esse ID."})
// 		}
// 		return err
// 	}

// 	err := db.DB.Where("user_id = ? AND item_id = ?", userID, cartaID).First(&colecaoItem).Error
// 	if err != nil {
// 		if err == gorm.ErrRecordNotFound {
// 			// Se o usuário não tiver essa carta na coleção, retorna a carta com quantidade acumulada zero
// 			return c.JSON(fiber.Map{"carta": carta, "quantidade_acumulada": 0})
// 		}
// 		return err
// 	}

// 	return c.JSON(fiber.Map{"carta": carta, "quantidade_acumulada": colecaoItem.Acumulado})
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
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "Nenhuma carta foi encontrada com esse ID."})
		}
		return err
	}

	// Busca a obra associada à carta
	if err := db.DB.First(&obra, carta.Obra).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "Nenhuma obra foi encontrada com esse ID."})
		}
		return err
	}

	// Verifica se o usuário possui essa carta na coleção
	err := db.DB.Where("user_id = ? AND item_id = ?", userID, cartaID).First(&colecaoItem).Error
	if err != nil {
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
			})
		}
		return err
	}

	// Retorna a carta e a quantidade acumulada na coleção do usuário
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
		"quantidade_acumulada": colecaoItem.Acumulado,
	})
}

// func BuscarCartaPorID(c *fiber.Ctx) error {
// 	cartaID := c.Params("carta_id")
// 	var carta models.Carta

// 	if err := db.DB.Find(&carta, cartaID).Error; err != nil {
// 		return err
// 	}

// 	if carta.ID == 0 {
// 		return c.JSON(fiber.Map{"erro": "nenhuma carta foi encontrada com esse ID."})
// 	}

// 	return c.JSON(carta)
// }

// func BuscarCartaPorNome(c *fiber.Ctx) error {
// 	var req struct {
// 		Termos string `json:"termos"`
// 	}

// 	if err := c.BodyParser(&req); err != nil {
// 		return err
// 	}

// 	var cartas []models.Carta

// 	if err := db.DB.Where("nome LIKE ?", "%"+req.Termos+"%").Find(&cartas).Error; err != nil {
// 		return err
// 	}

// 	if len(cartas) == 0 {
// 		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "nenhuma obra foi encontrada com esse nome."})
// 	}

// 	return c.JSON(cartas)
// }

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
	if err := db.DB.Model(&models.Carta{}).Where("nome LIKE ?", "%"+req.Termos+"%").Count(&totalCartas).Error; err != nil {
		return err
	}

	// Calcula o deslocamento (offset) com base na página atual
	offset := (pagina - 1) * resultadosPorPagina

	// Consulta para recuperar as cartas da página atual
	if err := db.DB.Where("nome LIKE ?", "%"+req.Termos+"%").Order("nome ASC").Offset(offset).Limit(resultadosPorPagina).Find(&cartas).Error; err != nil {
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
