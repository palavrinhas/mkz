package internal

import (
	"api/db"
	"api/models"
	"errors"
	"math"
	"sort"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

func InserirCarta(c *fiber.Ctx) error {

	userID := c.Params("userID")

	var novaCarta models.ColecaoItem
	if err := c.BodyParser(&novaCarta); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Falha ao fazer parse do corpo da requisição"})
	}

	novaCarta.UserID = userID

	var existingItem models.ColecaoItem
	result := db.DB.Where("user_id = ? AND item_id = ?", novaCarta.UserID, novaCarta.ItemID).First(&existingItem)
	if result.Error != nil && result.Error != gorm.ErrRecordNotFound {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Erro ao consultar o banco de dados"})
	}

	if result.Error == gorm.ErrRecordNotFound {
		novaCarta.Acumulado = 1
		db.DB.Create(&novaCarta)
	} else {
		existingItem.Acumulado += 1
		db.DB.Where("user_id = ? AND item_id = ?", existingItem.UserID, existingItem.ItemID).Save(&existingItem)
	}

	return c.JSON(fiber.Map{"message": "Item adicionado à coleção com sucesso"})
}

func RemoverCarta(c *fiber.Ctx) error {
	userID := c.Params("userID")

	var itemToRemove models.ColecaoItem

	if err := c.BodyParser(&itemToRemove); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Falha ao fazer parse do corpo da requisição"})
	}
	itemToRemove.UserID = userID

	var existingItem models.ColecaoItem
	result := db.DB.Where("user_id = ? AND item_id = ?", itemToRemove.UserID, itemToRemove.ItemID).First(&existingItem)
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Item não encontrado na coleção do usuário"})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Erro ao consultar o banco de dados"})
	}

	if existingItem.Acumulado == 0 {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "O item já está ausente na coleção do usuário"})
	}

	// Remover uma unidade do item da coleção
	existingItem.Acumulado -= 1
	if existingItem.Acumulado == 0 {
		db.DB.Where("user_id = ? AND item_id = ?", existingItem.UserID, existingItem.ItemID).Delete(&existingItem)
	} else {
		db.DB.Where("user_id = ? AND item_id = ?", existingItem.UserID, existingItem.ItemID).Save(&existingItem)
	}

	return c.JSON(fiber.Map{"message": "Item removido da coleção com sucesso"})
}

// Função para verificar se a carta está na coleção do usuário
func cartaNaColecao(userID string, itemID uint) bool {
	var count int64
	db.DB.Model(&models.ColecaoItem{}).Where("user_id = ? AND item_id = ?", userID, itemID).Count(&count)
	return count > 0
}

func SetarCartaFavorita(c *fiber.Ctx) error {
	type request struct {
		UserID string `json:"user"`
		ItemID uint   `json:"carta_fav"`
	}

	var req request

	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"message": "Dados inválidos",
		})
	}

	if req.ItemID != 0 && !cartaNaColecao(req.UserID, req.ItemID) {
		return c.Status(fiber.StatusForbidden).JSON(fiber.Map{
			"message": "Carta não encontrada na coleção do usuário",
		})
	}

	if err := db.DB.Model(&models.Usuario{}).Where("user_id = ?", req.UserID).Update("carta_fav", req.ItemID).Error; err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Erro ao atualizar a carta favorita",
		})
	}

	return c.JSON(fiber.Map{
		"message": "Carta favorita atualizada com sucesso",
	})
}

func PegarColecaoBruta(c *fiber.Ctx) error {
	userID := c.Params("user_id")

	var items []models.ColecaoItem
	db.DB.Where("user_id = ?", userID).Find(&items)

	collectionJSON := make(map[uint]uint)
	for _, item := range items {
		collectionJSON[item.ItemID] = item.Acumulado
	}

	return c.JSON(collectionJSON)
}

