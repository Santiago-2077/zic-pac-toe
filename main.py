import pygame as pg
import sys
from random import randint

# Tamaño de la ventana y de cada celda del tablero
WIN_SIZE = 900
CELL_SIZE = WIN_SIZE // 3
INF = float('inf')  # Valor que representa una celda vacía
vec2 = pg.math.Vector2
CELL_CENTER = vec2(CELL_SIZE / 2)


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

        # Elegir quién empieza (0 = zombie, 1 = girasol)
        self.player = 1

        # Las 8 combinaciones ganadoras: 3 filas, 3 columnas y 2 diagonales
        self.line_indices_array = [[(0,0), (0,1), (0,2)],
                                   [(1,0), (1,1), (1,2)],
                                   [(2,0), (2,1), (2,2)],
                                   [(0,0), (1,0), (2,0)],
                                   [(0,1), (1,1), (2,1)],
                                   [(0,2), (1,2), (2,2)],
                                   [(0,0), (1,1), (2,2)],
                                   [(0,2), (1,1), (2,0)],
                                   ]

        self.winner = None      # Almacena 'X' o 'O' cuando hay ganador
        self.game_steps = 0     # Contador de turnos jugados (máximo 9)
        self.font = pg.font.SysFont('Verdana', CELL_SIZE // 4, True)
    
    def check_winner(self):
        # Suma cada línea: 3 = tres girasoles (X), 0 = tres zombies (O)
        for line_indices in self.line_indices_array:
            sum_line = sum([self.game_array[i][j] for i,j in line_indices])
            if sum_line in {0,3}:
                self.winner = 'XO'[sum_line == 0]
                # Guardar los extremos de la línea ganadora para dibujarla
                self.winner_line = [vec2(line_indices[0][::-1]) * CELL_SIZE + CELL_CENTER,
                                    vec2(line_indices[2][::-1]) * CELL_SIZE + CELL_CENTER]

    def run_game_process(self):
        # Obtener la celda donde está el cursor del mouse
        current_cell = vec2(pg.mouse.get_pos()) // CELL_SIZE
        col, row = map(int, current_cell)
        left_click = pg.mouse.get_pressed()[0]

        # Si se hace clic izquierdo y la celda está vacía, colocar la ficha
        if left_click and self.game_array[row][col] == INF and not self.winner:
            self.game_array[row][col] = self.player
            self.player = not self.player  # Cambiar turno al otro jugador
            self.game_steps += 1
            self.check_winner()

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

    def draw_winner(self):
        # Trazar la línea ganadora y mostrar el mensaje de victoria centrado
        if self.winner:
            pg.draw.line(self.game.screen, 'red', *self.winner_line, CELL_SIZE // 8)
            winner_name = 'The Zombies' if self.winner == 'O' else 'The Plants'
            label = self.font.render(f'{winner_name} win!', True, 'white', 'black')
            self.game.screen.blit(label, (WIN_SIZE // 2 - label.get_width() // 2, WIN_SIZE // 4))

    def draw_draw(self):
        # Mostrar mensaje de empate centrado cuando el tablero está lleno y no hay ganador
        label = self.font.render("It's a Draw! Press Space to Restart", True, 'white', 'black')
        self.game.screen.blit(label, (WIN_SIZE // 2 - label.get_width() // 2, WIN_SIZE // 4))


    def draw(self):
        # Dibujar el fondo del tablero y luego las fichas
        self.game.screen.blit(self.field_image, (0, 0))
        self.draw_objects()
        self.draw_winner()
        if self.game_steps == 9 and not self.winner:
            self.draw_draw()

    @staticmethod
    def get_scaled_image(path, res):
        # Cargar una imagen y redimensionarla suavemente al tamaño indicado
        img = pg.image.load(path)
        return pg.transform.smoothscale(img, res)
    
    def print_caption(self):
        # Actualizar el título de la ventana según el estado actual de la partida
        player_name = 'The Zombies' if not self.player else 'The Plants'
        pg.display.set_caption(f'{player_name} turn!')
        if self.winner:
            winner_name = 'The Zombies' if self.winner == 'O' else 'The Plants'
            pg.display.set_caption(f'{winner_name} win! Press space to Restart')
        elif self.game_steps == 9:
            pg.display.set_caption(f'Game Over! Press Space to Restart')

    def run(self):
        self.print_caption()
        self.draw()
        self.run_game_process()


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([WIN_SIZE] * 2)
        self.clock = pg.time.Clock()
        self.zic_pac_toe = ZicPacToe(self)

    def new_game(self):
        # Reiniciar la partida creando una nueva instancia del juego
        self.zic_pac_toe = ZicPacToe(self)


    def check_events(self):
        # Manejar el evento de cierre de ventana
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  # Espacio reinicia la partida
                    self.new_game()

    def run(self):
        # Bucle principal: actualizar lógica, eventos y pantalla a 60 FPS
        self.zic_pac_toe.run()
        self.check_events()
        pg.display.update()
        self.clock.tick(60)  # Limitar a 60 FPS


if __name__ == "__main__":
    game = Game()
    while True:
        game.run()
