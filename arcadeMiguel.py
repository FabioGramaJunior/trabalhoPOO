import arcade
import random

ALTURA = 600
LARGURA = 800
TITULO = "AURA"

class Moeda(arcade.Sprite):
    def __init__(self):
        super().__init__("moeda.png", scale=0.1)


    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.right > LARGURA or  self.left < 0:
            self.change_x *= -1
            
        if self.top > ALTURA or self.bottom < 0:
            self.change_y *= -1
            
class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("player_direita.png", scale=0.5)
        self.textura_direita = arcade.load_texture("player_direita.png")
        self.textura_esquerda = arcade.load_texture("player_esquerda.png")

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda
        
        if self.right > LARGURA:
            self.change_x = 0

        elif self.left < 0:
            self.change_x = 0
        
        if self.top > ALTURA:
            self.change_y = 0

        elif self.bottom < 0:
            self.change_y = 0

    

class Mainwindow(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA, ALTURA,TITULO)

        arcade.set_background_color((46, 147, 255))

        self.velocidade = 4

        self.personagem = Player()
        self.personagem.center_x = 400
        self.personagem.center_y = 300
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.personagem)



        self.moeda = Moeda()
        self.moeda.center_x = 600
        self.moeda.center_y = 500
        self.moeda.change_x = self.velocidade
        self.moeda.change_y = self.velocidade

        self.moeda2 = Moeda()
        self.moeda2.left = 0
        self.moeda2.bottom = 300

        self.sprite_moedas = arcade.SpriteList()
        self.sprite_moedas.append(self.moeda)
        self.sprite_moedas.append(self.moeda2)

        for i in range(25):
            self.moeda_simples = Moeda()

            self.moeda_simples.center_x = random.randint(50, LARGURA-50)
            self.moeda_simples.center_y = random.randint(50, ALTURA-50)

            self.sprite_moedas.append(self.moeda_simples)
      

    def on_draw(self):
        self.clear()
        self.sprite_jogador.draw()
        self.sprite_moedas.draw()
        
    def on_update(self, delta_time):
        self.sprite_jogador.update(delta_time)
        self.sprite_moedas.update(delta_time)

    def on_key_press(self, key, modifiers):
        if(key ==arcade.key.D):
            self.personagem.change_x += self.velocidade
        if(key == arcade.key.A):
            self.personagem.change_x -= self.velocidade
        if(key == arcade.key.W):
            self.personagem.change_y += self.velocidade
        if(key == arcade.key.S):
            self.personagem.change_y -= self.velocidade

    def on_key_release(self, key, modifiers):
        if(key ==arcade.key.D):
            self.personagem.change_x = 0
        if(key == arcade.key.A):
            self.personagem.change_x = 0
        if(key == arcade.key.W):
            self.personagem.change_y = 0
        if(key == arcade.key.S):
            self.personagem.change_y = 0
def executar():
    jogo = Mainwindow()
    arcade.run()

if __name__ == "__main__":
    executar()