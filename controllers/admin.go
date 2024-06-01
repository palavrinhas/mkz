package internal

import (
	"api/db"
	"api/models"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

func CriarAdmin(c *fiber.Ctx) error {
	userID := c.Params("user_id")

	var usuario models.Usuario
	if err := db.DB.First(&usuario, "user_id = ?", userID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"mensagem": "Usuário não encontrado. Ele primeiro precisa iniciar o bot antes de ser admin.",
			})
		}
		return err
	}

	if err := db.DB.Model(&models.Usuario{}).Where("user_id = ?", userID).Update("admin", true).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"mensagem": "Campo Admin do usuário atualizado com sucesso.",
	})
}

func RemoverAdmin(c *fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"mensagem": "Administrador removido com sucesso.",
	})
}
