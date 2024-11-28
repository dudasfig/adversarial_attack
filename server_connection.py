import requests

def send_image_to_server(image, server_url):
    temp_path = "temp_image.jpg"
    image.save(temp_path)
    
    try:
        with open(temp_path, "rb") as img_file:
            response = requests.post(server_url, files={"file": img_file})
        
        if response.status_code == 200:
            print("Imagem enviada com sucesso!")
            return response.json()  
        else:
            print(f"Erro na requisição: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao enviar a imagem: {e}")
        return None

if __name__ == "__main__":
    from carregar_imagens import load_image  

    server_url = "http://ec2-54-85-67-162.compute-1.amazonaws.com:8080/classify"
    
    reprovado_img = load_image("./reprovado.jpg")
    
    if reprovado_img:
        response = send_image_to_server(reprovado_img, server_url)
        
        if response:
            print("Resposta do servidor:", response)
