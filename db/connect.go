package db

import (
	"api/models"
	"fmt"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var DB *gorm.DB

func Connect() {
	database, err := gorm.Open(sqlite.Open("padocard.db"), &gorm.Config{})
	if err != nil {
		fmt.Printf("Não foi possível conectar ao banco de dados. Motivo: %s", err)
	}
	DB = database
	DB.AutoMigrate(&models.Wishlist{}, &models.ColecaoItem{}, &models.Usuario{}, &models.Obra{}, &models.Carta{}, &models.Subobra{}, &models.CartaSub{})
}
