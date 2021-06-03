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
    @staticmethod
    def x_to_px(x):
        x = x * gameField.cellSize + gameField.borderSize
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

        pygame.draw.rect(window.win, (255, 125, 125),
                         (Canvas.x_to_px(snake.headPos[0]), Canvas.y_to_px(snake.headPos[1]),
                          gameField.cellSize, gameField.cellSize))

        for segment in range(len(snake.segmentsPos)):
            if segment == 0:
                pygame.draw.rect(window.win, (255, 125, 0), (int(Canvas.x_to_px(snake.segmentsPos[segment][0])),
                                                             int(Canvas.y_to_px(snake.segmentsPos[segment][1])),
                                                             gameField.cellSize, gameField.cellSize))
            else:
                pygame.draw.rect(window.win, (255, 0, 0), (int(Canvas.x_to_px(snake.segmentsPos[segment][0])),
                                                           int(Canvas.y_to_px(snake.segmentsPos[segment][1])),
                                                           gameField.cellSize, gameField.cellSize))

        pygame.display.update()


class Move:
    # Sterowanie klawiszami
    @staticmethod
    def key_handler():
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

        if snake.defaultDirection == 'left':
            snake.headPos = [round(snake.headPos[0] - snake.speed, 3), snake.headPos[1], 'left']
        elif snake.defaultDirection == 'right':
            snake.headPos = [round(snake.headPos[0] + snake.speed, 3), snake.headPos[1], 'right']
        elif snake.defaultDirection == 'up':
            snake.headPos = [snake.headPos[0], round(snake.headPos[1] - snake.speed, 3), 'up']
        elif snake.defaultDirection == 'down':
            snake.headPos = [snake.headPos[0], round(snake.headPos[1] + snake.speed, 3), 'down']


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
        if (apple.pos[1] < snake.segmentsPos[0][1] + 1 < apple.pos[1] + 1 and apple.pos[0] == snake.segmentsPos[0][
            0]) or \
                (apple.pos[0] < snake.segmentsPos[0][0] < apple.pos[0] + 1 and apple.pos[1] == snake.segmentsPos[0][
                    1]) or \
                (apple.pos[1] < snake.segmentsPos[0][1] < apple.pos[1] + 1 and apple.pos[0] == snake.segmentsPos[0][
                    0]) or \
                (apple.pos[0] < snake.segmentsPos[0][0] + 1 < apple.pos[0] + 1 and apple.pos[1] == snake.segmentsPos[0][
                    1]):
            print("Zjadłem :)")
            apple.spawned = False
            # Jak jabłko zjada się, to daje się zgoda na wzrost węża
            if snake.segmentsPos[0][2] == 'left':
                snake.segmentsPos.append([snake.segmentsPos[0][0] + 1, snake.segmentsPos[0][1], 'left'])
            elif snake.segmentsPos[0][2] == 'right':
                snake.segmentsPos.append([snake.segmentsPos[0][0] - 1, snake.segmentsPos[0][1], 'right'])
            elif snake.segmentsPos[0][2] == 'up':
                snake.segmentsPos.append([snake.segmentsPos[0][0], snake.segmentsPos[0][1] + 1, 'up'])
            elif snake.segmentsPos[0][2] == 'down':
                snake.segmentsPos.append([snake.segmentsPos[0][0], snake.segmentsPos[0][1] - 1, 'down'])


window = Vars.Config(1280, 720, 250)
gameField = Vars.Screen(_BorderSize, _CellSize, (window.width - 2 * _BorderSize) // _CellSize - 1,
                        (window.height - 2 * _BorderSize - 40) // _CellSize)

apple = Vars.Apple((random.randint(0, gameField.maxXCell - 1), random.randint(0, gameField.maxYCell)))
snake = Vars.Snake('left', 0.025)

snake.headPos = [gameField.maxXCell // 2 - 2, gameField.maxYCell // 2, 'left']
snake.segmentsPos.append([gameField.maxXCell // 2, gameField.maxYCell // 2, 'left'])
snake.segmentsPos.append([gameField.maxXCell // 2 - 1, gameField.maxYCell // 2, 'left'])


# snake.lastPos = [gameField.cellSize, gameField.cellSize]


def main():
    clock = pygame.time.Clock()

    while window.run:
        clock.tick(window.updateRate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window.run = False

        Move.key_handler()
        if snake.headPos[0] % 1 == 0.0 and snake.headPos[1] % 1 == 0.0:
            snake.defaultDirection = snake.chosenDirection
            snake.segmentsPos.append(snake.headPos)
            snake.segmentsPos.remove(snake.segmentsPos[0])

        if snake.segmentsPos[0][2] == 'left':
            snake.segmentsPos[0] = [round(snake.segmentsPos[0][0] - snake.speed, 3), snake.segmentsPos[0][1], 'left']
        elif snake.segmentsPos[0][2] == 'down':
            snake.segmentsPos[0] = [snake.segmentsPos[0][0], round(snake.segmentsPos[0][1] + snake.speed, 3), 'down']
        elif snake.segmentsPos[0][2] == 'right':
            snake.segmentsPos[0] = [round(snake.segmentsPos[0][0] + snake.speed, 3), snake.segmentsPos[0][1], 'right']
        elif snake.segmentsPos[0][2] == 'up':
            snake.segmentsPos[0] = [snake.segmentsPos[0][0], round(snake.segmentsPos[0][1] - snake.speed, 3), 'up']
        print(snake.segmentsPos)
        Move.snake_mover()
        Logic.apple_handler()
        Logic.crash_checker()

        Canvas.draw_window()

    pygame.quit()


if __name__ == '__main__':
    main()
