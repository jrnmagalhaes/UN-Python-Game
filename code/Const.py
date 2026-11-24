import pygame

WIN_WIDTH = 1024
WIN_HEIGHT = 640
WIN_TITLE = 'Survive'
FPS = 60

C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_GRAY = (170, 170, 170)
C_DARK = (20, 20, 24)
C_BLOOD = (190, 30, 30)
C_YELLOW = (240, 200, 60)
C_PANEL = (0, 0, 0, 160)

FONT_NAME = 'Arial'

MENU_BG = './assets/menu/bg.png'

MENU_OPTION = ('NOVO JOGO', 'PARTIDAS FINALIZADAS', 'SAIR')
MENU_COMMANDS = (
    ('WASD / Setas', 'Mover'),
    ('Mouse', 'Mirar'),
    ('Espaço / Clique', 'Faca'),
    ('Shift', 'Andar devagar'),
    ('ESC', 'Voltar'),
)

KEY_UP = (pygame.K_w, pygame.K_UP)
KEY_DOWN = (pygame.K_s, pygame.K_DOWN)
KEY_LEFT = (pygame.K_a, pygame.K_LEFT)
KEY_RIGHT = (pygame.K_d, pygame.K_RIGHT)
KEY_ATTACK = (pygame.K_SPACE,)
KEY_SLOW = (pygame.K_LSHIFT, pygame.K_RSHIFT)
KEY_CONFIRM = (pygame.K_RETURN, pygame.K_KP_ENTER)
KEY_BACK = (pygame.K_ESCAPE,)
KEY_DEBUG_WIN = (pygame.K_n,)

TILE_SIZE = 40
MAP_COLS = 25
MAP_ROWS = 15
HUD_HEIGHT = 40
MAP_OFFSET = ((WIN_WIDTH - MAP_COLS * TILE_SIZE) // 2, HUD_HEIGHT)
TILE_WALL = '#'
TILE_FLOOR = '.'
TILE_PLAYER = 'P'
TILE_TABLE = 'T'
TILE_PLANT = 'v'
TILE_SOLID = (TILE_WALL, TILE_TABLE, TILE_PLANT)
TILE_DIR = './assets/tilesystem/Tiles/PNG_version_2'
OBJ_DIR = './assets/tilesystem/Objects/PNG'
IMG_WALL = TILE_DIR + '/Roofs/Wall3_5.png'
IMG_TABLE = OBJ_DIR + '/objects_house_0052_Layer-53.png'
IMG_PLANT = OBJ_DIR + '/objects_house_0054_Layer-55.png'
C_WALL_EDGE = (12, 12, 14)
C_SHADOW = (0, 0, 0, 90)

LEVEL_COUNT = 3
LEVEL_WIN = 'win'
LEVEL_QUIT = 'quit'
C_HUD_BG = (14, 14, 18)
C_MARK_PLAYER = (60, 200, 90)
C_MARK_ENEMY = (210, 40, 40)
C_MARK_ROUTE = (240, 200, 60)
