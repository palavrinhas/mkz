package internal

import (
	"api/db"
	"api/models"

	"github.com/gofiber/fiber/v2"
)

func CriarSubobra(c *fiber.Ctx) error {
	var novaObra models.Subobra

	if err := c.BodyParser(&novaObra); err != nil {
		return err
	}

	if novaObra.Nome == "" || novaObra.Imagem == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"erro": "Campos 'nome' e 'imagem' são obrigatórios",
		})
	}

	if err := db.DB.Create(&novaObra).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"message": "Subobra cadastrada com sucesso",
		"ID":      novaObra.SubobraID,
	})
}

func BuscarSubobraPorID(c *fiber.Ctx) error {
	obraID := c.Params("subobra_id")
	var obra models.Subobra

	if err := db.DB.Find(&obra, obraID).Error; err != nil {
		return err
	}

	if obra.SubobraID == 0 {
		return c.JSON(fiber.Map{"erro": "nenhuma obra foi encontrada com esse ID."})
	}

	return c.JSON(obra)
}

func SortearSubobra(c *fiber.Ctx) error {
	var subobras []models.Subobra
	db.DB.Order("RANDOM()").Limit(3).Find(&subobras)
	return c.JSON(subobras)
}

func GetSubobras(c *fiber.Ctx) error {
	var subobras []models.Subobra
	db.DB.Find(&subobras)
	return c.JSON(subobras)
}
