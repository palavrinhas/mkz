package internal

import (
	"api/db"
	"api/models"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

const (
	BotToken = "7051533328:AAFiEX6Zc963hIKB768UEOkDZ5qmAzYReR8"
	ApiURL   = "https://api.telegram.org/bot" + BotToken + "/sendMessage"
)

type TelegramMessage struct {
	ChatID string `json:"chat_id"`
	Text   string `json:"text"`
}

func SendTelegramMessage(chatID string, message string) error {
	msg := TelegramMessage{
		ChatID: chatID,
		Text:   message,
	}

	body, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("error marshaling message: %v", err)
	}

	resp, err := http.Post(ApiURL, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("error sending message: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("non-OK HTTP status: %s", resp.Status)
	}

	return nil
}

func CriarPedido(c *fiber.Ctx) error {
	rand.Seed(time.Now().UnixNano())
	idPedido := rand.Intn(10000) + 1

	userID := c.Params("user_id")
	cartaID := c.Params("carta_id")
	carta_id, err := strconv.Atoi(cartaID)

	var dados struct {
		LinkGif string `json:"link"`
	}

	if err := c.BodyParser(&dados); err != nil {
		return err
	}

	if err != nil {
		fmt.Println(err)
		return c.JSON(fiber.Map{
			"erro": "não foi possivel converter a carta string em int.",
		})
	}

	msgID := c.Params("msgid")

	pedido := models.Pedidos{
		UserID:     userID,
		CartaID:    carta_id,
		GifLink:    dados.LinkGif,
		MensagemID: msgID,
		PedidoID:   idPedido,
	}

	if err := db.DB.Create(&pedido).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"mensagem": pedido,
	})
}

func RecusarPedido(c *fiber.Ctx) error {
	pedidoID := c.Params("pedido_id")

	var pedido models.Pedidos
	if err := db.DB.Where("pedido_id = ?", pedidoID).Find(&pedido).Error; err != nil {
		return err
	}

	SendTelegramMessage(pedido.UserID, "Infelizmente, o pedido do seu gif foi recusado... Você quebrou alguma regra.")

	if err := db.DB.Where("pedido_id = ?", pedidoID).Delete(&pedido).Error; err != nil {
		return err
	}

	return c.JSON(fiber.Map{
		"mensagem": "Pedido recusado com sucesso.",
	})
}

func AceitarPedido(c *fiber.Ctx) error {
	pedidoID := c.Params("pedido_id")

	var pedido models.Pedidos
	if err := db.DB.Where("pedido_id = ?", pedidoID).First(&pedido).Error; err != nil {
		return err
	}

	var gif models.Gifs
	if err := db.DB.Where("user_id = ? AND carta_id = ?", pedido.UserID, pedido.CartaID).First(&gif).Error; err != nil {
		if !errors.Is(err, gorm.ErrRecordNotFound) {
			return err
		}

		novoGif := models.Gifs{
			UserID:  pedido.UserID,
			CartaID: pedido.CartaID,
			GifLink: pedido.GifLink,
		}

		if err := db.DB.Create(&novoGif).Error; err != nil {
			return err
		}
	} else {
		if err := db.DB.Model(&gif).Where("user_id = ?", pedido.UserID).Update("gif_link", pedido.GifLink).Error; err != nil {
			return err
		}
	}

	if err := db.DB.Where("pedido_id = ?", pedidoID).Delete(&pedido).Error; err != nil {
		return err
	}

	if err := db.DB.Model(&models.ColecaoItem{}).Where("user_id = ? AND item_id = ?", pedido.UserID, pedido.CartaID).Update("personal_gif", true).Error; err != nil {
		return err
	}

	SendTelegramMessage(pedido.UserID, "Obaa! Seu último pedido de gif foi aceito. Verifique como está bonito agora!")

	return c.JSON(fiber.Map{
		"mensagem": "Pedido aceito com sucesso.",
	})
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

// func BuscarUsuario(c *fiber.Ctx) error {
// 	userID := c.Params("user_id")
// 	var user models.Usuario

// 	if err := db.DB.Find(&user, userID).Error; err != nil {
// 		return err
// 	}

// 	if user.UserID == "" {
// 		return c.JSON(fiber.Map{"erro": "não foi encontrado nenhum usuário."})
// 	}

// 	return c.JSON(user)
// }

func BuscarUsuario(c *fiber.Ctx) error {
	userID := c.Params("user_id")
	var user models.Usuario

	if err := db.DB.First(&user, "user_id = ?", userID).Error; err != nil {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"erro": "não foi encontrado nenhum usuário."})
	}

	var colecaoItem models.ColecaoItem
	specificItemID := user.CartaFav // Usar o valor de CartaFav como o ID do item específico

	if err := db.DB.Where("user_id = ? AND item_id = ?", userID, specificItemID).First(&colecaoItem).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			// Se o item específico não for encontrado na coleção, atualize o campo CartaFav para 0
			user.CartaFav = 0
			if err := db.DB.Where("user_id = ?", userID).Save(&user).Error; err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"erro": "não foi possível atualizar o usuário."})
			}
		} else {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"erro": "erro ao verificar a coleção do usuário."})
		}
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
