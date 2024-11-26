import numpy as np
from PIL import Image
import random


class SquareAttack:
    def __init__(self, eps, n_iters, initial_p, num_squares):
        """
        :param eps: Intensidade máxima da perturbação.
        :param n_iters: Número de iterações do ataque.
        :param initial_p: Tamanho inicial do quadrado como proporção da imagem.
        :param num_squares: Número de quadrados aplicados por iteração.
        """
        self.eps = eps
        self.n_iters = n_iters
        self.initial_p = initial_p
        self.num_squares = num_squares

    def p_selection(self, p_init, it, n_iters):
        """Reduz gradualmente o tamanho do quadrado ao longo das iterações."""
        return p_init * (1 - it / n_iters)

    def apply(self, image, send_image_to_server, server_url):
        """Aplica o Square Attack diretamente na matriz de pixels."""
        width, height = image.size
        perturbed_image = np.array(image, dtype=np.float32) / 255.0  # Normalizar para [0, 1]
        p_init = self.initial_p
        n_features = width * height

        for it in range(self.n_iters):
            p = self.p_selection(p_init, it, self.n_iters)
            s = int(round(np.sqrt(p * n_features)))
            s = max(5, min(s, min(width, height) - 1))  # Limitar tamanho do quadrado

            for _ in range(self.num_squares):
                # Escolher aleatoriamente a posição do quadrado
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
        square_attack = SquareAttack(eps=0.1, n_iters=15, initial_p=0.3, num_squares=5)
        adversarial_image = square_attack.apply(reprovado_img, send_image_to_server, server_url)
        
