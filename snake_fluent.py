# Logika i poruszanie: Romek Szlachtun 2C
import pygame
import random

_BorderSize = 16
_CellSize = 24


# Wyodrębniłem wszystkie definicje zmiennych do klasy Vars
class Vars:
    class Window:
        def __init__(self, width, height, update_rate):
            self.width = width
            self.height = height
            self.updateRate = update_rate
            self.win = pygame.display.set_mode([self.width, self.height])
            self.run = True

    class GameField:
        def __init__(self, border_size, cell_size, max_x_cell, max_y_cell):
            self.borderSize = border_size
            self.cellSize = cell_size
            self.maxXCell = max_x_cell
            self.maxYCell = max_y_cell

    class Snake:
        def __init__(self, direction, speed):
            self.headPos = []
            self.segmentsPos = []
            self.lastPos = []
            self.defaultDirection = direction
            self.chosenDirection = direction
            self.speed = speed

    class Apple:
        def __init__(self, pos):
            self.spawned = False
            self.eaten = False
            self.pos = pos


class Canvas:
    # pygame wyświetla elementy wyłącznie w pikselach
    # funkcje przekształcają siatkę wsp. w pikseli
    @staticmethod
    def x_to_px(x):
        x = x * gameField.cellSize + gameField.borderSize
        return x

    @staticmethod
    def y_to_px(y):
        y = y * gameField.cellSize + 56
        return y

    # Wyświetla interfejs gry
    @staticmethod
    def draw_window():
        # Tło
        window.win.fill((255, 255, 255))

        # Granice
        pygame.draw.line(window.win, (0, 0, 0), (0, 47), (window.width - 1, 47),
                         width=gameField.borderSize)
        pygame.draw.line(window.win, (0, 0, 0), (window.width - 1, 50), (window.width - 1, window.height - 1),
                         width=gameField.borderSize * 2)
        pygame.draw.line(window.win, (0, 0, 0), (window.width - 1, window.height - 1), (0, window.height - 1),
                         width=gameField.borderSize * 2)
        pygame.draw.line(window.win, (0, 0, 0), (0, window.height - 1), (0, 55),
                         width=gameField.borderSize * 2 - 1)

        # Jabłko
        if apple.spawned:
            pygame.draw.rect(window.win, (0, 255, 0), (Canvas.x_to_px(apple.pos[0]), Canvas.y_to_px(apple.pos[1]),
                                                       gameField.cellSize, gameField.cellSize))
        # Głowa
        pygame.draw.rect(window.win, (153, 204, 255),
                         (Canvas.x_to_px(snake.headPos[0]), Canvas.y_to_px(snake.headPos[1]),
                          gameField.cellSize, gameField.cellSize))

        # Reszta ciała z ogonem
        for segment in range(len(snake.segmentsPos)):
            pygame.draw.rect(window.win, (255, 0, 0), (int(Canvas.x_to_px(snake.segmentsPos[segment][0])),
                                                       int(Canvas.y_to_px(snake.segmentsPos[segment][1])),
                                                       gameField.cellSize, gameField.cellSize))

        pygame.display.update()


