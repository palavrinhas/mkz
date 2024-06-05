import httpx

def tamanho_arquivo_aceitavel(url):
    try:
        with httpx.Client() as client:
            response = client.head(url)
            file_size = response.headers.get('content-length')

            if file_size:
                size_in_mb = int(file_size) / (1024 * 1024)
                return size_in_mb < 10
            else:
                print("Não foi possível determinar o tamanho do arquivo.")
                return False
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return False
