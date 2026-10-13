import arcade
import random
import math
import datetime
from peewee import (SqliteDatabase, Model, CharField,
                    IntegerField, FloatField, DateTimeField)

ALTURA = 600
LARGURA = 800
TITULO = "AURA"

GRAVIDADE = 0.5
FORCA_PULO = 12
TAM_BLOCO = 40

# ---- Spritesheet do jogador (ajuste conforme a sua imagem) ----
QUADRO_LARGURA = 64
QUADRO_ALTURA = 64
SHEET_COLUNAS = 6
SHEET_QUADROS = 6
# Ordem esperada na folha: 0 = parado | 1 a 4 = caminhada | 5 = pulo


# ============================================================
# BANCO DE DADOS (PEEWEE ORM)
# ============================================================
db = SqliteDatabase("ranking.db")


class BaseModel(Model):
    class Meta:
        database = db


class Pontuacao(BaseModel):
    nome_jogador = CharField()
    pontos = IntegerField()
    tempo_partida = FloatField()
    data_hora = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{self.nome_jogador} - {self.pontos} pts ({self.tempo_partida:.1f}s)"

    @classmethod
    def registrar(cls, nome, pontos, tempo):
        """CREATE: grava uma nova pontuação."""
        return cls.create(nome_jogador=nome, pontos=pontos, tempo_partida=tempo)

    @classmethod
    def top10(cls):
        """READ: os 10 melhores, do maior para o menor."""
        return cls.select().order_by(cls.pontos.desc()).limit(10)


def iniciar_banco():
    db.connect(reuse_if_open=True)
    db.create_tables([Pontuacao])


# ============================================================
# BLOCO (chão e plataformas)
# ============================================================
class Bloco(arcade.SpriteSolidColor):
    def __init__(self, x, y, largura=TAM_BLOCO, altura=TAM_BLOCO, cor=(90, 60, 30)):
        super().__init__(largura, altura, color=cor)
        self.center_x = x
        self.center_y = y


# ============================================================
# PLAYER (com spritesheet e máquina de estados)
# ============================================================
class Player(arcade.Sprite):
    def __init__(self, arquivo_sheet):
        # carrega a folha e fatia em quadros
        sheet = arcade.load_spritesheet(arquivo_sheet)
        quadros = sheet.get_texture_grid(
            size=(QUADRO_LARGURA, QUADRO_ALTURA),
            columns=SHEET_COLUNAS,
            count=SHEET_QUADROS,
        )

        # separa os quadros por estado (lado direito)
        self.tex_parado = [quadros[0]]
        self.tex_andando = quadros[1:5]
        self.tex_pulo = [quadros[5]]

        # versões espelhadas (lado esquerdo)
        self.tex_parado_esq = [t.flip_left_right() for t in self.tex_parado]
        self.tex_andando_esq = [t.flip_left_right() for t in self.tex_andando]
        self.tex_pulo_esq = [t.flip_left_right() for t in self.tex_pulo]

        super().__init__(self.tex_parado[0], scale=1.0)

        self.virado_para = "direita"
        self.indice_quadro = 0
        self.tempo_animacao = 0

    def update(self, delta_time=1 / 60):
        # --- direção ---
        if self.change_x > 0:
            self.virado_para = "direita"
        elif self.change_x < 0:
            self.virado_para = "esquerda"

        direita = self.virado_para == "direita"

        # --- MÁQUINA DE ESTADOS (prioridade: Pulo > Parado > Andando) ---
        if self.change_y != 0:
            # 1) pulo / queda
            lista = self.tex_pulo if direita else self.tex_pulo_esq
            self.texture = lista[0]
        elif self.change_x == 0:
            # 2) idle
            lista = self.tex_parado if direita else self.tex_parado_esq
            self.texture = lista[0]
        else:
            # 3) caminhando: troca de quadro a cada 100 ms
            self.tempo_animacao += delta_time
            if self.tempo_animacao >= 0.1:
                self.tempo_animacao = 0
                self.indice_quadro = (self.indice_quadro + 1) % len(self.tex_andando)
            lista = self.tex_andando if direita else self.tex_andando_esq
            self.texture = lista[self.indice_quadro]

        # --- trava nas bordas laterais e no teto ---
        if self.left < 0:
            self.left = 0
        if self.right > LARGURA:
            self.right = LARGURA
        if self.top > ALTURA:
            self.top = ALTURA
            self.change_y = 0