func PegarColecao(c *fiber.Ctx) error {
	userID := c.Params("userID")

	page, _ := strconv.Atoi(c.Query("pagina", "1"))
	itemsPerPage := 15

	var totalItemsCount int64
	var cartas []struct {
		models.ColecaoItem
		CartaNome string
		Categoria string
		ObraNome  string
	}

	// Contar o total de itens na coleção do usuário
	db.DB.Model(&models.ColecaoItem{}).Where("user_id = ?", userID).Count(&totalItemsCount)

	// Buscar todos os itens da coleção do usuário com join nas tabelas necessárias
	db.DB.Table("colecao_items").
		Select("colecao_items.*, carta.nome as carta_nome, obras.categoria, obras.nome as obra_nome").
		Joins("JOIN carta ON carta.id = colecao_items.item_id").
		Joins("JOIN obras ON obras.obra_id = carta.obra").
		Where("colecao_items.user_id = ?", userID).
		Scan(&cartas)

	totalPages := int(math.Ceil(float64(totalItemsCount) / float64(itemsPerPage)))

	// Organizar as cartas por categoria
	categoriasMap := map[string][]struct {
		models.ColecaoItem
		CartaNome string
		Categoria string
		ObraNome  string
	}{}

	for _, carta := range cartas {
		categoriasMap[carta.Categoria] = append(categoriasMap[carta.Categoria], carta)
	}

	for _, cartasCategoria := range categoriasMap {
		// Ordenar as cartas dentro da categoria, primeiro por obra e depois por nome da carta
		sort.SliceStable(cartasCategoria, func(i, j int) bool {
			if cartasCategoria[i].ObraNome == cartasCategoria[j].ObraNome {
				return cartasCategoria[i].CartaNome < cartasCategoria[j].CartaNome
			}
			return cartasCategoria[i].ObraNome < cartasCategoria[j].ObraNome
		})
	}

	var cartasOrdenadas []struct {
		models.ColecaoItem
		CartaNome string
		Categoria string
		ObraNome  string
	}

	categorias := []string{"Música", "Série", "Animação", "Jogo", "Filme", "Multi"}
	for _, categoria := range categorias {
		cartasOrdenadas = append(cartasOrdenadas, categoriasMap[categoria]...)
	}

	offset := (page - 1) * itemsPerPage
	if offset > len(cartasOrdenadas) {
		offset = len(cartasOrdenadas)
	}

	limit := itemsPerPage
	if offset+limit > len(cartasOrdenadas) {
		limit = len(cartasOrdenadas) - offset
	}

	pagedItems := cartasOrdenadas[offset : offset+limit]

	collectionJSON := make(map[string]interface{})
	collectionJSON["total_paginas"] = totalPages
	collectionJSON["pagina_atual"] = page
	collectionJSON["colecao"] = make([]map[string]interface{}, 0)

	for _, item := range pagedItems {
		carta := map[string]interface{}{
			"id":        item.ItemID,
			"nome":      item.CartaNome,
			"acumulado": item.Acumulado,
			"categoria": item.Categoria,
			"obra_nome": item.ObraNome,
		}
		collectionJSON["colecao"] = append(collectionJSON["colecao"].([]map[string]interface{}), carta)
	}

	return c.JSON(collectionJSON)
}

func PegarColecaoFiltradaPorID(c *fiber.Ctx) error {
	userID := c.Params("userID")
	obraID := c.Params("obraID")

	pageSize := 15
	page := 1

	pageParam := c.Query("page")
	if pageParam != "" {
		page, _ = strconv.Atoi(pageParam)
	}

	var cartas []models.CartaComAcumulado
	var totalCartas int64
	var totalCartasDaObra int64
	var obra models.Obra

	db.DB.Table("carta").Where("obra = ?", obraID).Order("nome ASC").Count(&totalCartasDaObra)

	typeParam := c.Query("type")

	if err := db.DB.First(&obra, obraID).Error; err != nil {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Obra não encontrada"})
	}

	switch typeParam {
	case "f":
		db.DB.
			Table("carta").
			Select("carta.*, 0 AS acumulado").
			Joins("LEFT JOIN colecao_items ON carta.ID = colecao_items.item_id AND colecao_items.user_id = ?", userID).
			Where("carta.obra = ? AND colecao_items.item_id IS NULL", obraID).
			Order("nome ASC").
			Count(&totalCartas).
			Offset((page - 1) * pageSize).
			Limit(pageSize).
			Find(&cartas)
	case "s":
		db.DB.
			Table("carta").
			Select("carta.*, colecao_items.acumulado").
			Joins("JOIN colecao_items ON carta.ID = colecao_items.item_id").
			Where("colecao_items.user_id = ? AND carta.obra = ?", userID, obraID).
			Order("nome ASC").
			Count(&totalCartas).
			Offset((page - 1) * pageSize).
			Limit(pageSize).
			Find(&cartas)
	default:
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Parâmetro inválido."})
	}

	totalPages := int(math.Ceil(float64(totalCartas) / float64(pageSize)))

	response := map[string]interface{}{
		"total_paginas":     totalPages,
		"pagina_atual":      page,
		"total_cartas":      totalCartas,
		"total_cartas_obra": totalCartasDaObra,
		"content":           cartas,
		"obra": map[string]interface{}{
			"nome":      obra.Nome,
			"categoria": obra.Categoria,
			"imagem":    obra.Imagem,
		},
	}
	return c.JSON(response)
}
