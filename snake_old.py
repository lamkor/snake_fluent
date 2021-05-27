import pygame
import random
import copy
import time

# Ustawienia i parametry gry
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BORDER_SIZE = 16
CELL_SIZE = 24
UPDATE_RATE = 250
APPLE_SPAWNED = False
APPLE_EATEN = False
APPLE_POS = ()

# Wyliczenie maks. liczby kwadratów na plansze. Uwzględniono odstępy gry od okna.
CANVAS_MAX_CELL_X = (SCREEN_WIDTH - 2 * BORDER_SIZE) // CELL_SIZE - 1
CANVAS_MAX_CELL_Y = (SCREEN_HEIGHT - 2 * BORDER_SIZE - 40) // CELL_SIZE - 1
# print(CANVAS_MAX_CELL_X, CANVAS_MAX_CELL_Y)

# Wyświetlenie okna gry
WIN = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Snake")


# Zawiera funkcje potrzebne do wyświetlania wyniku
class Canvas:
    # pygame rysuje prostokąty od lewego górnego rogu. Dwie funkcje poniżej wyliczają to miejsce w pikselach
    @staticmethod
    def x_to_px(x):
        x = x * CELL_SIZE + 2 * BORDER_SIZE + 8
        return x

    @staticmethod
    def y_to_px(y):
        y = y * CELL_SIZE + 56
        return y

    @staticmethod
    def draw_window():
        # Tło
        WIN.fill((255, 255, 255))

        # Granice
        pygame.draw.line(WIN, (0, 0, 0), (0, 47), (SCREEN_WIDTH - 1, 47), width=BORDER_SIZE)
        pygame.draw.line(WIN, (0, 0, 0), (SCREEN_WIDTH - 1, 50), (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1),
                         width=BORDER_SIZE * 2)
        pygame.draw.line(WIN, (0, 0, 0), (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1), (0, SCREEN_HEIGHT - 1),
                         width=BORDER_SIZE * 2)
        pygame.draw.line(WIN, (0, 0, 0), (0, SCREEN_HEIGHT - 1), (0, 55), width=BORDER_SIZE * 2 - 1)

        # Jabłko
        if APPLE_SPAWNED:
            pygame.draw.rect(WIN, (0, 255, 0),
                             (Canvas.x_to_px(APPLE_POS[0]), Canvas.y_to_px(APPLE_POS[1]), CELL_SIZE, CELL_SIZE))

        # Wąż
        for segment in range(len(snake.segments_pos)):
            # Głowa ma trochę inny kolor niż ciało
            if segment == 0:
                pygame.draw.rect(
                    WIN, (255, 125, 125),
                    (int(Canvas.x_to_px(snake.segments_pos[segment][0]) -
                         CELL_SIZE), int(Canvas.y_to_px(snake.segments_pos[segment][1])),
                     CELL_SIZE, CELL_SIZE))
            # Reszta ciała
            else:
                pygame.draw.rect(
                    WIN, (255, 0, 0),
                    (int(Canvas.x_to_px(snake.segments_pos[segment][0]) -
                         CELL_SIZE), int(Canvas.y_to_px(snake.segments_pos[segment][1])),
                     CELL_SIZE, CELL_SIZE))

        pygame.display.update()


# Odpowiada za przemieszczenie węża
class Move:
    # Precyzuje rzeczywiste współrzędne
    @staticmethod
    def rounder(long_position):
        long_position = int(round(long_position, 3) * 1000) / 1000
        return long_position

    # Sterowanie klawiszami
    @staticmethod
    def key_handler():
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and snake.direction_last != 'left':
            snake.direction = 'right'
        elif keys[pygame.K_LEFT] and snake.direction_last != 'right':
            snake.direction = 'left'
        elif keys[pygame.K_UP] and snake.direction_last != 'down':
            snake.direction = 'up'
        elif keys[pygame.K_DOWN] and snake.direction_last != 'up':
            snake.direction = 'down'
        elif keys[pygame.K_ESCAPE]:
            exit()

    # Odpowiada za przesunięcie węża co klatkę
    @staticmethod
    def snake_small_mover(direct, segments_pos):
        temp = copy.deepcopy(segments_pos[:1])
        if direct == 'left':
            temp[0][0] -= snake.vel
        elif direct == 'right':
            temp[0][0] += snake.vel
        elif direct == 'up':
            temp[0][1] -= snake.vel
        elif direct == 'down':
            temp[0][1] += snake.vel

        temp[0][0], temp[0][1] = round(temp[0][0], 3), round(temp[0][1], 3)

        temp.extend(segments_pos[:-1])
        segments_pos = temp
        return segments_pos


