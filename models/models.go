package models

// Estas structs são referentes às tabelas criadas no banco de dados.
// Todas elas tem suas colunas e tipo de retorno json.
// Se você não conseguir ler, só lamentos, skill issue.

type CartaSub struct {
	CartaSubID int    `gorm:"primaryKey"`
	Nome       string `json:"nome"`
	SubObra    int    `json:"subID"`
	Imagem     string `json:"imagem"`
	Creditos   string `json:"creditos"`
}

type Subobra struct {
	SubobraID    int    `gorm:"primaryKey"`
	Nome         string `json:"nome"`
	ObraOriginal int    `json:"obraoriginal"`
	Imagem       string `json:"imagem"`
}

type Usuario struct {
	UserID       string `json:"user_id"`
	Giros        int    `json:"giros"`
	CartaFav     int    `json:"carta_fav"`
	Banido       bool   `json:"banido"`
	Privado      bool   `json:"privado"`
	DesejaTrocar bool   `json:"trocar"`
	Premium      bool   `json:"premium"`
	Admin        bool   `json:"admin"`
	Moedas       int    `json:"moedas"`
	Notificar    bool   `json:"notificar"`
}

type Obra struct {
	ObraID    int    `gorm:"primaryKey;autoIncrement"`
	Nome      string `json:"nome"`
	Categoria string `json:"categoria"`
	Imagem    string `json:"imagem"`
}

type Carta struct {
	ID        int    `gorm:"primaryKey"`
	Nome      string `json:"nome"`
	Obra      int    `json:"obra"`
	Imagem    string `json:"imagem"`
	Categoria string `json:"categoria"`
	Credito   string `json:"creditos"`
}

type ColecaoItem struct {
	UserID      string `json:"user_id"`
	ItemID      uint   `json:"item_id"`
	Acumulado   uint   `json:"acumulado"`
	PersonalGif bool   `json:"permitido"`
}

type CartaComAcumulado struct {
	Carta
	Acumulado uint `json:"acumulado"`
}

type Gifs struct {
	UserID  string `json:"user_id"`
	CartaID int    `json:"carta_id"`
	GifLink string `json:"link"`
}

type Pedidos struct {
	PedidoID   int    `json:"id_pedido"`
	UserID     string `json:"user_id"`
	CartaID    int    `json:"carta_id"`
	GifLink    string `json:"gif_link"`
	MensagemID string `json:"mensagem_id"`
}

type Wishlist struct {
	UserID  string `json:"user_id"`
	CartaID int    `json:"carta_id"`
}
