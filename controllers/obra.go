package internal

import (
	"api/db"
	"api/models"
	"math"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

/*
 - Criar obra (nome, categoria, imagem);
 - Editar obra (nome, categoria, imagem);
 - Puxar obras
*/

func GetObras(c *fiber.Ctx) error {
	var obras []models.Obra
	categoria := c.Query("categoria")

	switch categoria {
	case "p":
		categoria = "Música"
	case "a":
		categoria = "Animação"
	case "mu":
		categoria = "Filme"
	case "s":
		categoria = "Série"
	case "b":
		categoria = "Jogo"
	case "mi":
		categoria = "Multi"
	default:
		return c.JSON(fiber.Map{
			"erro": "A categoria fornecida é inválida.",
		})
	}

	page, err := strconv.Atoi(c.Query("page", "1"))
	if err != nil || page < 1 {
		page = 1
	}
	pageSize := 15

	var totalObras int64
	db.DB.Model(&models.Obra{}).Where("categoria = ?", categoria).Count(&totalObras)

	totalPages := int(math.Ceil(float64(totalObras) / float64(pageSize)))

	offset := (page - 1) * pageSize
	if offset < 0 {
		offset = 0
	}

	db.DB.Model(&models.Obra{}).Where("categoria = ?", categoria).Order("nome ASC").Limit(pageSize).Offset(offset).Find(&obras)

	response := map[string]interface{}{
		"obras":       obras,
		"totalPages":  totalPages,
		"currentPage": page,
	}
	return c.JSON(response)
}

func BuscarObraPorID(c *fiber.Ctx) error {
	obraID := c.Params("obra_id")
	var obra models.Obra

	if err := db.DB.Find(&obra, obraID).Error; err != nil {
		return err
	}

	if obra.ObraID == 0 {
		return c.JSON(fiber.Map{"erro": "nenhuma obra foi encontrada com esse ID."})
	}

	return c.JSON(obra)
}

// func BuscarObraPorNome(c *fiber.Ctx) error {

// 	var req struct {
// 		Termos string `json:"termos"`
// 	}

// 	if err := c.BodyParser(&req); err != nil {
// 		return err
// 	}

// 	var obras []models.Obra

// 	if err := db.DB.Where("nome LIKE ?", "%"+req.Termos+"%").Find(&obras).Error; err != nil {
// 		return err
// 	}

// 	if len(obras) == 0 {
// 		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "nenhuma obra foi encontrada com esse nome."})
// 	}

// 	return c.JSON(obras)
// }

func BuscarObraPorNome(c *fiber.Ctx) error {
	page, err := strconv.Atoi(c.Query("page"))
	if err != nil || page <= 0 {
		page = 1
	}

	pageSize := 15

	offset := (page - 1) * pageSize

	var req struct {
		Termos string `json:"termos"`
	}

	if err := c.BodyParser(&req); err != nil {
		return err
	}

	var obras []models.Obra
	var count int64

	if err := db.DB.Where("nome ILIKE ?", "%"+req.Termos+"%").Order("nome ASC").Offset(offset).Limit(pageSize).Find(&obras).Error; err != nil {
		return err
	}

	if err := db.DB.Model(&models.Obra{}).Where("nome LIKE ?", "%"+req.Termos+"%").Count(&count).Error; err != nil {
		return err
	}

	totalPages := int(math.Ceil(float64(count) / float64(pageSize)))

	if len(obras) == 0 {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "nenhuma obra foi encontrada com esse nome."})
	}

	return c.JSON(fiber.Map{
		"obras":        obras,
		"total_pages":  totalPages,
		"current_page": page,
	})
}

func SortearObraPorCategoria(c *fiber.Ctx) error {
	var filmes []models.Obra
	var categoria string

	switch c.Params("categoria") {
	case "1":
		categoria = "Filme"
	case "2":
		categoria = "Série"
	case "3":
		categoria = "Animação"
	case "4":
		categoria = "Música"
	case "5":
		categoria = "Jogo"
	case "6":
		categoria = "Multi"
	}

	if err := db.DB.Where("categoria = ?", categoria).Order("RANDOM()").Limit(6).Find(&filmes).Error; err != nil {
		return err
	}

	if len(filmes) < 1 {
		return c.JSON(fiber.Map{
			"erro":     404,
			"mensagem": "Err... Não tenho nenhuma obra para essa categoria no momento :(",
		})
	}

	return c.JSON(filmes)
}

