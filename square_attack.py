import os
import numpy as np
import random
from PIL import Image
from server_connection import send_image_to_server
from carregar_imagens import load_image

class SquareAttack:
    def __init__(self, eps, n_iters, initial_p, num_squares):
        """
        :param eps: Intensidade máxima da perturbação.
        :param n_iters: Número de iterações do ataque.
        :param initial_p: Proporção inicial da área perturbada.
        :param num_squares: Número de quadrados aplicados por iteração.
        """
        self.eps = eps
        self.n_iters = n_iters
        self.initial_p = initial_p
        self.num_squares = num_squares

        os.makedirs("imagens_perturbadas", exist_ok=True)

    def p_selection(self, p_init, it, n_iters):
        it = int(it / n_iters * 10000)
        if 10 < it <= 50:
            return p_init / 2
        elif 50 < it <= 200:
            return p_init / 4
        elif 200 < it <= 500:
            return p_init / 8
        elif 500 < it <= 1000:
            return p_init / 16
        elif 1000 < it <= 2000:
            return p_init / 32
        elif 2000 < it <= 4000:
            return p_init / 64
        elif 4000 < it <= 6000:
            return p_init / 128
        elif 6000 < it <= 8000:
            return p_init / 256
        elif 8000 < it <= 10000:
            return p_init / 512
        else:
            return p_init

    def apply(self, image, send_image_to_server, server_url):
        """Aplica o Square Attack diretamente na matriz de pixels."""
        width, height = image.size
        perturbed_image = np.array(image, dtype=np.float32) / 255.0  # Normalizar para [0, 1]
        p_init = self.initial_p
        n_features = width * height

        for it in range(self.n_iters):
            p = self.p_selection(p_init, it, self.n_iters)
            s = int(round(np.sqrt(p * n_features) * 0.5))  # Tamanho do quadrado
            s = max(1, min(s, min(width, height) - 1))  # Ajusta limites

            for _ in range(self.num_squares):
                # Garantir que o quadrado se encaixe na imagem
                x = random.randint(0, width - s)
                y = random.randint(0, height - s)

                # Gerar perturbação aleatória multiplicativa
                perturbation = np.random.uniform(1 - self.eps, 1 + self.eps, (s, s, 3))

                # Multiplicar a região da imagem pela perturbação
                perturbed_image[y:y + s, x:x + s] *= perturbation

            perturbed_image = np.clip(perturbed_image, 0, 1)  # Garantir valores válidos [0, 1]

            # Enviar imagem perturbada para o servidor
            perturbed_image_uint8 = (perturbed_image * 255).astype(np.uint8)
            perturbed_pil_image = Image.fromarray(perturbed_image_uint8)

            perturbed_pil_image.save(f"imagens_perturbadas/iter_{it + 1}.jpg")

            try:
                response = send_image_to_server(perturbed_pil_image, server_url)
            except Exception as e:
                print(f"Erro ao enviar imagem na iteração {it + 1}: {e}")
                continue

            # Verificar a resposta do servidor
            if response:
                predicted_class = response.get("class")
                confidence = response.get("confidence")
                print(f"Iteração {it + 1}: Classe = {predicted_class}, Confiança = {confidence}")

                if predicted_class == "aprovado\n":
                    print("Ataque bem-sucedido!")
                    perturbed_pil_image.save("adversarial_image.jpg")
                    print("Imagem adversarial salva como 'adversarial_image.jpg'.")
                    return perturbed_pil_image

        print("O ataque não conseguiu enganar o modelo.")
        final_image = Image.fromarray((perturbed_image * 255).astype(np.uint8))
        final_image.save("failed_attack_image.jpg")
        print("Imagem final salva como 'failed_attack_image.jpg'.")
        return final_image

# Exemplo de uso
if __name__ == "__main__":
    from carregar_imagens import load_image
    from server_connection import send_image_to_server

    server_url = "http://ec2-54-85-67-162.compute-1.amazonaws.com:8080/classify"
    reprovado_img = load_image("./reprovado.jpg")

    if reprovado_img:
        square_attack = SquareAttack(eps=0.2, n_iters=200, initial_p=0.45, num_squares=9)
        adversarial_image = square_attack.apply(reprovado_img, send_image_to_server, server_url)