# ============================================================
# MOEDAS E INIMIGOS
# ============================================================
class Moeda(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("moeda.png", scale=0.2)
        self.center_x = x
        self.center_y = y


class MoedaEspecial(arcade.Sprite):
    def __init__(self):
        super().__init__("moeda_especial.png", scale=0.5)
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(100, ALTURA - 20)
        self.change_x = random.choice([-3, -2, 2, 3])
        self.change_y = random.choice([-3, -2, 2, 3])

    def update(self, delta_time=1 / 60):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.top > ALTURA or self.bottom < 0:
            self.change_y *= -1


class Inimigo(arcade.Sprite):
    def __init__(self):
        super().__init__("personagem_inimigo_direita.png", scale=0.2)
        self.textura_direita = arcade.load_texture("personagem_inimigo_direita.png")
        self.textura_esquerda = arcade.load_texture("personagem_inimigo_esquerda.png")

        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(100, ALTURA - 20)
        self.change_x = random.choice([-2, -1, 1, 2])
        self.change_y = random.choice([-2, -1, 1, 2])

    def update(self, delta_time=1 / 60):
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
        super().__init__("inimigo_especial.png", scale=0.2)
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(100, ALTURA - 20)
        self.velocidade = 1.5

    def seguir(self, alvo_x, alvo_y):
        dx = alvo_x - self.center_x
        dy = alvo_y - self.center_y
        distancia = math.hypot(dx, dy)
        if distancia != 0:
            self.change_x = (dx / distancia) * self.velocidade
            self.change_y = (dy / distancia) * self.velocidade

    def update(self, delta_time=1 / 60):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def reposicionar(self):
        self.center_x = random.randint(20, LARGURA - 20)
        self.center_y = random.randint(100, ALTURA - 20)


# ============================================================
# TELA 1: MENU PRINCIPAL
# ============================================================
class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color((30, 30, 60))

    def on_draw(self):
        self.clear()
        arcade.draw_text(TITULO, LARGURA / 2, ALTURA - 130,
                         arcade.color.WHITE, 50, anchor_x="center", bold=True)

        opcoes = ["[J] Jogar", "[I] Instruções", "[S] Sobre o Jogo",
                  "[R] Ranking", "[ESC] Sair"]
        for i, texto in enumerate(opcoes):
            arcade.draw_text(texto, LARGURA / 2, ALTURA / 2 + 60 - i * 40,
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
        elif key == arcade.key.R:
            self.window.show_view(TelaRanking())
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

        texto = (
            "Objetivo: os dois jogadores cooperam para coletar\n"
            "todas as moedas do mapa e vencer juntos.\n\n"
            "- Moedas normais: +1 ponto (ficam sobre as plataformas)\n"
            "- Moedas especiais: +5 pontos, voam e rebatem nas bordas\n"
            "- Inimigos comuns: -1 ponto ao encostar, vagam sempre\n"
            "- Inimigos especiais: -1 ponto, perseguem os jogadores (mais lentos)\n"
            "  e reaparecem em outro lugar do mapa ao tocar alguém\n\n"
            "Jogador 1:  A / D - andar    W - pular\n"
            "Jogador 2:  J / L - andar    I - pular\n"
            "(não é possível pular duas vezes no ar)\n"
        )

        arcade.draw_text(texto, LARGURA / 2, ALTURA / 2 + 20,
                         arcade.color.WHITE, 15, anchor_x="center",
                         align="center", width=700, multiline=True)

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
            {"nome": "Nome 1", "imagem": "avatar1.png"},
            {"nome": "Nome 2", "imagem": "avatar2.png"},
            {"nome": "Nome 3", "imagem": "avatar3.png"},
        ]

        espacamento = LARGURA / (len(integrantes) + 1)
        self.nomes = []
        for i, pessoa in enumerate(integrantes):
            avatar = arcade.Sprite(pessoa["imagem"], scale=0.5)
            avatar.center_x = espacamento * (i + 1)
            avatar.center_y = ALTURA / 2
            self.avatares.append(avatar)
            self.nomes.append((pessoa["nome"], avatar.center_x, avatar.center_y - 90))

    def on_show_view(self):
        arcade.set_background_color((50, 30, 60))

    def on_draw(self):
        self.clear()
        arcade.draw_text("SOBRE O JOGO", LARGURA / 2, ALTURA - 60,
                         arcade.color.WHITE, 36, anchor_x="center", bold=True)

        self.avatares.draw()

        for nome, x, y in self.nomes:
            arcade.draw_text(nome, x, y, arcade.color.WHITE, 18, anchor_x="center")

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
        self.tempo_partida = 0.0
        self.alerta_timer = 0
        self.cooldown_dano1 = 0
        self.cooldown_dano2 = 0

    def setup(self):
        self.pontos = 0
        self.tempo_partida = 0.0
        self.alerta_timer = 0
        self.cooldown_dano1 = 0
        self.cooldown_dano2 = 0

        # ---- Cenário: chão + plataformas (SpriteList de Bloco) ----
        self.blocos = arcade.SpriteList()

        # chão (topo em y = 40)
        for x in range(0, LARGURA, TAM_BLOCO):
            self.blocos.append(Bloco(x + TAM_BLOCO / 2, TAM_BLOCO / 2))

        # plataformas suspensas: (x_inicial, y_do_topo, quantidade_de_blocos)
        plataformas = [
            (100, 130, 4),
            (520, 130, 4),
            (300, 220, 5),
            (120, 310, 3),
            (560, 310, 3),
        ]
        for x_ini, y_topo, qtd in plataformas:
            for i in range(qtd):
                x = x_ini + i * TAM_BLOCO + TAM_BLOCO / 2
                self.blocos.append(Bloco(x, y_topo - 10, TAM_BLOCO, 20, (120, 80, 40)))

        # ---- Jogador 1 ----
        self.personagem = Player("player_spritesheet.png")
        self.personagem.center_x = 300
        self.personagem.center_y = 120
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.personagem)

        # ---- Jogador 2 ----
        self.personagem2 = Player("player_spritesheet.png")  # troque pela folha do P2, se tiver
        self.personagem2.center_x = 500
        self.personagem2.center_y = 120
        self.sprite_jogador2 = arcade.SpriteList()
        self.sprite_jogador2.append(self.personagem2)

        # ---- Motores de física ----
        self.physics_engine1 = arcade.PhysicsEnginePlatformer(
            self.personagem, walls=self.blocos, gravity_constant=GRAVIDADE)
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.personagem2, walls=self.blocos, gravity_constant=GRAVIDADE)

        # ---- Moedas normais: nascem em cima de blocos (sempre alcançáveis) ----
        self.moedas_lista = arcade.SpriteList()
        for _ in range(10):
            bloco = random.choice(self.blocos)
            self.moedas_lista.append(Moeda(bloco.center_x, bloco.top + 25))

        self.moeda_especial_lista = arcade.SpriteList()
        for _ in range(5):
            self.moeda_especial_lista.append(MoedaEspecial())

        self.inimigos_lista = arcade.SpriteList()
        for _ in range(2):
            self.inimigos_lista.append(Inimigo())

        self.inimigo_especial_lista = arcade.SpriteList()
        self.inimigo_especial_lista.append(InimigoEspecial())

        self.background = arcade.load_texture("tela_cenario_medieval.png")

    def on_show_view(self):
        arcade.set_background_color((46, 147, 255))

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, LARGURA, ALTURA))

        self.blocos.draw()
        self.moedas_lista.draw()
        self.moeda_especial_lista.draw()
        self.inimigos_lista.draw()
        self.inimigo_especial_lista.draw()
        self.sprite_jogador.draw()
        self.sprite_jogador2.draw()

        arcade.draw_text(f"Pontos: {self.pontos}", 10, ALTURA - 30,
                         arcade.color.WHITE, 20)
        arcade.draw_text(f"Tempo: {self.tempo_partida:.0f}s", LARGURA - 130, ALTURA - 30,
                         arcade.color.WHITE, 20)

        if self.alerta_timer > 0:
            arcade.draw_text("CUIDADO!", LARGURA / 2 - 60, ALTURA - 60,
                             arcade.color.RED, 28, bold=True)

    def on_update(self, delta_time):
        self.tempo_partida += delta_time

        # 1) física (gravidade + colisão com blocos) move os jogadores
        self.physics_engine1.update()
        self.physics_engine2.update()

        # 2) animação / limites dos jogadores
        self.personagem.update(delta_time)
        self.personagem2.update(delta_time)

        self.moeda_especial_lista.update(delta_time)
        self.inimigos_lista.update(delta_time)

        # inimigo especial persegue o jogador mais próximo
        for inimigo_esp in self.inimigo_especial_lista:
            d1 = math.hypot(self.personagem.center_x - inimigo_esp.center_x,
                            self.personagem.center_y - inimigo_esp.center_y)
            d2 = math.hypot(self.personagem2.center_x - inimigo_esp.center_x,
                            self.personagem2.center_y - inimigo_esp.center_y)
            alvo = self.personagem if d1 <= d2 else self.personagem2
            inimigo_esp.seguir(alvo.center_x, alvo.center_y)
        self.inimigo_especial_lista.update(delta_time)

        # --- moedas normais ---
        for jogador in (self.personagem, self.personagem2):
            for moeda in arcade.check_for_collision_with_list(jogador, self.moedas_lista):
                moeda.remove_from_sprite_lists()
                self.pontos += 1

        # --- moedas especiais ---
        for jogador in (self.personagem, self.personagem2):
            for m in arcade.check_for_collision_with_list(jogador, self.moeda_especial_lista):
                m.remove_from_sprite_lists()
                self.pontos += 5

        # --- inimigo comum (nunca é removido; cooldown por jogador) ---
        if self.cooldown_dano1 <= 0:
            if arcade.check_for_collision_with_list(self.personagem, self.inimigos_lista):
                self.pontos -= 1
                self.alerta_timer = 1.0
                self.cooldown_dano1 = 0.5
        else:
            self.cooldown_dano1 -= delta_time

        if self.cooldown_dano2 <= 0:
            if arcade.check_for_collision_with_list(self.personagem2, self.inimigos_lista):
                self.pontos -= 1
                self.alerta_timer = 1.0
                self.cooldown_dano2 = 0.5
        else:
            self.cooldown_dano2 -= delta_time

        # --- inimigo especial (teleporta) ---
        for jogador in (self.personagem, self.personagem2):
            for ie in arcade.check_for_collision_with_list(jogador, self.inimigo_especial_lista):
                self.pontos -= 1
                ie.reposicionar()

        if self.alerta_timer > 0:
            self.alerta_timer -= delta_time

        # --- fim de jogo ---
        if len(self.moedas_lista) == 0 and len(self.moeda_especial_lista) == 0:
            self.window.show_view(GameOverView(self.pontos, self.tempo_partida))

    def on_key_press(self, key, modifiers):
        # Jogador 1: A / D andam, W pula (só se estiver no chão)
        if key == arcade.key.D:
            self.personagem.change_x = self.velocidade
        if key == arcade.key.A:
            self.personagem.change_x = -self.velocidade
        if key == arcade.key.W and self.physics_engine1.can_jump():
            self.personagem.change_y = FORCA_PULO

        # Jogador 2: L / J andam, I pula
        if key == arcade.key.L:
            self.personagem2.change_x = self.velocidade
        if key == arcade.key.J:
            self.personagem2.change_x = -self.velocidade
        if key == arcade.key.I and self.physics_engine2.can_jump():
            self.personagem2.change_y = FORCA_PULO

        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.D, arcade.key.A):
            self.personagem.change_x = 0
        if key in (arcade.key.L, arcade.key.J):
            self.personagem2.change_x = 0


