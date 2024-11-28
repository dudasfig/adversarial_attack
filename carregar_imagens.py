from PIL import Image

def load_image(image_path):
    try:
        image = Image.open(image_path)
        print(f"Imagem carregada com sucesso: {image_path}")
        return image
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")
        return None
    
reprovado_img = load_image("./reprovado.jpg")

if reprovado_img:
    reprovado_img.show()  

