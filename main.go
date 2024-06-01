package main

/*
@naftalino<t.me/naftalino>
*/

import (
	internal "api/controllers"
	"api/db"

	"github.com/gofiber/fiber/v2"
)

func main() {

	db.Connect()

	app := fiber.New()

	app.Use(func(c *fiber.Ctx) error {
		c.Set("Access-Control-Allow-Origin", "*")
		c.Set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE")
		c.Set("Access-Control-Allow-Headers", "*")

		if c.Method() == "OPTIONS" {
			return c.SendStatus(fiber.StatusNoContent)
		}

		return c.Next()
	})

	app.Get("/cadastrar/admin/:user_id", internal.CriarAdmin)

	//app.Get("/subobras", internal.GetSubobras)
	//app.Post("/cadastrar/subobra", internal.CriarSubobra)
	//app.Get("/subobra/:subobra_id", internal.BuscarSubobraPorID)
	//app.Post("/editar/subobra/:subobra_id")
	//app.Post("/cadastrar/cartasubobra", internal.CriarCartaSubobra)
	//app.Get("/carta/subobra/:carta_id")
	//app.Get("/editar/carta/subobra/:carta_id")

	app.Get("/obras", internal.GetObras)
	app.Post("/cadastrar/obra", internal.CriarObra)
	app.Get("/obra/:obra_id", internal.BuscarObraPorID)
	app.Post("/obra-nome/", internal.BuscarObraPorNome)
	app.Post("/carta-nome/", internal.BuscarCartaPorNome)
	app.Post("/editar/obra/:obra_id", internal.EditarObra)
	app.Get("/sortear/obras/:categoria", internal.SortearObraPorCategoria)
	app.Get("/sortear/carta/:obra_id", internal.SortearCartaPorObraID)
	app.Get("/sortear/subobras/", internal.SortearSubobra)
	app.Post("/cadastrar/carta", internal.CriarCarta)
	app.Get("/carta/:carta_id", internal.BuscarCartaPorID)
	app.Post("/editar/carta/:carta_id", internal.EditarCarta)
	app.Get("/usuario/:user_id", internal.BuscarUsuario)
	app.Post("/colecao/:userID/adicionar", internal.InserirCarta)
	app.Get("/colecao/:userID", internal.PegarColecao)
	app.Get("/colecao/bruta/:user_id", internal.PegarColecaoBruta)
	app.Post("/colecao/:userID/remover", internal.RemoverCarta)
	app.Get("/cadastrar/usuario/:user_id", internal.ContaNova)
	app.Get("/colecao/filtrada/:userID/:obraID", internal.PegarColecaoFiltradaPorID)
	app.Post("/set-fav/", internal.SetarCartaFavorita)

	// Rotas de giro (remover/adicionar)
	app.Get("/giros/remover/:userID", internal.RemoverGiro)
	app.Post("/inserir/giros/:user", internal.InserirGiros)

	// Rotas wishlist
	app.Get("/wishlist/:userID", internal.GetWishlist)
	app.Post("/wishlist/adicionar", internal.AdicionarItemWishlist)
	app.Get("/wishlist/remover/:userID/:cartaID", internal.RemoverItemWishlist)
	app.Get("/carta/obra/:obra_id", internal.CartasPorObra)

	// não terminado
	app.Get("/banir/:userID", internal.Banir)

	app.Listen(":3000")
}
