from random import random
import pygame
from pygame.locals import *
from myutils import load_image

LARGURA = 640 #Largura (em pixels) da tela
ALTURA  = 220 #Altura (em pixels) da tela

DELAY_INIMIGO       = 1500 #Intervalo de tempo (msecs) entre os inimigos
PROB_INIMIGO        = 0.60 #A probabilidade (em %) de um novo inimigo ser adicionado
INIMIGOS_PARA_MATAR = 10   #Numero de inimigos para matar antes de aumentar a dificuldade


#Criacao da tela e definicao do titulo
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Spritesheet Test')
fonte = pygame.font.Font(None, 30)

#A importacao dos sprites deve ser feita apos a criacao da tela
from personagens import Marine, Robo, CaranguejoGigante

#Esta classe modela um jogo de plataforma simples
class Jogo:
    def __init__(self):
        self.inicializa()

    def inicializa(self):
        #Variaveis principais do jogo
        self.background = load_image('background.gif')
        self.marine     = Marine([300, 210])
        self.chefe      = CaranguejoGigante([self.background.get_width(), 210], self.marine, LARGURA, self.matou_chefe)
        self.bgScroll   = 0
        self.clock      = pygame.time.Clock()
        self.rodando    = True
        self.inimigos   = []
        self.balas      = []
        self.pontos     = 0
        self.energia    = 100
        self.terminou   = False
        self.exibeFinal = False

        self.delayInimigo      = DELAY_INIMIGO
        self.ultimoTiro        = 0
        self.ultimoInimigo     = 0
        self.inimigosParaMatar = INIMIGOS_PARA_MATAR

    def exibe_texto(self, texto, x = None, y = None):
        text = fonte.render(texto, True, (255, 255, 255))
        textRect = text.get_rect()

        if x == None:
            textRect.centerx = tela.get_rect().centerx
        else:
            textRect.x = x

        if y == None:
            textRect.centery = tela.get_rect().centery
        else:
            textRect.y = y

        tela.blit(text, textRect)

    def exibe_texto_centralizado(self, texto, x, y):
        text = fonte.render(texto, True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.centerx = x
        textRect.y = y
        tela.blit(text, textRect)

    #Metodo responsavel por adicionar novos inimigos no jogo
    def adiciona_inimigos(self):
        if self.terminou:
            return
        if pygame.time.get_ticks() - self.ultimoInimigo > self.delayInimigo and random() < PROB_INIMIGO:
            pos_x   = 700
            direcao = Robo.ESQUERDA

            #Escolhe aleatoriamente se o robo adicionado vem da esquerda ou da direita
            if random() < 0.5:
                pos_x = -30
                direcao = Robo.DIREITA

            self.inimigos.append(Robo([pos_x - self.bgScroll, 210], direcao))
            self.ultimoInimigo = pygame.time.get_ticks()

    #Metodo responsavel por atualizar o estado das entidades (jogador, balas e inimigos)
    def atualiza_entidades(self):
        self.marine.update()
        for bala in self.balas: bala.update()
        for inimigo in self.inimigos: inimigo.update()
        self.chefe.update()

    #Neste metodo estao as regras do jogo
    def logica_jogo(self):
        #1. Verifica se a bala atingiu o inimigo
        for bala in self.balas:
            for inimigo in self.inimigos:
                if not inimigo.morto and bala.rect.colliderect(inimigo.rect):
                    #Atingiu um inimigo !
                    inimigo.morrer()
                    self.pontos += 1
                    self.balas.remove(bala)
                    self.inimigosParaMatar -= 1
                    #A cada 10 inimigos mortos a velocidade com que eles sao adicionados aumenta
                    if self.inimigosParaMatar == 0:
                        self.pontos += 10
                        self.inimigosParaMatar = INIMIGOS_PARA_MATAR
                        self.delayInimigo -= 10
                    break
            if not self.chefe.morto and bala.rect.colliderect(self.chefe.rect):
                self.chefe.energia -= 10
                self.balas.remove(bala)
                if self.chefe.energia == 0:
                    self.terminou = True
                    self.inimigos = []
                    self.chefe.morrer()
                break
        #2. Verifica se o inimigo atingiu o jogador
        if not self.marine.morreu:
            for inimigo in self.inimigos:
                if not inimigo.morto and self.marine.rect.colliderect(inimigo.rect):
                    inimigo.morrer()
                    self.personagem_atingido()
                if inimigo.morto and pygame.time.get_ticks() - inimigo.horaMorte > Robo.DELAY_SUMIR:
                    self.inimigos.remove(inimigo)
        #3. Se uma bala sai da tela, ela eh automaticamente removida
        for bala in self.balas:
            if bala.posicao[0] + self.bgScroll > LARGURA or bala.posicao[0] + self.bgScroll < 0:
                self.balas.remove(bala)
        #4. Verifica se o chefao atingir o personagem
        if not self.marine.morreu and self.marine.rect.colliderect(self.chefe.rect):
            self.personagem_atingido()

    def matou_chefe(self):
        self.exibeFinal = True

    def personagem_atingido(self):
        self.energia -= 25
        if self.energia <= 0:
            self.energia = 0
            self.marine.morrer()
        else:
            self.marine.atingido()

    #Metodo responsavel por fazer a rolagem do cenario de acordo com a posicao do jogador
    def rolagem_cenario(self):
        #Regras para a rolagem do cenario
        if self.bgScroll > -(self.background.get_rect().width - LARGURA) and self.marine.rect.centerx + self.bgScroll > LARGURA * .75:
            self.bgScroll -= 2
        if self.bgScroll < 0 and self.marine.rect.centerx + self.bgScroll < LARGURA * .25:
            self.bgScroll += 2

    #Neste metodo estao as rotinas de deseho do jogo
    def desenha_jogo(self):
        #Desenha o cenario
        tela.blit(self.background, Rect(self.bgScroll, 0, LARGURA, ALTURA))
        #Desenha as balas
        for bala in self.balas:
            balaRect = bala.rect.move(self.bgScroll, 0)
            pygame.draw.rect(tela, (255, 255, 255), balaRect)
        #Desenha os inimigos
        for inimigo in self.inimigos:
            inimigoRect = inimigo.rect.move(self.bgScroll, 0)
            if inimigo.morto:
                #Efeito de fade-out para os robos mortos
                inimigo.image.set_alpha(255.0 * (1.0 - float(pygame.time.get_ticks() - inimigo.horaMorte) / float(Robo.DELAY_SUMIR)))
            tela.blit(inimigo.image, inimigoRect)
        #Desenha o personagem principal
        marineRect = self.marine.rect.move(self.bgScroll, 0)
        tela.blit(self.marine.image, marineRect)
        #Desenha o chefao da fase
        chefeRect = self.chefe.rect.move(self.bgScroll, 0)
        tela.blit(self.chefe.image, chefeRect)
        self.exibe_texto_centralizado('%d%%' % (self.chefe.energia), chefeRect.centerx, chefeRect.y - 20)


        if self.marine.morreu:
            self.exibe_texto('Voce perdeu, pressione qualquer tecla para reiniciar')
        elif self.exibeFinal:
            self.exibe_texto('Voce ganhou! Pressione qualquer tecla para reiniciar')
        self.exibe_texto('Pontos: %d' % (self.pontos), 10, 10)
        self.exibe_texto('Energia: %d%%' % (self.energia), 10, 35)

        #Atualiza o desenho do jogo na placa de video
        pygame.display.flip()

    #Metodo responsavel por processar os estimulos do teclado
    def processa_teclado(self):
        #Obtem a lista de teclas pressionadas
        teclas = pygame.key.get_pressed()

        acao = False

        if teclas[K_ESCAPE]:
            self.rodando = False
        if teclas[K_LEFT]:
            acao = self.marine.andar(Marine.ESQUERDA)
        if teclas[K_RIGHT]:
            acao = self.marine.andar(Marine.DIREITA)
        if teclas[K_UP]:
            acao = self.marine.pular()
        if teclas[K_DOWN]:
            acao = self.marine.abaixar()
        if teclas[K_SPACE]:
            acao = self.marine.atirar(self.balas)
        if not acao and self.marine.is_parado():
            self.marine.animacao = Marine.PARADO

    #Laco do jogo
    def game_loop(self):
        while self.rodando:
            self.clock.tick(120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False
                if (self.marine.morreu or self.exibeFinal) and event.type == pygame.KEYDOWN:
                    self.inicializa()

            self.processa_teclado()
            self.adiciona_inimigos()
            self.atualiza_entidades()
            self.logica_jogo()
            self.rolagem_cenario()
            self.desenha_jogo()

#Inicializacao do jogo
if __name__ == "__main__":
    plataforma = Jogo()
    plataforma.game_loop()