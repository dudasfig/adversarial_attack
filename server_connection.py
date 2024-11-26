import requests

def send_image_to_server(image, server_url):
    # Salvar a imagem em um arquivo temporário
    temp_path = "temp_image.jpg"
    image.save(temp_path)
    
    try:
        # Abrir o arquivo para envio
        with open(temp_path, "rb") as img_file:
            response = requests.post(server_url, files={"file": img_file})
        
        # Verificar a resposta
        if response.status_code == 200:
            print("Imagem enviada com sucesso!")
            return response.json()  # Retorna a resposta do servidor em JSON
        else:
            print(f"Erro na requisição: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao enviar a imagem: {e}")
        return None

# Exemplo de uso
if __name__ == "__main__":
    from carregar_imagens import load_image  # Importe o código do primeiro arquivo

    # URL do servidor
    server_url = "http://ec2-54-85-67-162.compute-1.amazonaws.com:8080/classify"
    
    # Carregar a imagem reprovado.jpg
    reprovado_img = load_image("./reprovado.jpg")
    
    if reprovado_img:
        # Enviar a imagem para o servidor
        response = send_image_to_server(reprovado_img, server_url)
        
        if response:
            print("Resposta do servidor:", response)
