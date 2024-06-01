package internal

import (
	"api/db"
	"api/models"

	"github.com/gofiber/fiber/v2"
)

func CriarCartaSubobra(c *fiber.Ctx) error {
	var carta models.CartaSub
	if err := c.BodyParser(&carta); err != nil {
		return err
	}

	if carta.Nome == "" || carta.SubObra == 0 || carta.Creditos == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"erro": "Campos 'nome', 'Subobra ID' e 'Creditos' são obrigatórios",
		})
	}

	if err := db.DB.Create(&carta).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"mensagem": "Carta criada com sucesso!",
		"cartaID":  carta.CartaSubID,
	})
}

func EditarCartaSubobra(c *fiber.Ctx) error {
	return c.JSON("so")
}
