import arcade
import random
import math

ALTURA = 600
LARGURA = 800
TITULO = "AURA"

PONTOS_PARA_VENCER = 20


# ============================================================
# SPRITES DO JOGO
# ============================================================
class Player(arcade.Sprite):
    def __init__(self, imagem_direita, imagem_esquerda):
        super().__init__(imagem_direita, scale=0.5)
        self.textura_direita = arcade.load_texture(imagem_direita)
        self.textura_esquerda = arcade.load_texture(imagem_esquerda)

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda

        if self.left < 0:
            self.left = 0
        if self.right > LARGURA:
            self.right = LARGURA
        if self.bottom < 0:
            self.bottom = 0
        if self.top > ALTURA:
            self.top = ALTURA


class Moeda(arcade.Sprite):
    def __init__(self):
        super().__init__("moeda.png", scale=0.1)
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(20, ALTURA - 20)


class MoedaEspecial(arcade.Sprite):
    def __init__(self):
        super().__init__("moeda_especial.png", scale=0.5)
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(20, ALTURA - 20)
        self.change_x = random.choice([-3, -2, 2, 3])
        self.change_y = random.choice([-3, -2, 2, 3])

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.top > ALTURA or self.bottom < 0:
            self.change_y *= -1


class Inimigo(arcade.Sprite):
    def __init__(self):
        super().__init__("personagem_inimigo_direita.png", scale=0.1)
        self.textura_direita = arcade.load_texture(
            "personagem_inimigo_direita.png")
        self.textura_esquerda = arcade.load_texture(
            "personagem_inimigo_esquerda.png")

        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(20, ALTURA - 20)
        self.change_x = random.choice([-2, -1, 1, 2])
        self.change_y = random.choice([-2, -1, 1, 2])

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda

        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.top > ALTURA or self.bottom < 0:
            self.change_y *= -1


class InimigoEspecial(arcade.Sprite):
    def __init__(self):
        super().__init__("inimigo_especial.png", scale=0.20)
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(20, ALTURA - 20)
        self.velocidade = 1.5

    def seguir(self, alvo_x, alvo_y):
        dx = alvo_x - self.center_x
        dy = alvo_y - self.center_y
        distancia = math.hypot(dx, dy)
        if distancia != 0:
            self.change_x = (dx / distancia) * self.velocidade
            self.change_y = (dy / distancia) * self.velocidade

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def reposicionar(self):
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(20, ALTURA - 20)


