import pygame

# Janela
WIN_WIDTH = 1024
WIN_HEIGHT = 640
WIN_TITLE = 'Survive'
FPS = 60

# Cores
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_GRAY = (170, 170, 170)
C_DARK = (20, 20, 24)
C_BLOOD = (190, 30, 30)
C_YELLOW = (240, 200, 60)
C_PANEL = (0, 0, 0, 160)

# Fontes
FONT_NAME = 'Arial'

# Assets (caminhos relativos ao diretório do jogo)
MENU_BG = './assets/menu/bg.png'

# Menu
MENU_OPTION = ('NOVO JOGO', 'PARTIDAS FINALIZADAS', 'SAIR')
MENU_COMMANDS = (
    ('WASD / Setas', 'Mover'),
    ('Mouse', 'Mirar'),
    ('Espaço / Clique', 'Faca'),
    ('Shift', 'Andar devagar'),
    ('ESC', 'Voltar'),
)

# Teclas
KEY_UP = (pygame.K_w, pygame.K_UP)
KEY_DOWN = (pygame.K_s, pygame.K_DOWN)
KEY_LEFT = (pygame.K_a, pygame.K_LEFT)
KEY_RIGHT = (pygame.K_d, pygame.K_RIGHT)
KEY_ATTACK = (pygame.K_SPACE,)
KEY_SLOW = (pygame.K_LSHIFT, pygame.K_RSHIFT)
KEY_CONFIRM = (pygame.K_RETURN, pygame.K_KP_ENTER)
KEY_BACK = (pygame.K_ESCAPE,)
