import pygame
import random

_BorderSize = 16
_CellSize = 24


class Vars:
    class Config:
        def __init__(self, width, height, update_rate):
            self.width = width
            self.height = height
            self.updateRate = update_rate
            self.win = pygame.display.set_mode([self.width, self.height])
            self.run = True

    class Screen:
        def __init__(self, border_size, cell_size, max_x_cell, max_y_cell):
            self.borderSize = border_size
            self.cellSize = cell_size
            self.maxXCell = max_x_cell
            self.maxYCell = max_y_cell

    class Snake:
        def __init__(self, direction, speed):
            self.segmentsPos = []
            self.defaultDirection = direction
            self.direction = None
            self.speed = speed

    class Apple:
        def __init__(self, pos):
            self.spawned = False
            self.eaten = False
            self.pos = pos


class Canvas:
    @staticmethod
    def x_to_px(x):
        x = x * gameField.cellSize + 2 * gameField.borderSize + 8
        return x

    @staticmethod
    def y_to_px(y):
        y = y * gameField.cellSize + 56
        return y

    @staticmethod
    def draw_window():
        # Tło
        window.win.fill((255, 255, 255))

        # Granice
        pygame.draw.line(window.win, (0, 0, 0), (0, 47), (window.width - 1, 47), width=gameField.borderSize)
        pygame.draw.line(window.win, (0, 0, 0), (window.width - 1, 50), (window.width - 1, window.height - 1),
                         width=gameField.borderSize * 2)
        pygame.draw.line(window.win, (0, 0, 0), (window.width - 1, window.height - 1), (0, window.height - 1),
                         width=gameField.borderSize * 2)
        pygame.draw.line(window.win, (0, 0, 0), (0, window.height - 1), (0, 55), width=gameField.borderSize * 2 - 1)

        # Jabłko
        if apple.spawned:
            pygame.draw.rect(window.win, (0, 255, 0), (Canvas.x_to_px(apple.pos[0]), Canvas.y_to_px(apple.pos[1]),
                                                       gameField.cellSize, gameField.cellSize))

        # Wąż
        for segment in range(len(snake.segmentsPos)):
            # Głowa ma trochę inny kolor niż ciało
            if segment == 0:
                pygame.draw.rect(window.win, (255, 125, 125),
                                 (int(Canvas.x_to_px(snake.segmentsPos[segment][0]) - gameField.cellSize),
                                  int(Canvas.y_to_px(snake.segmentsPos[segment][1])), gameField.cellSize,
                                  gameField.cellSize))
            # Reszta ciała
            else:
                pygame.draw.rect(
                    window.win, (255, 0, 0), (int(Canvas.x_to_px(snake.segmentsPos[segment][0]) - gameField.cellSize),
                                              int(Canvas.y_to_px(snake.segmentsPos[segment][1])), gameField.cellSize,
                                              gameField.cellSize))
        pygame.display.update()


# Odpowiada za przemieszczenie węża
class Move:
    # Sterowanie klawiszami
    @staticmethod
    def key_handler():
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and snake.direction != 'left':
            snake.direction = 'right'
        elif keys[pygame.K_LEFT] and snake.direction != 'right':
            snake.direction = 'left'
        elif keys[pygame.K_UP] and snake.direction != 'down':
            snake.direction = 'up'
        elif keys[pygame.K_DOWN] and snake.direction != 'up':
            snake.direction = 'down'
        elif keys[pygame.K_ESCAPE]:
            exit()

    @staticmethod
    def snake_mover():
        temp = []
        '''if snake.segmentsPos[0][2] == 'left':
            temp = [[round(snake.segmentsPos[0][0] - snake.speed, 3), snake.segmentsPos[0][1], 'left']]
        elif snake.segmentsPos[0][2] == 'right':
            temp = [[round(snake.segmentsPos[0][0] + snake.speed, 3), snake.segmentsPos[0][1], 'right']]
        elif snake.segmentsPos[0][2] == 'up':
            temp = [[snake.segmentsPos[0][0], round(snake.segmentsPos[0][1] - snake.speed, 3), 'up']]
        elif snake.segmentsPos[0][2] == 'down':
            temp = [[snake.segmentsPos[0][0], round(snake.segmentsPos[0][1] + snake.speed, 3), 'down']]'''

        for segment in range(0, len(snake.segmentsPos)):
            if snake.segmentsPos[segment][2] == 'left':
                temp.append([round(snake.segmentsPos[segment][0] - snake.speed, 3), snake.segmentsPos[segment][1], 'left'])
            elif snake.segmentsPos[segment][2] == 'right':
                temp.append([round(snake.segmentsPos[segment][0] + snake.speed, 3), snake.segmentsPos[segment][1], 'right'])
            elif snake.segmentsPos[segment][2] == 'up':
                temp.append([snake.segmentsPos[segment][0], round(snake.segmentsPos[segment][1] - snake.speed, 3), 'up'])
            elif snake.segmentsPos[segment][2] == 'down':
                temp.append([snake.segmentsPos[segment][0], round(snake.segmentsPos[segment][1] + snake.speed, 3), 'down'])

        snake.segmentsPos = temp

# Odpowiada za kolizje ze ścianami, jabłek oraz wzrost węża
class Logic:
    # Kolizje
    @staticmethod
    def crash_checker():
        if snake.segmentsPos[0][0] < 0.0 or snake.segmentsPos[0][0] > float(gameField.maxXCell) or \
                snake.segmentsPos[0][1] < 0.0 or snake.segmentsPos[0][1] > float(gameField.maxYCell - 1):
            window.run = False

    # Logika jabłek
    @staticmethod
    def apple_handler():
        # APPLE_SPAWNED odp. za generację jabłka. Jak go nie ma, to ono generuje się. Jak jest, to nic się nie dzieje
        if not apple.spawned:
            apple.pos = (random.randint(0, gameField.maxXCell - 1), random.randint(0, gameField.maxYCell - 1))
            apple.spawned = True
        # Sprawdza kolizję węża i jabłka. Po co 1? Nie wiem, ale bez jedynki to działa niewłaściwie
        if (int(snake.segmentsPos[0][0] - 1), int(snake.segmentsPos[0][1])) == apple.pos:
            print("Zjadłem :)")
            apple.spawned = False
            # Jak jabłko zjada się, to daje się zgoda na wzrost węża
            snake.segmentsPos.append([snake.segmentsPos[-1][0] - 1, snake.segmentsPos[-1][1], 'left'])



window = Vars.Config(1280, 720, 250)
gameField = Vars.Screen(_BorderSize, _CellSize, (window.width - 2 * _BorderSize) // _CellSize - 1,
                        (window.height - 2 * _BorderSize - 40) // _CellSize)

apple = Vars.Apple((random.randint(0, gameField.maxXCell - 1), random.randint(0, gameField.maxYCell)))
snake = Vars.Snake('left', 0.025)

snake.segmentsPos.append([gameField.maxXCell // 2, gameField.maxYCell // 2, snake.direction])


def main():
    clock = pygame.time.Clock()

    while window.run:
        clock.tick(window.updateRate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window.run = False

        Move.key_handler()
        if snake.segmentsPos[0][0] % 1 == 0.0 and snake.segmentsPos[0][1] % 1 == 0.0:
            snake.segmentsPos[0][2] = snake.direction
        Move.snake_mover()
        Logic.apple_handler()
        Logic.crash_checker()

        Canvas.draw_window()
    pygame.quit()


if __name__ == '__main__':
    main()