# ============================================================
# TELA 5: GAME OVER (digita o nome e salva no banco)
# ============================================================
class GameOverView(arcade.View):
    def __init__(self, pontos_finais, tempo_partida):
        super().__init__()
        self.pontos_finais = pontos_finais
        self.tempo_partida = tempo_partida
        self.nome = ""
        self.salvo = False

    def on_show_view(self):
        arcade.set_background_color((10, 10, 10))

    def on_draw(self):
        self.clear()
        arcade.draw_text("FIM DE JOGO", LARGURA / 2, ALTURA - 120,
                         arcade.color.RED, 48, anchor_x="center", bold=True)
        arcade.draw_text(f"Pontuação final: {self.pontos_finais}   |   Tempo: {self.tempo_partida:.1f}s",
                         LARGURA / 2, ALTURA - 180, arcade.color.WHITE, 22,
                         anchor_x="center")

        if not self.salvo:
            arcade.draw_text("Digite seu nome:", LARGURA / 2, ALTURA / 2 + 20,
                             arcade.color.YELLOW, 22, anchor_x="center")
            arcade.draw_text(self.nome + "_", LARGURA / 2, ALTURA / 2 - 30,
                             arcade.color.WHITE, 30, anchor_x="center")
            arcade.draw_text("[ENTER] Salvar   [ESC] Menu (sem salvar)",
                             LARGURA / 2, 80, arcade.color.GRAY, 16,
                             anchor_x="center")
        else:
            arcade.draw_text("Pontuação salva!", LARGURA / 2, ALTURA / 2 + 20,
                             arcade.color.GREEN, 26, anchor_x="center")
            arcade.draw_text("[ENTER] Jogar novamente   [R] Ranking   [ESC] Menu",
                             LARGURA / 2, ALTURA / 2 - 40, arcade.color.YELLOW, 18,
                             anchor_x="center")

    def on_text(self, text):
        # captura de texto digitado (só enquanto não salvou)
        if self.salvo:
            return
        if text.isprintable() and len(self.nome) < 12:
            self.nome += text

    def on_key_press(self, key, modifiers):
        if not self.salvo:
            if key == arcade.key.BACKSPACE:
                self.nome = self.nome[:-1]
            elif key in (arcade.key.ENTER, arcade.key.NUM_ENTER):
                nome = self.nome.strip() or "Anônimo"
                registro = Pontuacao.registrar(nome, self.pontos_finais, self.tempo_partida)
                print(registro)  # usa o __str__ do modelo
                self.salvo = True
            elif key == arcade.key.ESCAPE:
                self.window.show_view(MenuView())
        else:
            if key in (arcade.key.ENTER, arcade.key.NUM_ENTER):
                game_view = GameView()
                game_view.setup()
                self.window.show_view(game_view)
            elif key == arcade.key.R:
                self.window.show_view(TelaRanking())
            elif key == arcade.key.ESCAPE:
                self.window.show_view(MenuView())


