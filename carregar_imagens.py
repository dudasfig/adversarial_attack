from PIL import Image

def load_image(image_path):
    try:
        image = Image.open(image_path)
        print(f"Imagem carregada com sucesso: {image_path}")
        return image
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")
        return None

# Carregar as imagens diretamente da pasta local
reprovado_img = load_image("./reprovado.jpg")
aprovado_img = load_image("./aprovado.jpg")

# Exemplo de verificação
if reprovado_img:
    reprovado_img.show()  # Mostra a imagem "reprovado.jpg"

if aprovado_img:
    aprovado_img.show()  # Mostra a imagem "aprovado.jpg"
