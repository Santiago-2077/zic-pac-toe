import pygame as pg
import sys
from random import randint

# Tamaño de la ventana y de cada celda del tablero
WIN_SIZE = 900
CELL_SIZE = WIN_SIZE // 3
INF = float('inf')  # Valor que representa una celda vacía
vec2 = pg.math.Vector2


class ZicPacToe:
    def __init__(self, game):
        self.game = game

        # Cargar y escalar las imágenes del tablero y los personajes
        self.field_image = self.get_scaled_image(path="resources/field.png", res=[WIN_SIZE] * 2)
        self.sunflower_image = self.get_scaled_image(path="resources/sunflower.png", res=[CELL_SIZE] * 2)
        self.zombie_image = self.get_scaled_image(path="resources/zombie.png", res=[CELL_SIZE] * 2)

        # Tablero 3x3: INF = celda vacía, 1 = girasol (X), 0 = zombie (O)
        self.game_array = [[INF, INF, INF],
                           [INF, INF, INF],
                           [INF, INF, INF]]

        # Elegir aleatoriamente quién empieza (0 = zombie, 1 = girasol)
        self.player = randint(0, 1)

    def run_game_process(self):
        # Obtener la celda donde está el cursor del mouse
        current_cell = vec2(pg.mouse.get_pos()) // CELL_SIZE
        col, row = map(int, current_cell)
        left_click = pg.mouse.get_pressed()[0]

        # Si se hace clic izquierdo y la celda está vacía, colocar la ficha
        if left_click and self.game_array[row][col] == INF:
            self.game_array[row][col] = self.player
            self.player = not self.player  # Cambiar turno al otro jugador

    def draw_objects(self):
        # Recorrer el tablero y dibujar la imagen correspondiente en cada celda ocupada
        for y, row in enumerate(self.game_array):
            for x, obj in enumerate(row):
                if obj != INF:
                    # 1 = girasol, 0 = zombie
                    self.game.screen.blit(
                        self.sunflower_image if obj else self.zombie_image,
                        vec2(x, y) * CELL_SIZE
                    )

    def draw(self):
        # Dibujar el fondo del tablero y luego las fichas
        self.game.screen.blit(self.field_image, (0, 0))
        self.draw_objects()

    @staticmethod
    def get_scaled_image(path, res):
        # Cargar una imagen y redimensionarla suavemente al tamaño indicado
        img = pg.image.load(path)
        return pg.transform.smoothscale(img, res)

    def run(self):
        self.draw()
        self.run_game_process()


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([WIN_SIZE] * 2)
        self.clock = pg.time.Clock()
        self.zic_pac_toe = ZicPacToe(self)

    def check_events(self):
        # Manejar el evento de cierre de ventana
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

    def run(self):
        self.zic_pac_toe.run()
        self.check_events()
        pg.display.update()
        self.clock.tick(60)  # Limitar a 60 FPS


if __name__ == "__main__":
    game = Game()
    while True:
        game.run()