class Move:
    # Sterowanie klawiszami
    @staticmethod
    def key_handler():
        # Tutaj zapisuje się wybrany kierunek węża, dokąd wąż skręci dopiero jak osiągnie całkowite wspórzędne (wsp.)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and snake.defaultDirection != 'left':
            snake.chosenDirection = 'right'
        elif keys[pygame.K_LEFT] and snake.defaultDirection != 'right':
            snake.chosenDirection = 'left'
        elif keys[pygame.K_UP] and snake.defaultDirection != 'down':
            snake.chosenDirection = 'up'
        elif keys[pygame.K_DOWN] and snake.defaultDirection != 'up':
            snake.chosenDirection = 'down'
        elif keys[pygame.K_ESCAPE]:
            exit()

    # Algorytm płynnego poruszania głowy po siatce wsp.
    @staticmethod
    def head_move():
        if snake.defaultDirection == 'left':
            snake.headPos = [round(snake.headPos[0] - snake.speed, 3), snake.headPos[1], 'left']
        elif snake.defaultDirection == 'right':
            snake.headPos = [round(snake.headPos[0] + snake.speed, 3), snake.headPos[1], 'right']
        elif snake.defaultDirection == 'up':
            snake.headPos = [snake.headPos[0], round(snake.headPos[1] - snake.speed, 3), 'up']
        elif snake.defaultDirection == 'down':
            snake.headPos = [snake.headPos[0], round(snake.headPos[1] + snake.speed, 3), 'down']

    # Po osiągnięciu głową całkowitych wsp. należy przesunąć nieruchome ciało (poza ogonem) w kierunku głowy
    @staticmethod
    def segments_update():
        newSegmentsPos = [snake.headPos]
        for segment in snake.segmentsPos[:-1]:
            newSegmentsPos.append(segment)
        snake.segmentsPos = newSegmentsPos

    # Ogonem występuje ostatnia część ciała, która płynnie przesuwa się do przedostatniej (nieruchomej) części ciała
    # Gdy ogon osiąga tą część ciała, ogon usuwa się, i ówczesna przedostatnia część ciała staje się ruchoma i pełni
    # funkcję ogona
    @staticmethod
    def tail_update():
        # Usprawnia zawroty ogona węża
        if snake.segmentsPos[-2][2] != snake.segmentsPos[-1][2]:
            snake.segmentsPos[-1][2] = snake.segmentsPos[-2][2]

        if snake.segmentsPos[-1][2] == 'left':
            snake.segmentsPos[-1][0] = round(snake.segmentsPos[-1][0] - snake.speed, 3)
        elif snake.segmentsPos[-1][2] == 'right':
            snake.segmentsPos[-1][0] = round(snake.segmentsPos[-1][0] + snake.speed, 3)
        elif snake.segmentsPos[-1][2] == 'up':
            snake.segmentsPos[-1][1] = round(snake.segmentsPos[-1][1] - snake.speed, 3)
        elif snake.segmentsPos[-1][2] == 'down':
            snake.segmentsPos[-1][1] = round(snake.segmentsPos[-1][1] + snake.speed, 3)


