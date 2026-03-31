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

        # Tablero 3x3: INF = celda vacía, 1 = girasol (plantas), 0 = zombie
        self.game_array = [[INF, INF, INF],
                           [INF, INF, INF],
                           [INF, INF, INF]]

        # El jugador inicial viene del estado persistente de Game (sobrevive al reinicio)
        self.player = game.starting_player

        # Las 8 combinaciones ganadoras: 3 filas, 3 columnas y 2 diagonales
        self.line_indices_array = [[(0,0), (0,1), (0,2)],
                                   [(1,0), (1,1), (1,2)],
                                   [(2,0), (2,1), (2,2)],
                                   [(0,0), (1,0), (2,0)],
                                   [(0,1), (1,1), (2,1)],
                                   [(0,2), (1,2), (2,2)],
                                   [(0,0), (1,1), (2,2)],
                                   [(0,2), (1,1), (2,0)]]

        self.winner = None      # Almacena 'X' o 'O' cuando hay ganador
        self.game_steps = 0     # Contador de turnos jugados (máximo 9)
        self.font = pg.font.SysFont('Verdana', CELL_SIZE // 4, True)

    def check_winner(self):
        # Suma cada línea: 3 = tres plantas (X gana), 0 = tres zombies (O gana)
        for line_indices in self.line_indices_array:
            sum_line = sum([self.game_array[i][j] for i, j in line_indices])
            if sum_line in {0, 3}:
                self.winner = 'XO'[sum_line == 0]
                # Guardar los extremos de la línea ganadora para dibujarla
                self.winner_line = [vec2(line_indices[0][::-1]) * CELL_SIZE + CELL_CENTER,
                                    vec2(line_indices[2][::-1]) * CELL_SIZE + CELL_CENTER]

    def cpu_move(self):
        # IA simple: elige una celda vacía al azar con randint
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.game_array[r][c] == INF]
        if empty_cells:
            row, col = empty_cells[randint(0, len(empty_cells) - 1)]
            self.game_array[row][col] = self.player
            self.player = 1 - self.player
            self.game_steps += 1
            self.check_winner()

    def handle_click(self):
        # Procesar clic del jugador humano; ignorar si es turno de la CPU
        if self.winner or self.game_steps == 9:
            return
        if self.game.cpu_mode and self.player == 0:
            return
        x, y = pg.mouse.get_pos()
        col, row = int(x // CELL_SIZE), int(y // CELL_SIZE)
        if 0 <= row < 3 and 0 <= col < 3 and self.game_array[row][col] == INF:
            self.game_array[row][col] = self.player
            self.player = 1 - self.player
            self.game_steps += 1
            self.check_winner()

    def run_game_process(self):
        # Si es turno de la CPU (zombie = 0) en modo vs CPU, mover automáticamente
        if self.game.cpu_mode and self.player == 0 and not self.winner and self.game_steps < 9:
            self.cpu_move()

    def draw_objects(self):
        # Recorrer el tablero y dibujar la imagen correspondiente en cada celda ocupada
        for y, row in enumerate(self.game_array):
            for x, obj in enumerate(row):
                if obj != INF:
                    # 1 = girasol (planta), 0 = zombie
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
        font = pg.font.SysFont('Verdana', CELL_SIZE // 10, True)
        label = font.render("It's a Draw! Press Space to Restart", True, 'white', 'black')
        self.game.screen.blit(label, (WIN_SIZE // 2 - label.get_width() // 2, WIN_SIZE // 4))

    def draw_menu(self):
        # Dibujar panel de ayuda semitransparente con todos los controles disponibles
        overlay = pg.Surface((WIN_SIZE, WIN_SIZE), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.game.screen.blit(overlay, (0, 0))

        font_title = pg.font.SysFont('Verdana', CELL_SIZE // 5, True)
        font_item  = pg.font.SysFont('Verdana', CELL_SIZE // 8, False)

        mode_text  = 'vs CPU' if self.game.cpu_mode else 'vs Player 2'
        start_text = 'The Plants' if self.game.starting_player else 'The Zombies'

        entries = [
            ('CONTROLS',                                    font_title, 'yellow'),
            ('',                                            font_item,  'white'),
            ('Left Click  —  Place piece',                  font_item,  'white'),
            (f'C  —  Toggle mode  [{mode_text}]',           font_item,  'white'),
            (f'S  —  Switch starter  [{start_text}]',       font_item,  'white'),
            ('Space  —  Restart game',                      font_item,  'white'),
            ('H  —  Hold to show this menu',                font_item,  'gray'),
        ]

        # Calcular posición Y inicial para centrar verticalmente el bloque de texto
        total_h = sum(f.get_linesize() + 8 for _, f, _ in entries)
        y = WIN_SIZE // 2 - total_h // 2

        for text, font, color in entries:
            label = font.render(text, True, color)
            self.game.screen.blit(label, (WIN_SIZE // 2 - label.get_width() // 2, y))
            y += font.get_linesize() + 8

    def draw(self):
        # Dibujar el fondo del tablero y luego las fichas
        self.game.screen.blit(self.field_image, (0, 0))
        self.draw_objects()
        self.draw_winner()
        if self.game_steps == 9 and not self.winner:
            self.draw_draw()
        # Mostrar el menú de ayuda mientras se mantiene presionada H
        if pg.key.get_pressed()[pg.K_h]:
            self.draw_menu()

    @staticmethod
    def get_scaled_image(path, res):
        # Cargar una imagen y redimensionarla suavemente al tamaño indicado
        img = pg.image.load(path)
        return pg.transform.smoothscale(img, res)

    def print_caption(self):
        # Actualizar el título de la ventana según el estado actual de la partida
        mode = 'vs CPU' if self.game.cpu_mode else 'vs Player 2'
        player_name = 'The Zombies' if not self.player else 'The Plants'
        pg.display.set_caption(f'[{mode}]  {player_name} turn!')
        if self.winner:
            winner_name = 'The Zombies' if self.winner == 'O' else 'The Plants'
            pg.display.set_caption(f'[{mode}]  {winner_name} win! Press Space to Restart')
        elif self.game_steps == 9:
            pg.display.set_caption(f'[{mode}]  Draw! Press Space to Restart')

    def run(self):
        self.print_caption()
        self.draw()
        self.run_game_process()


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([WIN_SIZE] * 2)
        self.clock = pg.time.Clock()
        # Estado persistente entre partidas: sobrevive a los reinicios con Space
        self.cpu_mode = False       # False = 2 jugadores, True = vs CPU (zombies)
        self.starting_player = 1   # 1 = The Plants empieza, 0 = The Zombies empieza
        self.zic_pac_toe = ZicPacToe(self)

    def new_game(self):
        # Reiniciar la partida creando una nueva instancia del juego
        self.zic_pac_toe = ZicPacToe(self)

    def check_events(self):
        # Manejar eventos de ventana, teclado y ratón
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Clic izquierdo: pasar al juego para procesar en el turno correcto
                self.zic_pac_toe.handle_click()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    # Espacio: reiniciar la partida manteniendo el modo y el inicio
                    self.new_game()
                if event.key == pg.K_c:
                    # C: alternar entre 2 jugadores y vs CPU, luego reiniciar
                    self.cpu_mode = not self.cpu_mode
                    self.new_game()
                if event.key == pg.K_s:
                    # S: cambiar quién empieza (planta ↔ zombie), luego reiniciar
                    self.starting_player = 1 - self.starting_player
                    self.new_game()

    def run(self):
        # Bucle principal: actualizar lógica, eventos y pantalla a 60 FPS
        self.zic_pac_toe.run()
        self.check_events()
        pg.display.update()
        self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    while True:
        game.run()
