package db

import (
	"api/models"
	"fmt"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func Connect() {
	dsn := "user=naftalino dbname=pado password= host=localhost port=5432 sslmode=disable TimeZone=America/Sao_Paulo"
	database, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})

	if err != nil {
		fmt.Printf("Não foi possível conectar ao banco de dados. Motivo: %s", err)
	}

	DB = database
	DB.AutoMigrate(
		&models.Wishlist{},
		&models.ColecaoItem{},
		&models.Usuario{},
		&models.Obra{},
		&models.Carta{},
		&models.Subobra{},
		&models.CartaSub{},
		&models.Gifs{},
		&models.Pedidos{},
	)
}