class Logic:
    # Kolizje
    @staticmethod
    def crash_checker():
        # Jak węż przekracza granicy ściany, to gra się zamyka
        if snake.segmentsPos[0][0] < 0.0 or snake.segmentsPos[0][0] > float(gameField.maxXCell) or \
                snake.segmentsPos[0][1] < 0.0 or snake.segmentsPos[0][1] > float(gameField.maxYCell - 1):
            window.run = False

    # Logika jabłek
    @staticmethod
    def apple_handler():
        # apple.spawned odp. za generację jabłka. Jak go nie ma, to ono generuje się. Jak jest, to nic się nie dzieje
        if not apple.spawned:
            apple.pos = (random.randint(0, gameField.maxXCell - 1), random.randint(0, gameField.maxYCell - 1))
            apple.spawned = True
        # Sprawdza kolizję węża i jabłka. Działa tylko gdy wąż przekracza granice jabłka
        if (apple.pos[1] < snake.headPos[1] + 1 < apple.pos[1] + 1 and apple.pos[0] == snake.headPos[0]) or \
                (apple.pos[0] < snake.headPos[0] < apple.pos[0] + 1 and apple.pos[1] == snake.headPos[1]) or \
                (apple.pos[1] < snake.headPos[1] < apple.pos[1] + 1 and apple.pos[0] == snake.headPos[0]) or \
                (apple.pos[0] < snake.headPos[0] + 1 < apple.pos[0] + 1 and apple.pos[1] == snake.headPos[1]):
            print("Zjadłem :)")
            # Prawdziwy apple.eaten daje zgodę na wzrost węża
            apple.eaten = True
            # Daje zgodę na ponowną generację jabłka
            apple.spawned = False

    @staticmethod
    def snake_grow():
        # Aby zwiększyć wzrost węża, nowy element dodaje się do przedostatniej nieruchomej części ciała
        # Aby dodać nowy element z właściwej strony, trzeba odczytać kierunek części ciała, który jest niezmienny i
        # zadany przy jego generacji
        if snake.segmentsPos[-2][2] == 'left':
            temp = snake.segmentsPos[:-1]
            temp.append([snake.segmentsPos[-2][0] + 1, snake.segmentsPos[-2][1], snake.segmentsPos[-2][2]])
            temp.append([snake.segmentsPos[-1]])
            snake.segmentsPos = temp
        elif snake.segmentsPos[-2][2] == 'right':
            temp = snake.segmentsPos[:-1]
            temp.append([snake.segmentsPos[-2][0] - 1, snake.segmentsPos[-2][1], snake.segmentsPos[-2][2]])
            temp.append([snake.segmentsPos[-1]])
            snake.segmentsPos = temp
        elif snake.segmentsPos[-2][2] == 'up':
            temp = snake.segmentsPos[:-1]
            temp.append([snake.segmentsPos[-2][0], snake.segmentsPos[-2][1] + 1, snake.segmentsPos[-2][2]])
            temp.append([snake.segmentsPos[-1]])
            snake.segmentsPos = temp
        elif snake.segmentsPos[-2][2] == 'down':
            temp = snake.segmentsPos[:-1]
            temp.append([snake.segmentsPos[-2][0], snake.segmentsPos[-2][1] - 1, snake.segmentsPos[-2][2]])
            temp.append([snake.segmentsPos[-1]])
            snake.segmentsPos = temp


# Utworzenie obietków (grupy zmiennych) z klasów w Vars
# PRZYKLAD: Aby skorzystać ze zmiennej segmentsPos obiektu snake (którego z kolei utworzono od klasy Vars.Snake) należy
# napisać snake.segmentsPos = 'cokolwiek'
window = Vars.Window(width=1280, height=720, update_rate=250)
gameField = Vars.GameField(border_size=_BorderSize, cell_size=_CellSize,
                           max_x_cell=(window.width - 2 * _BorderSize) // _CellSize - 1,
                           max_y_cell=(window.height - 2 * _BorderSize - 40) // _CellSize)

snake = Vars.Snake(direction='left', speed=0.025)
apple = Vars.Apple(pos=(random.randint(0, gameField.maxXCell - 1), random.randint(0, gameField.maxYCell)))
# Na dobry początek utwarza się kilka członów węża i jego początkowy kierunek
snake.headPos = [gameField.maxXCell // 2, gameField.maxYCell // 2, snake.defaultDirection]
snake.segmentsPos.append([gameField.maxXCell // 2, gameField.maxYCell // 2, snake.defaultDirection])
snake.segmentsPos.append([gameField.maxXCell // 2, gameField.maxYCell // 2, snake.defaultDirection])


def main():
    clock = pygame.time.Clock()

    while window.run:
        clock.tick(window.updateRate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window.run = False
        # Aby skorzystać z funkcji należy napisać grupę do której funkcja należy (Canvas, Move, Logic), kropkę i nazwę
        # samej fukcji

        Move.key_handler()
        # Wąż skręca i wydłuża się tylko kiedy znajduje się na granicy siatki współrzędnej
        if snake.headPos[0] % 1 == 0.0 and snake.headPos[1] % 1 == 0.0:
            snake.defaultDirection = snake.chosenDirection
            if apple.eaten:
                apple.eaten = False
                Logic.snake_grow()
            Move.segments_update()

        Move.tail_update()
        Move.head_move()
        Logic.apple_handler()
        Logic.crash_checker()

        Canvas.draw_window()

    pygame.quit()


if __name__ == '__main__':
    main()
