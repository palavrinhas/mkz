package models

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
	UserID       string `json:"user"`
	Giros        int    `json:"giros"`
	CartaFav     string `json:"carta_fav"`
	Banido       bool   `json:"banido"`
	ColecaoNome  string `json:"colecaoNome"`
	DesejaTrocar bool   `json:"trocar"`
	Premium      bool   `json:"premium"`
	Admin        bool   `json:"admin"`
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
	UserID    string `json:"user_id"`
	ItemID    uint   `json:"item_id"`
	Acumulado uint
}

type Wishlist struct {
	UserID  string `json:"user_id"`
	CartaID int    `json:"carta_id"`
}
