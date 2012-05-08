import os
import pygame

IMG_DIR = 'imagens'

def load_image(filename):
    return pygame.image.load(os.path.join(IMG_DIR, filename)).convert()

class Spritesheet:
    def __init__(self, filename):
        self.sheet = load_image(filename)
    def imgat(self, rect, colorkey = None):
        rect = pygame.Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    def imgsat(self, rects, colorkey = None):
        imgs = []
        for rect in rects:
            imgs.append(self.imgat(rect, colorkey))
        return imgs

class Animacao:
    def __init__(self, spritesheet, fps, rects, incremento=1, loop=True, callback=None):
        self.spritesheet  = spritesheet
        self.fps          = fps
        self.rects        = rects
        self.incremento   = incremento
        self.loop         = loop
        self.callback     = callback
        self.frameAtual   = 0
        self.delay        = 1000 / fps
        self.ultimoUpdate = 0
        self.frames       = spritesheet.imgsat(self.rects, -1)
        self.frame        = self.frames[self.frameAtual]
        self.rect         = pygame.Rect(self.rects[self.frameAtual])

    def reset(self):
        self.frameAtual = 0

    def atualiza(self, tempoAtual):
        if tempoAtual - self.ultimoUpdate > self.delay:
            self.ultimoUpdate = tempoAtual

            #Se a animacao eh um loop, seus frames sao circulares
            if self.loop:
                self.frameAtual = (self.frameAtual + 1) % len(self.frames)
            else: #Caso contrario, para no ultimo frame
                self.frameAtual = self.frameAtual + 1
                if self.frameAtual >= len(self.frames):
                    if self.callback != None:
                        self.callback()
                    self.frameAtual = len(self.frames) - 1

            self.frame = self.frames[self.frameAtual]
            self.rect  = pygame.Rect(self.rects[self.frameAtual])

    def inverte(self):
        inverso = Animacao(self.spritesheet, self.fps, self.rects, self.incremento, self.loop, self.callback)
        new_frames = []
        for f in inverso.frames:
            new_frames.append(pygame.transform.flip(f, True, False))
        inverso.frames = new_frames
        return inverso
