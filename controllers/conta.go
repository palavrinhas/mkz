package internal

import (
	"api/db"
	"api/models"
	"strconv"

	"github.com/gofiber/fiber/v2"
)

func Pedido(c *fiber.Ctx) error {
	return c.JSON("ok")
}

func Banir(c *fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"mensagem": "usuário banido com sucesso. Ele não tem mais acesso ao bot.",
	})
}

func GetWishlist(c *fiber.Ctx) error {
	userID := c.Params("userID")
	var items []models.Wishlist

	db.DB.Where("user_id = ?", userID).Find(&items)

	var collectionJSON []string

	for _, item := range items {
		collectionJSON = append(collectionJSON, strconv.Itoa(item.CartaID))
	}

	return c.JSON(collectionJSON)
}

func AdicionarItemWishlist(c *fiber.Ctx) error {
	var item models.Wishlist

	if err := c.BodyParser(&item); err != nil {
		return err
	}

	if err := db.DB.Create(&item).Error; err != nil {
		return err
	}

	return c.JSON(item)
}

func RemoverItemWishlist(c *fiber.Ctx) error {
	userID := c.Params("userID")
	cartaID := c.Params("cartaID")

	if err := db.DB.Where("user_id = ? AND carta_id = ?", userID, cartaID).Delete(&models.Wishlist{}).Error; err != nil {
		return err
	}

	return c.SendStatus(fiber.StatusNoContent)
}

func ContaNova(c *fiber.Ctx) error {
	userID := c.Params("user_id")

	usuario := models.Usuario{
		UserID:       userID,
		Giros:        8,
		Banido:       false,
		DesejaTrocar: false,
		Privado:      false,
		Premium:      false,
		Admin:        false,
		CartaFav:     0,
		Moedas:       0,
		Notificar:    true,
	}

	if err := db.DB.Create(&usuario).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"mensagem": usuario,
	})
}

func BuscarUsuario(c *fiber.Ctx) error {
	userID := c.Params("user_id")
	var user models.Usuario

	if err := db.DB.Find(&user, userID).Error; err != nil {
		return err
	}

	if user.UserID == "" {
		return c.JSON(fiber.Map{"erro": "não foi encontrado nenhum usuário."})
	}

	return c.JSON(user)
}

func InserirGiros(c *fiber.Ctx) error {
	id := c.Params("user")

	var novosDados struct {
		Giros int `json:"giros"`
	}

	if err := c.BodyParser(&novosDados); err != nil {
		return err
	}

	var usuario models.Usuario
	if err := db.DB.Where("user_id = ?", id).First(&usuario).Error; err != nil {
		return err
	}

	usuario.Giros = novosDados.Giros

	if err := db.DB.Model(&models.Usuario{}).Where("user_id = ?", id).Update("giros", novosDados.Giros).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"message":    "Giros atualizados com sucesso!",
		"atualizado": usuario.Giros,
	})
}

func RemoverGiro(c *fiber.Ctx) error {
	id := c.Params("userID")

	var usuario models.Usuario
	if err := db.DB.Where("user_id = ?", id).First(&usuario).Error; err != nil {
		return err
	}

	usuario.Giros = usuario.Giros - 1

	if err := db.DB.Model(&models.Usuario{}).Where("user_id = ?", id).Update("giros", usuario.Giros).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"message":    "Giros atualizados com sucesso!",
		"atualizado": usuario.Giros,
	})
}

// método não utilizado diretamente na API.
func TrocarCartas(userID string, cartaID int, trocadorID string) {
}

// método para ser concluido
func NomearColecao(userID string, nomeNovo string) {
}