# ============================================================
# TELA 6: RANKING (Top 10)
# ============================================================
class TelaRanking(arcade.View):
    def __init__(self):
        super().__init__()
        # consulta feita UMA vez, aqui no __init__ (nunca no on_draw)
        self.melhores = list(Pontuacao.top10())

    def on_show_view(self):
        arcade.set_background_color((25, 25, 50))

    def on_draw(self):
        self.clear()
        arcade.draw_text("TOP 10 - RANKING", LARGURA / 2, ALTURA - 60,
                         arcade.color.GOLD, 34, anchor_x="center", bold=True)

        if not self.melhores:
            arcade.draw_text("Nenhuma pontuação registrada ainda.",
                             LARGURA / 2, ALTURA / 2, arcade.color.WHITE, 22,
                             anchor_x="center")
        else:
            # cabeçalho
            arcade.draw_text("#", 130, ALTURA - 115, arcade.color.GRAY, 16)
            arcade.draw_text("Jogador", 190, ALTURA - 115, arcade.color.GRAY, 16)
            arcade.draw_text("Pontos", 470, ALTURA - 115, arcade.color.GRAY, 16)
            arcade.draw_text("Tempo", 590, ALTURA - 115, arcade.color.GRAY, 16)

            for i, p in enumerate(self.melhores):
                y = ALTURA - 150 - i * 36
                cor = arcade.color.YELLOW if i == 0 else arcade.color.WHITE
                arcade.draw_text(f"{i + 1}º", 130, y, cor, 20)
                arcade.draw_text(p.nome_jogador, 190, y, cor, 20)
                arcade.draw_text(str(p.pontos), 470, y, cor, 20)
                arcade.draw_text(f"{p.tempo_partida:.1f}s", 590, y, cor, 20)

        arcade.draw_text("[ESC] ou [M] - Voltar ao Menu", LARGURA / 2, 25,
                         arcade.color.YELLOW, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.M):
            self.window.show_view(MenuView())


# ============================================================
# JANELA PRINCIPAL
# ============================================================
class Mainwindow(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)
        self.show_view(MenuView())


def executar():
    iniciar_banco()
    jogo = Mainwindow()
    arcade.run()


if __name__ == "__main__":
    executar()