# Odpowiada za kolizje ze ścianami, jabłek oraz wzrost węża
class Logic:
    # Kolizje
    @staticmethod
    def crash_checker(run):
        if snake.segments_pos[0][0] < 0.0 or snake.segments_pos[0][0] > float(CANVAS_MAX_CELL_X) or \
                snake.segments_pos[0][1] < 0.0 or \
                snake.segments_pos[0][1] > float(CANVAS_MAX_CELL_Y):
            run = False
        return run

    # Logika jabłek
    @staticmethod
    def apple_handler():
        global APPLE_POS, APPLE_SPAWNED, APPLE_EATEN, snake
        # APPLE_SPAWNED odp. za generację jabłka. Jak go nie ma, to ono generuje się. Jak jabłko jest, to nic się nie
        # dzieje
        if not APPLE_SPAWNED:
            APPLE_POS = (random.randint(0, CANVAS_MAX_CELL_X - 1),
                         random.randint(0, CANVAS_MAX_CELL_Y))
            APPLE_SPAWNED = True
        # Sprawdza kolizję węża i jabłka. Po co 1? Nie wiem, ale bez jedynki to działa niewłaściwie
        if (int(snake.segments_pos[0][0] - 1), int(snake.segments_pos[0][1])) == APPLE_POS:
            print("Zjadłem :)")
            APPLE_SPAWNED = False
            # Jak jabłko zjada się, to daje się zgoda na wzrost węża
            APPLE_EATEN = True

    # Wzrost węża od jabłek
    @staticmethod
    def snake_grow():
        global APPLE_EATEN
        if APPLE_EATEN:
            # TODO Zrobić spawn segmenta z właściwych stron
            # Póki co ogon spawni się z boku
            # Move.snake_small_mover()
            for i in range(40):
                snake.segments_pos.append([snake.segments_pos[-1][0] - 1, snake.segments_pos[-1][1]])


class Player:
    def __init__(self):
        self.segments_pos = []
        self.segments_pos_old = []
        self.need_update = False
        self.direction_last = 'left'
        self.direction = self.direction_last
        self.vel = 0.025


snake = Player()
# Zapis pierwszego segmentu — głowy
snake.segments_pos.append([CANVAS_MAX_CELL_X // 2, CANVAS_MAX_CELL_Y // 2])


# Zarząda działaniem gry
def main():
    global APPLE_EATEN
    clock = pygame.time.Clock()
    run = True
    fps = 0
    start_time = time.time()
    while run:
        if time.time() - start_time > 1:
            start_time = time.time()
            print(fps)
            fps = 0
        else:
            fps += 1
        clock.tick(UPDATE_RATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if APPLE_EATEN:# and snake.segments_pos[0][0] % 1 == 0.0 and snake.segments_pos[0][1] % 1 == 0.0:
            Logic.snake_grow()
            APPLE_EATEN = False

        # Move.key_handler()
        Move.key_handler()
        snake.segments_pos = Move.snake_small_mover(snake.direction_last, snake.segments_pos)
        Logic.apple_handler()

        if snake.segments_pos[0][0] % 1 == 0.0 and snake.segments_pos[0][1] % 1 == 0.0:
            snake.direction_last = snake.direction
            # Move.snake_small_mover(snake.direction_last)
            Logic.apple_handler()

        run = Logic.crash_checker(run)
        # Debug apples and snake position
        # print(f"{APPLE_POS}  {snake.segments_pos[0][0]}, {snake.segments_pos[0][1]}")
        # print(f"{APPLE_POS}  {snake.segments_pos[0][0]}, {snake.segments_pos[0][1]}")
        Canvas.draw_window()

    pygame.quit()


if __name__ == '__main__':
    main()