# ============================================================
# TELA 1: MENU PRINCIPAL
# ============================================================
class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color((30, 30, 60))

    def on_draw(self):
        self.clear()
        arcade.draw_text(TITULO, LARGURA / 2, ALTURA - 150,
                         arcade.color.WHITE, 50, anchor_x="center", bold=True)

        arcade.draw_text("[J] Jogar", LARGURA / 2, ALTURA / 2 + 40,
                         arcade.color.YELLOW, 24, anchor_x="center")
        arcade.draw_text("[I] Instruções", LARGURA / 2, ALTURA / 2,
                         arcade.color.YELLOW, 24, anchor_x="center")
        arcade.draw_text("[S] Sobre o Jogo", LARGURA / 2, ALTURA / 2 - 40,
                         arcade.color.YELLOW, 24, anchor_x="center")
        arcade.draw_text("[ESC] Sair", LARGURA / 2, ALTURA / 2 - 80,
                         arcade.color.YELLOW, 24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.J:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.I:
            self.window.show_view(InstrucoesView())
        elif key == arcade.key.S:
            self.window.show_view(SobreView())
        elif key == arcade.key.ESCAPE:
            arcade.exit()


# ============================================================
# TELA 2: INSTRUÇÕES
# ============================================================
class InstrucoesView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color((20, 50, 40))

    def on_draw(self):
        self.clear()
        arcade.draw_text("INSTRUÇÕES", LARGURA / 2, ALTURA - 50,
                         arcade.color.WHITE, 32, anchor_x="center", bold=True)

        arcade.draw_text(
            "Objetivo: cooperem para coletar todas as moedas do mapa.",
            LARGURA / 2, ALTURA - 110,
            arcade.color.WHITE, 16, anchor_x="center"
        )
        arcade.draw_text(
            f"Pontuação final >= {PONTOS_PARA_VENCER}: VITÓRIA!   |   "
            f"Abaixo de {PONTOS_PARA_VENCER}: GAME OVER",
            LARGURA / 2, ALTURA - 135,
            arcade.color.YELLOW_GREEN, 15, anchor_x="center"
        )

        texto = (
            "- Moeda normal: +1 ponto (some ao ser coletada)\n"
            "- Moeda especial: +5 pontos (move-se e rebate nas bordas)\n"
            "- Inimigo comum: -1 ponto ao encostar (fica vagando sempre)\n"
            "- Inimigo especial: -1 ponto, persegue os jogadores (mais lento)\n"
            "  e reaparece em outro lugar do mapa ao tocar alguém"
        )
        arcade.draw_text(texto, LARGURA / 2, ALTURA - 175,
                         arcade.color.WHITE, 15, anchor_x="center",
                         align="center", width=700, multiline=True)

        arcade.draw_text("Controles", LARGURA / 2, ALTURA - 320,
                         arcade.color.WHITE, 18, anchor_x="center", bold=True)
        arcade.draw_text(
            "Jogador 1:  W A S D  (cima / esquerda / baixo / direita)",
            LARGURA / 2, ALTURA - 350,
            arcade.color.WHITE, 15, anchor_x="center"
        )
        arcade.draw_text(
            "Jogador 2:  I J K L  (cima / esquerda / baixo / direita)",
            LARGURA / 2, ALTURA - 375,
            arcade.color.WHITE, 15, anchor_x="center"
        )

        arcade.draw_text("[ESC] ou [M] - Voltar ao Menu", LARGURA / 2, 30,
                         arcade.color.YELLOW, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.M):
            self.window.show_view(MenuView())


# ============================================================
# TELA 3: SOBRE O JOGO
# ============================================================
class SobreView(arcade.View):
    def __init__(self):
        super().__init__()
        self.avatares = arcade.SpriteList()

        integrantes = [
            {"nome": "Gabriel Bueno", "imagem": "avatar1.png"},
            {"nome": "Fábio Grama", "imagem": "avatar2.png"},
            {"nome": "Fábio e Gabriel", "imagem": "avatar3.png"},
        ]

        espacamento = LARGURA / (len(integrantes) + 1)
        self.nomes = []
        for i, pessoa in enumerate(integrantes):
            avatar = arcade.Sprite(pessoa["imagem"], scale=0.5)
            avatar.center_x = espacamento * (i + 1)
            avatar.center_y = ALTURA / 2
            self.avatares.append(avatar)
            self.nomes.append(
                (pessoa["nome"], avatar.center_x, avatar.center_y - 90))

    def on_show_view(self):
        arcade.set_background_color((50, 30, 60))

    def on_draw(self):
        self.clear()
        arcade.draw_text("SOBRE O JOGO", LARGURA / 2, ALTURA - 60,
                         arcade.color.WHITE, 36, anchor_x="center", bold=True)

        self.avatares.draw()

        for nome, x, y in self.nomes:
            arcade.draw_text(nome, x, y, arcade.color.WHITE,
                             18, anchor_x="center")

        arcade.draw_text("[ESC] ou [M] - Voltar ao Menu", LARGURA / 2, 40,
                         arcade.color.YELLOW, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.M):
            self.window.show_view(MenuView())


# ============================================================
# TELA 4: GAMEPLAY
# ============================================================
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.velocidade = 4
        self.pontos = 0
        self.alerta_timer = 0
        self.cooldown_dano1 = 0
        self.cooldown_dano2 = 0

    def setup(self):
        self.pontos = 0
        self.alerta_timer = 0
        self.cooldown_dano1 = 0
        self.cooldown_dano2 = 0

        # ---- Jogador 1 ----
        self.personagem = Player("personagem_cavaleiro_direita.png",
                                 "personagem_cavaleiro_esquerda.png")
        self.personagem.center_x = 300
        self.personagem.center_y = 300
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.personagem)

        # ---- Jogador 2 ----
        self.personagem2 = Player("personagem_cavaleiro2_direita.png",
                                  "personagem_cavaleiro2_esquerda.png")
        self.personagem2.center_x = 500
        self.personagem2.center_y = 300
        self.sprite_jogador2 = arcade.SpriteList()
        self.sprite_jogador2.append(self.personagem2)

        self.moedas_lista = arcade.SpriteList()
        for _ in range(10):
            self.moedas_lista.append(Moeda())

        self.moeda_especial_lista = arcade.SpriteList()
        for _ in range(3):
            self.moeda_especial_lista.append(MoedaEspecial())

        self.inimigos_lista = arcade.SpriteList()
        for _ in range(2):
            self.inimigos_lista.append(Inimigo())

        self.inimigo_especial_lista = arcade.SpriteList()
        for _ in range(1):
            self.inimigo_especial_lista.append(InimigoEspecial())

        self.background = arcade.load_texture("tela_cenario_medieval.png")

    def on_show_view(self):
        arcade.set_background_color((46, 147, 255))

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background, arcade.LBWH(0, 0, LARGURA, ALTURA))

        self.moedas_lista.draw()
        self.moeda_especial_lista.draw()
        self.inimigos_lista.draw()
        self.inimigo_especial_lista.draw()
        self.sprite_jogador.draw()
        self.sprite_jogador2.draw()

        arcade.draw_text(f"Pontos: {self.pontos}", 10, ALTURA - 30,
                         arcade.color.WHITE, 20)

        if self.alerta_timer > 0:
            arcade.draw_text("CUIDADO!", LARGURA / 2 - 60, ALTURA - 60,
                             arcade.color.RED, 28, bold=True)

    def on_update(self, delta_time):
        self.personagem.update(delta_time)
        self.personagem2.update(delta_time)
        self.moedas_lista.update(delta_time)
        self.moeda_especial_lista.update(delta_time)
        self.inimigos_lista.update(delta_time)

        # inimigo especial persegue o jogador mais próximo dele
        for inimigo_esp in self.inimigo_especial_lista:
            d1 = math.hypot(self.personagem.center_x - inimigo_esp.center_x,
                            self.personagem.center_y - inimigo_esp.center_y)
            d2 = math.hypot(self.personagem2.center_x - inimigo_esp.center_x,
                            self.personagem2.center_y - inimigo_esp.center_y)
            alvo = self.personagem if d1 <= d2 else self.personagem2
            inimigo_esp.seguir(alvo.center_x, alvo.center_y)
        self.inimigo_especial_lista.update(delta_time)

        # --- colisões: moeda normal (qualquer jogador coleta) ---
        for jogador in (self.personagem, self.personagem2):
            moedas_atingidas = arcade.check_for_collision_with_list(
                jogador, self.moedas_lista)
            for moeda in moedas_atingidas:
                moeda.remove_from_sprite_lists()
                self.pontos += 1

        # --- moeda especial ---
        for jogador in (self.personagem, self.personagem2):
            especiais_atingidas = arcade.check_for_collision_with_list(
                jogador, self.moeda_especial_lista)
            for m in especiais_atingidas:
                m.remove_from_sprite_lists()
                self.pontos += 5

        # --- inimigo comum (com cooldown separado por jogador) ---
        if self.cooldown_dano1 <= 0:
            atingiu1 = arcade.check_for_collision_with_list(
                self.personagem, self.inimigos_lista)
            if atingiu1:
                self.pontos -= 1
                self.alerta_timer = 1.0
                self.cooldown_dano1 = 0.5
        else:
            self.cooldown_dano1 -= delta_time

        if self.cooldown_dano2 <= 0:
            atingiu2 = arcade.check_for_collision_with_list(
                self.personagem2, self.inimigos_lista)
            if atingiu2:
                self.pontos -= 1
                self.alerta_timer = 1.0
                self.cooldown_dano2 = 0.5
        else:
            self.cooldown_dano2 -= delta_time

        # --- inimigo especial (teleporta ao tocar qualquer jogador) ---
        for jogador in (self.personagem, self.personagem2):
            especiais_inimigo = arcade.check_for_collision_with_list(
                jogador, self.inimigo_especial_lista)
            for ie in especiais_inimigo:
                self.pontos -= 1
                ie.reposicionar()

        if self.alerta_timer > 0:
            self.alerta_timer -= delta_time

        # CONDIÇÃO DE FIM DE JOGO: coletaram todas as moedas
        if len(self.moedas_lista) == 0 and len(self.moeda_especial_lista) == 0:
            if self.pontos >= PONTOS_PARA_VENCER:
                self.window.show_view(VitoriaView(self.pontos))
            else:
                self.window.show_view(GameOverView(self.pontos))

    def on_key_press(self, key, modifiers):
        # Jogador 1: WASD
        if key == arcade.key.D:
            self.personagem.change_x = self.velocidade
        if key == arcade.key.A:
            self.personagem.change_x = -self.velocidade
        if key == arcade.key.W:
            self.personagem.change_y = self.velocidade
        if key == arcade.key.S:
            self.personagem.change_y = -self.velocidade

        # Jogador 2: IJKL
        if key == arcade.key.L:
            self.personagem2.change_x = self.velocidade
        if key == arcade.key.J:
            self.personagem2.change_x = -self.velocidade
        if key == arcade.key.I:
            self.personagem2.change_y = self.velocidade
        if key == arcade.key.K:
            self.personagem2.change_y = -self.velocidade

        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.D, arcade.key.A):
            self.personagem.change_x = 0
        if key in (arcade.key.W, arcade.key.S):
            self.personagem.change_y = 0

        if key in (arcade.key.L, arcade.key.J):
            self.personagem2.change_x = 0
        if key in (arcade.key.I, arcade.key.K):
            self.personagem2.change_y = 0


