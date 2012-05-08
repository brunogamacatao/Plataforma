import math
import pygame
import pygame.sprite
from myutils import Spritesheet, Animacao

class Marine(pygame.sprite.Sprite):
    #Carregamento do spritesheet
    spritesheet = Spritesheet('marine.gif')

    DELAY_TIRO = 200 #Intervalo de tempo (msecs) entre os tiros

    #Definicao das direcoes
    ESQUERDA = 0
    DIREITA  = 1

    #Definicao das animacoes
    PARADO   = 'parado'
    CORRER   = 'correr'
    PULAR    = 'pular'
    ATIRAR   = 'atirar'
    MORRER   = 'morrer'
    ATINGIDO = 'atingido'
    VIRAR    = 'virar'
    ABAIXAR  = 'abaixar'

    def __init__(self, posicaoInicial, fps = 15):
        pygame.sprite.Sprite.__init__(self)
        self.posicao    = posicaoInicial
        self.pulando    = False
        self.bloqueado  = False
        self.ultimoTiro = 0

        self.animacoes = {
            'parado' : [
                Animacao(Marine.spritesheet, fps, [(142, 44, 28, 37), (175, 43, 25, 38), (205, 43, 25, 37), (234, 42, 23, 39), (261, 43, 24, 38), (234, 42, 23, 39), (205, 43, 25, 37)], -1),
            ],
            'correr' : [
                Animacao(Marine.spritesheet, fps, [(88, 2, 22, 35), (116, 2, 25, 35), (144, 1, 29, 36), (175, 1, 24, 36), (203, 2, 21, 35), (228, 2, 27, 35), (257, 1, 30, 36), (291, 1, 24, 36), (318, 2, 21, 35)], -1),
            ],
            'pular' : [
                Animacao(Marine.spritesheet, 1, [(297, 193, 42, 39), (252, 193, 42, 41), (207, 193, 41, 37), (162, 193, 42, 31), (207, 193, 41, 37), (252, 193, 42, 41)]),
            ],
            'atirar' : [
                Animacao(Marine.spritesheet, fps, [(284, 730, 55, 34), (229, 730, 51, 34), (168, 730, 57, 34)]),
            ],
            'morrer' : [
                Animacao(Marine.spritesheet, fps, [(312, 1469, 27, 38), (283, 1468, 26, 39), (256, 1467, 24, 40), (230, 1469, 22, 38), (202, 1471, 25, 36), (167, 1474, 32, 33), (129, 1481, 35, 26), (93, 1494, 33, 13), (57, 1494, 33, 13)], 1, False),
            ],
            'atingido' : [
                Animacao(Marine.spritesheet, fps, [(312, 1469, 27, 38), (283, 1468, 26, 39), (256, 1467, 24, 40), (230, 1469, 22, 38), (202, 1471, 25, 36), (167, 1474, 32, 33), (129, 1481, 35, 26), (93, 1494, 33, 13), (57, 1494, 33, 13)], 1, False, self.atingido_callback),
            ],
            'virar' : [
                Animacao(Marine.spritesheet, 30, [(314, 117, 25, 40), (281, 119, 28, 35), (247, 119, 30, 35), (210, 120, 32, 34), (173, 121, 34, 33), (438, 120, 32, 34), (403, 119, 30, 35), (371, 119, 28, 35), (341, 117, 25, 37)], 1, False, self.virar_callback),
            ],
            'abaixar' : [
                Animacao(Marine.spritesheet, fps, [(312, 83, 27, 32), (278, 88, 31, 27), (245, 88, 31, 27), (211, 88, 31, 27), (176, 89, 31, 26)], 1, False),
            ],
        }

        #Criando automaticamente os sprites para a DIREITA
        for animacao in self.animacoes.keys():
            self.animacoes[animacao].append(self.animacoes[animacao][Marine.ESQUERDA].inverte())

        self.velocidades = {
            'parado'  : (0, 0),
            'correr'  : (-2, 2),
            'pular'   : (0, 0),
            'atirar'  : (0, 0),
            'morrer'  : (0, 0),
            'atingido': (0, 0),
            'virar'   : (0, 0),
            'abaixar' : (0, 0),
        }

        self.direcao  = Marine.DIREITA
        self.animacao = Marine.PARADO
        self.prevAnim = None
        self.pularAng = 0
        self.morreu   = False

    #Este metodo sera chamado sempre que o personagem for atingido
    def atingido(self):
        if self.bloqueado:
            return False
        self.bloqueado = True
        self.animacao  = Marine.ATINGIDO
        self.prevAnim  = self.animacao
        self.reset_animacao()
        return True

    #Este metodo sera chamado sempre que a animacao 'atingido' terminar
    def atingido_callback(self):
        self.bloqueado = False
        self.animacao  = self.prevAnim

    def virar(self):
        if self.bloqueado:
            return False
        self.bloqueado = True
        self.animacao  = Marine.VIRAR
        self.reset_animacao()
        return True

    def virar_callback(self):
        self.bloqueado = False
        self.direcao   = (self.direcao + 1) % 2 #Troca a direcao do movimento

    def andar(self, direcao):
        if self.bloqueado:
            return False
        if self.direcao != direcao:
            self.virar()
            return True
        self.animacao = Marine.CORRER
        return True

    def abaixar(self):
        if self.bloqueado:
            return False
        self.animacao = Marine.ABAIXAR
        self.reset_animacao()
        return True

    def atirar(self, balas):
        if self.bloqueado:
            return False
        self.animacao = Marine.ATIRAR
        if pygame.time.get_ticks() - self.ultimoTiro > Marine.DELAY_TIRO:
            balas.append(Bala(self.posicao, self.direcao))
            self.ultimoTiro = pygame.time.get_ticks()
        return True

    def morrer(self):
        self.morreu    = True
        self.bloqueado = True
        self.animacao  = Marine.MORRER

    def pular(self):
        if self.pulando or self.bloqueado:
            #Se voce quiser implementar um pulo duplo, o lugar eh aqui
            return False
        self.bloqueado = True
        self.pulando   = True
        self.prevAnim  = self.animacao
        self.animacao  = Marine.PULAR
        self.pularAng  = 0
        self.reset_animacao()
        return True

    #Este metodo determina se o personagem esta parado ou nao
    def is_parado(self):
        return not self.bloqueado and not self.pulando and not self.morreu

    #Este metodo garante que a animacao iniciara no primeiro quadro
    def reset_animacao(self):
        self.animacoes[self.animacao][self.direcao].reset()

    def update(self):
        animacao = self.animacoes[self.animacao][self.direcao]
        animacao.atualiza(pygame.time.get_ticks())
        self.image = animacao.frame
        self.rect  = animacao.rect
        self.rect.centerx = self.posicao[0]
        self.rect.bottom  = self.posicao[1]

        if self.pulando:
            self.posicao[0] += self.velocidades[self.prevAnim][self.direcao]
            self.pularAng += 0.25
            if self.pularAng > 2 * math.pi:
                self.pulando   = False
                self.bloqueado = False
                self.animacao  = self.prevAnim
            #O movimento do pulo eh definido por uma funcao seno
            self.posicao[1] -= 5 * math.sin(self.pularAng)
        else:
            self.posicao[0]  += self.velocidades[self.animacao][self.direcao]