func CriarObra(c *fiber.Ctx) error {
	var novaObra models.Obra

	if err := c.BodyParser(&novaObra); err != nil {
		return err
	}

	if novaObra.Nome == "" || novaObra.Categoria == "" || novaObra.Imagem == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"message": false,
		})
	}

	if err := db.DB.Create(&novaObra).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"message": true,
		"ID":      novaObra.ObraID,
	})
}

func EditarObra(c *fiber.Ctx) error {
	ObraID := c.Params("obra_id")

	var novosDados struct {
		Tipo     string `json:"tipo"`
		Conteudo string `json:"conteudo"`
	}

	if err := c.BodyParser(&novosDados); err != nil {
		return err
	}

	var obra models.Obra
	if err := db.DB.First(&obra, ObraID).Error; err != nil {
		return err
	}

	switch novosDados.Tipo {
	case "nome":
		obra.Nome = novosDados.Conteudo
	case "categoria":
		obra.Categoria = novosDados.Conteudo
	case "imagem":
		obra.Imagem = novosDados.Conteudo
	default:
		return fiber.NewError(fiber.StatusBadRequest, "Tipo de campo inválido")
	}

	if err := db.DB.Save(&obra).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"message": "Obra editada com sucesso",
		"obra":    obra,
	})
}

// func CartasPorObra(c *fiber.Ctx) error {
// 	obraID := c.Params("obra_id")

// 	var obra models.Obra
// 	if err := db.DB.First(&obra, "obra_id = ?", obraID).Error; err != nil {
// 		if err == gorm.ErrRecordNotFound {
// 			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
// 				"erro": "Obra não encontrada",
// 			})
// 		}
// 		return err
// 	}

// 	var cartas []models.Carta
// 	if err := db.DB.Where("obra = ?", obraID).Find(&cartas).Error; err != nil {
// 		return err
// 	}

// 	return c.JSON(cartas)
// }

func CartasPorObra(c *fiber.Ctx) error {
	obraID := c.Params("obra_id")

	var obra models.Obra
	if err := db.DB.First(&obra, "obra_id = ?", obraID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"erro": "Obra não encontrada",
			})
		}
		return err
	}

	var totalCartas int64
	if err := db.DB.Model(&models.Carta{}).Where("obra = ?", obraID).Count(&totalCartas).Error; err != nil {
		return err
	}

	pageSize := 15
	page, err := strconv.Atoi(c.Query("page", "1"))
	if err != nil || page < 1 {
		page = 1
	}

	var cartas []models.CartaComAcumulado

	if page == 0 {
		if err := db.DB.
			Table("carta").
			Select("carta.*, COALESCE(colecao_items.acumulado, 0) AS acumulado").
			Joins("LEFT JOIN colecao_items ON carta.ID = colecao_items.item_id").
			Where("carta.obra = ?", obraID).
			Order("nome ASC").
			Find(&cartas).Error; err != nil {
			return err
		}
	} else {
		offset := (page - 1) * pageSize
		if err := db.DB.
			Table("carta").
			Select("carta.*, COALESCE(colecao_items.acumulado, 0) AS acumulado").
			Joins("LEFT JOIN colecao_items ON carta.ID = colecao_items.item_id").
			Where("carta.obra = ?", obraID).
			Order("nome ASC").
			Offset(offset).
			Limit(pageSize).
			Find(&cartas).Error; err != nil {
			return err
		}
	}

	totalPages := int(math.Ceil(float64(totalCartas) / float64(pageSize)))

	response := fiber.Map{
		"totalCartasObra": totalCartas,
		"totalPages":      totalPages,
		"page":            page,
		"cartas":          cartas,
	}

	return c.JSON(response)
}