# ============================================================
# TELA 5: VITÓRIA (pontuação >= PONTOS_PARA_VENCER)
# ============================================================
class VitoriaView(arcade.View):
    def __init__(self, pontos_finais):
        super().__init__()
        self.pontos_finais = pontos_finais

    def on_show_view(self):
        arcade.set_background_color((10, 60, 20))

    def on_draw(self):
        self.clear()
        arcade.draw_text("PARABÉNS! VOCÊS VENCERAM!", LARGURA / 2, ALTURA / 2 + 60,
                         arcade.color.GREEN, 40, anchor_x="center", bold=True)
        arcade.draw_text(f"Pontuação final: {self.pontos_finais}",
                         LARGURA / 2, ALTURA / 2, arcade.color.WHITE, 24,
                         anchor_x="center")
        arcade.draw_text("[ENTER] Jogar novamente   [ESC] Menu",
                         LARGURA / 2, ALTURA / 2 - 60, arcade.color.YELLOW, 18,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


# ============================================================
# TELA 6: GAME OVER (pontuação < PONTOS_PARA_VENCER)
# ============================================================
class GameOverView(arcade.View):
    def __init__(self, pontos_finais):
        super().__init__()
        self.pontos_finais = pontos_finais

    def on_show_view(self):
        arcade.set_background_color((10, 10, 10))

    def on_draw(self):
        self.clear()
        arcade.draw_text("FIM DE JOGO", LARGURA / 2, ALTURA / 2 + 60,
                         arcade.color.RED, 48, anchor_x="center", bold=True)
        arcade.draw_text(f"Pontuação final: {self.pontos_finais}",
                         LARGURA / 2, ALTURA / 2, arcade.color.WHITE, 24,
                         anchor_x="center")
        arcade.draw_text("[ENTER] Jogar novamente   [ESC] Menu",
                         LARGURA / 2, ALTURA / 2 - 60, arcade.color.YELLOW, 18,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


# ============================================================
# JANELA PRINCIPAL
# ============================================================
class Mainwindow(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)
        menu_view = MenuView()
        self.show_view(menu_view)


def executar():
    jogo = Mainwindow()
    arcade.run()


if __name__ == "__main__":
    executar()