class Robo(pygame.sprite.Sprite):
    #Carregamento do spritesheet
    spritesheet = Spritesheet('shootrobot.gif')

    #Definicao das direcoes
    ESQUERDA = 0
    DIREITA  = 1

    #Definicao das animacoes
    ANDAR  = 'andar'
    MORRER = 'morrer'

    DELAY_SUMIR = 2000 #Intervalo de tempo (msecs) entre o robo morrer e sumir da tela
    
    def __init__(self, posicaoInicial, direcao = ESQUERDA, fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self.posicao = posicaoInicial

        self.animacoes = {
            'andar': [
                Animacao(Robo.spritesheet, fps, [(238, 4, 62, 61), (174, 3, 61, 62), (111, 2, 60, 63), (49, 2, 58, 63), (111, 2, 60, 63), (174, 3, 61, 62)]),
            ],
            'morrer': [
                Animacao(Robo.spritesheet, fps, [(222, 1788, 78, 46),]),
            ]
        }

        self.velocidades = {
            'andar': (-2, 3),
            'morrer': (0, 0),
        }


        #Criando automaticamente os sprites para a DIREITA
        for animacao in self.animacoes.keys():
            self.animacoes[animacao].append(self.animacoes[animacao][Robo.ESQUERDA].inverte())

        self.animacao  = Robo.ANDAR
        self.direcao   = direcao
        self.morto     = False
        self.horaMorte = 0

    def morrer(self):
        self.animacao = Robo.MORRER
        self.morto = True
        self.horaMorte = pygame.time.get_ticks()

    def update(self):
        animacao = self.animacoes[self.animacao][self.direcao]
        animacao.atualiza(pygame.time.get_ticks())
        self.image = animacao.frame
        self.rect  = animacao.rect
        self.rect.centerx = self.posicao[0]
        self.rect.bottom  = self.posicao[1]
        self.posicao[0]  += self.velocidades[self.animacao][self.direcao]

class CaranguejoGigante(pygame.sprite.Sprite):
    #Carregamento do spritesheet
    spritesheet = Spritesheet('giantorgancecrab.gif')

    #Definicao das direcoes
    ESQUERDA = 0
    DIREITA  = 1

    #Definicao das animacoes
    PARADO = 'parado'
    ANDAR  = 'andar'
    ATACAR = 'atacar'
    MORRER = 'morrer'

    DELAY_SUMIR = 2000 #Intervalo de tempo (msecs) entre o robo morrer e sumir da tela

    def __init__(self, posicaoInicial, marine, larguraTela, matou_callback, direcao = ESQUERDA, fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self.posicao = posicaoInicial
        self.marine  = marine
        self.larguraTela = larguraTela

        self.animacoes = {
            'parado': [
                Animacao(CaranguejoGigante.spritesheet, fps, [(23, 0, 103, 81), (130, 1, 101, 80), (234, 2, 98, 79), (335, 2, 101, 79), (439, 2, 102, 79), (544, 2, 105, 79), (654, 1, 102, 80)]),
            ],
            'andar': [
                Animacao(CaranguejoGigante.spritesheet, fps, [(9, 171, 105, 79), (118, 171, 104, 79), (225, 170, 107, 80), (335, 170, 106, 80), (444, 169, 106, 81), (554, 169, 107, 81), (664, 169, 107, 81), (130, 254, 105, 80), (238, 254, 101, 80), (342, 255, 98, 79), (443, 255, 101, 79), (547, 255, 102, 79)]),
            ],
            'atacar': [
                Animacao(CaranguejoGigante.spritesheet, fps, [(32, 998, 98, 81), (133, 999, 88, 80), (224, 993, 79, 86), (306, 991, 76, 88), (385, 988, 86, 91), (474, 991, 76, 88), (553, 999, 90, 80), (646, 1000, 100, 79), (44, 1083, 126, 81), (173, 1083, 128, 82), (304, 1083, 117, 79), (424, 1083, 108, 79), (535, 1082, 94, 80), (631, 1082, 106, 80), (196, 1168, 132, 83), (331, 1168, 132, 84), (467, 1168, 117, 81)]),
            ],
            'morrer': [
                Animacao(CaranguejoGigante.spritesheet, fps, [(29, 2002, 93, 82), (125, 2001, 95, 83), (223, 1995, 99, 89), (325, 1994, 99, 90), (428, 1994, 103, 90), (535, 2002, 106, 82), (644, 2007, 106, 77), (35, 2086, 109, 73), (147, 2093, 113, 66), (263, 2100, 121, 58), (387, 2104, 117, 55), (507, 2106, 116, 54), (627, 2108, 117, 50), (30, 2162, 117, 50), (150, 2163, 118, 49), (271, 2165, 118, 45), (392, 2167, 118, 43), (513, 2170, 117, 40), (633, 2173, 116, 37), (20, 2215, 115, 34), (138, 2219, 110, 29), (251, 2223, 103, 25), (357, 2228, 102, 20), (462, 2232, 97, 16)], 1, False, matou_callback),
            ],
        }

        self.velocidades = {
            'parado': (0, 0),
            'andar' : (-1, 1),
            'atacar': (0, 0),
            'morrer': (0, 0),
        }


        #Criando automaticamente os sprites para a DIREITA
        for animacao in self.animacoes.keys():
            self.animacoes[animacao].append(self.animacoes[animacao][CaranguejoGigante.ESQUERDA].inverte())

        self.animacao  = CaranguejoGigante.PARADO
        self.direcao   = direcao
        self.morto     = False
        self.energia   = 100
        self.horaMorte = 0

    def morrer(self):
        self.animacao = CaranguejoGigante.MORRER
        self.morto = True
        self.horaMorte = pygame.time.get_ticks()

    #Implementacao da inteligencia artificial do caranguejo
    def processa_ia(self):
        if self.posicao[0] < self.marine.posicao[0]: #se esta a esqueda do marine
            self.direcao = CaranguejoGigante.DIREITA
        else: #caso contrario, esta a direita do marine
            self.direcao = CaranguejoGigante.ESQUERDA
        distancia = math.fabs(self.posicao[0] - self.marine.posicao[0])
        
        if distancia > self.larguraTela:
            self.animacao = CaranguejoGigante.PARADO
        elif distancia > self.rect.width:
            self.animacao = CaranguejoGigante.ANDAR
        else:
            self.animacao = CaranguejoGigante.ATACAR

    def update(self):
        animacao = self.animacoes[self.animacao][self.direcao]
        animacao.atualiza(pygame.time.get_ticks())
        self.image = animacao.frame
        self.rect  = animacao.rect
        self.rect.centerx = self.posicao[0]
        self.rect.bottom  = self.posicao[1]
        self.posicao[0]  += self.velocidades[self.animacao][self.direcao]
        
        if animacao.frameAtual == 0:
            self.processa_ia()

class Bala(pygame.sprite.Sprite):
    #Definicao das direcoes
    ESQUERDA = 0
    DIREITA  = 1

    #Velocidade padrao da bala
    VELOCIDADE = (-5, 5)
    
    def __init__(self, posicao, direcao):
        pygame.sprite.Sprite.__init__(self)
        self.posicao = [posicao[0], posicao[1] - 18]
        self.direcao = direcao
        self.rect = pygame.Rect(self.posicao, (2, 2))

    def update(self):
        self.rect.centerx = self.posicao[0]
        self.rect.bottom  = self.posicao[1]
        self.posicao[0]  += Bala.VELOCIDADE[self.direcao]
