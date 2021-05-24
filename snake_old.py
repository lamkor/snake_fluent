"""
CHANGELOG:
1. Kilkasegmentowy wąż teraz rusza się!
2. Napisałem łatwe do rozumienia (i słuchania) komentarzy. Mam nadzieję, że kod będzie jeszcze czytelniejszy
3. Lista segments_pos odnawia się tylko gdy węż zmienił swoją pozycję
4. Za przesunięcie współrzędnych w segments_pos (kiedy widaczna jest zmiana na erkanie) odpowiada funkcja
   snake_big_move(), a za małe przesunięcia (różnicy na ekanie nie widać) odpowiada funkcja snake_small_move()
5. Lista segmentów (segments_pos) węża została przeniesiona do __init__ klasy Player
"""

import pygame
import random

# Ustawienia i parametry gry
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BORDER_SIZE = 16
CELL_SIZE = 16
UPDATE_RATE = 240
APPLE_SPAWNED = False
APPLE_EATEN = False
APPLE_POS = ()

# Wyliczenie maks. liczby kwadratów na plansze. Uwzględniono odstępy gry od okna.
CANVAS_MAX_CELL_X = (SCREEN_WIDTH - 2 * BORDER_SIZE) // CELL_SIZE
CANVAS_MAX_CELL_Y = (SCREEN_HEIGHT - 2 * BORDER_SIZE - 48) // CELL_SIZE
# print(CANVAS_MAX_CELL_X, CANVAS_MAX_CELL_Y)

# Wyświetlenie okna gry
WIN = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Snake")


# Zawiera funkcje potrzebne do wyświetlania wyniku
class Canvas:
    # pygame rysuje prostokąty od lewego górnego rogu. Dwie funkcje poniżej wyliczają to miejsce w pikselach
    @staticmethod
    def x_to_px(x):
        x = x * CELL_SIZE + BORDER_SIZE
        return x

    @staticmethod
    def y_to_px(y):
        y = y * CELL_SIZE + 48
        return y

    @staticmethod
    def draw_window():
        # Tło
        WIN.fill((255, 255, 255))

        # Granice
        pygame.draw.line(WIN, (0, 0, 0), (0, 55), (SCREEN_WIDTH - 1, 55),
                         width=BORDER_SIZE)
        pygame.draw.line(WIN, (0, 0, 0), (SCREEN_WIDTH - 1, 50),
                         (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1),
                         width=BORDER_SIZE * 2)
        pygame.draw.line(WIN, (0, 0, 0), (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1),
                         (0, SCREEN_HEIGHT - 1),
                         width=BORDER_SIZE * 2)
        pygame.draw.line(WIN, (0, 0, 0), (0, SCREEN_HEIGHT - 1), (0, 55),
                         width=BORDER_SIZE * 2 - 1)

        # Jabłko
        if APPLE_SPAWNED:
            pygame.draw.rect(
                WIN, (0, 255, 0),
                (Canvas.x_to_px(APPLE_POS[0]), Canvas.y_to_px(
                    APPLE_POS[1]), CELL_SIZE, CELL_SIZE))

        # Wąż
        for segment in range(len(snake.segments_pos)):
            # Głowa ma trochę inny kolor niż ciało
            if segment == 0:
                pygame.draw.rect(
                    WIN, (255, 125, 125),
                    (Canvas.x_to_px(snake.segments_pos[segment][0]) -
                     CELL_SIZE, Canvas.y_to_px(snake.segments_pos[segment][1]),
                     CELL_SIZE, CELL_SIZE))
            # Reszta ciała
            else:
                pygame.draw.rect(
                    WIN, (255, 0, 0),
                    (Canvas.x_to_px(snake.segments_pos[segment][0]) -
                     CELL_SIZE, Canvas.y_to_px(snake.segments_pos[segment][1]),
                     CELL_SIZE, CELL_SIZE))

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

    # Małe niewidoczne przemieszczenia
    @staticmethod
    def snake_small_move():
        if snake.direction == 'left':
            snake.x_real_pos -= snake.vel
        elif snake.direction == 'right':
            snake.x_real_pos += snake.vel
        elif snake.direction == 'up':
            snake.y_real_pos -= snake.vel
        elif snake.direction == 'down':
            snake.y_real_pos += snake.vel

        # Jak suma małych przemieszczeń przekracza 1 kwadrat, trzeba przesunąć weżą
        if snake.segments_pos[0][0] != int(
                snake.x_real_pos) or snake.segments_pos[0][1] != int(
                    snake.y_real_pos):
            # print('moved')
            # Daje zgodę na przesunięcie
            snake.need_update = True

    @staticmethod
    def snake_big_move():
        # Blokuje niepożądane wywołanie tej funkcji
        snake.need_update = False

        # Podczas przesuwania węża dla głowy generują się nowe współrzędne, drugi segment staje na dotychczasowe miejsce
        # głowy itd. Ostatnia współrzędna starego węża usuwa się.

        # Dotychczasowe współ. węża trafiają do tymczasowego schowku
        old_segments_pos = snake.segments_pos

        # Schowek na nowe wspoł. węża
        new_segments_pos = []
        # Generacja wspoł głowy (bierze z rzeczywistej pozycji głowy)
        new_segments_pos.append([int(snake.x_real_pos), int(snake.y_real_pos)])
        # Przesunięcie grupowe potrzebuje >= 2 segmenta. W przeciwnym wypadku przemieszcza się tylko głowa (kod wyżej)
        if len(old_segments_pos) > 1:
            # Drugi segment staje na dotychczasowe miejsce głowy itd. Ostatni segment starego węża ignoruje się
            for segment_num in range(0, len(old_segments_pos) - 1):
                new_segments_pos.append(old_segments_pos[segment_num])
        # Zapis nowych współ. segmentów na stałe
        snake.segments_pos = new_segments_pos


# Odpowiada za kolizje ze ścianami, jabłek oraz wzrost węża
class Logic:
    # Kolizje
    @staticmethod
    def crash_checker(run):
        if snake.x_real_pos < 1 or snake.x_real_pos > CANVAS_MAX_CELL_X + 1 or snake.y_real_pos < 1 or \
                snake.y_real_pos > CANVAS_MAX_CELL_Y + 1:
            run = False
        return run

    # Logika jabłek
    @staticmethod
    def apple_handler():
        global APPLE_POS, APPLE_SPAWNED, APPLE_EATEN, snake
        # APPLE_SPAWNED odp. za generację jabłka. Jak go nie ma, to ono generuje się. Jak jabłko jest, to nic się nie
        # dzieje
        if not APPLE_SPAWNED:
            APPLE_POS = (random.randint(1, CANVAS_MAX_CELL_X - 1),
                         random.randint(1, CANVAS_MAX_CELL_Y - 1))
            APPLE_SPAWNED = True
        # Sprawdza kolizję węża i jabłka. Po co 1? Nie wiem, ale bez jedynki to działa niewłaściwie
        if (int(snake.x_real_pos) - 1, int(snake.y_real_pos)) == APPLE_POS:
            print("Zjadłem :)")
            APPLE_SPAWNED = False
            # Jak jabłko zjada się, to daje się zgoda na wzrost węża
            APPLE_EATEN = True

    # Wzrost węża od jabłek
    @staticmethod
    def snake_grow():
        global APPLE_EATEN
        if APPLE_EATEN:
            #TODO Zrobić spawn segmenta z właściwych stron
            # Póki co ogon spawni się z boku
            snake.segments_pos.append(
                [snake.segments_pos[-1][0] - 1, snake.segments_pos[-1][1]])
            APPLE_EATEN = False


class Player:
    def __init__(self, x, y):
        self.x_px = Canvas.x_to_px(x)
        self.y_px = Canvas.y_to_px(y)
        self.x_real_pos = x
        self.y_real_pos = y
        self.segments_pos = []
        self.need_update = False
        self.direction = 'left'
        self.vel = 0.1 / 6


snake = Player(CANVAS_MAX_CELL_X // 2, CANVAS_MAX_CELL_Y // 2)
# Zapis pierwszego segmentu — głowy
snake.segments_pos.append([CANVAS_MAX_CELL_X // 2, CANVAS_MAX_CELL_Y // 2])


# Zarząda działaniem gry
def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(UPDATE_RATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        Move.key_handler()
        Move.snake_small_move()
        if snake.need_update:
            Move.snake_big_move()

        Logic.apple_handler()
        if APPLE_EATEN:
            Logic.snake_grow()

        run = Logic.crash_checker(run)
        # Debug apples and snake position
        print(f"{APPLE_POS}  {int(snake.x_real_pos)}, {int(snake.y_real_pos)}")
        Canvas.draw_window()

    pygame.quit()


if __name__ == '__main__':
    main()
'''
import pygame
import random
pygame.font.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 432
# BORDER_SIZE = 10
BORDER_SIZE = 0
cell_siza = 16
FPS = 240
WIN = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Snake")

def x_to_px(x):
  x = x * cell_siza
  return x
def y_to_px(y):
  y = y * cell_siza + 48
  return y
class player(object):
  def __init__(self, x, y, size):
    self.x = x
    self.y = y
    self.width = size
    self.height = size
    self.vel = 0.1 / 6
    self.vertical = 0
    self.horizontal = 0
    self.x_px = x_to_px(x)
    self.y_px = y_to_px(y)
    self.x_real = x
    self.y_real = y
    self.x_display = x
    self.y_display = y
snake = player((SCREEN_WIDTH // cell_siza) // 2, (SCREEN_HEIGHT // cell_siza) // 2, cell_siza)
def draw_window():
    # WIN.fill((255, 255, 255))
    # for x in range(BORDER_SIZE, SCREEN_WIDTH - BORDER_SIZE, CELL_SIZE):
    #   for y in range(50 + BORDER_SIZE, SCREEN_HEIGHT - BORDER_SIZE, CELL_SIZE):
    #     if random.random() <= 0.5:
    #       pygame.draw.rect(WIN, (255, 0, 0), (x, y, CELL_SIZE, CELL_SIZE))
    # # Rysowanie granicy planszy
    # pygame.draw.line(WIN, (0, 0, 0), (0, 50), (SCREEN_WIDTH - 1, 50), width=1)
    # pygame.draw.line(WIN, (0, 0, 0), (SCREEN_WIDTH - 1, 50), (SCREEN_WIDTH - 1, 719), width=BORDER_SIZE*2)
    # pygame.draw.line(WIN, (0, 0, 0), (SCREEN_WIDTH - 1, 719), (0, 719), width=BORDER_SIZE*2)
    # pygame.draw.line(WIN, (0, 0, 0), (0, 719), (0, 50), width=BORDER_SIZE*2)
    # pygame.display.update()
    WIN.fill((0, 0, 0))
    pygame.draw.rect(WIN, (255, 0, 0), (snake.x_px - snake.width, snake.y_px, snake.width, snake.height))
    pygame.display.update()
def death_screen():
  WIN.fill((0, 0, 0))
  death_screen_font = pygame.font.SysFont('comicsans', 40)
  death_screen_text = death_screen_font.render("Naciśnij spację, żeby zacząć od nowa", 1, (255, 255, 255))
  WIN.blit(death_screen_text, (SCREEN_WIDTH/2 - death_screen_text.get_width()//2, SCREEN_HEIGHT/2-death_screen_text.get_height()//2))
  pygame.display.update()
def main():
  clock = pygame.time.Clock()
  run = True
  while run:
    clock.tick(FPS)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
         run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
      run = False
      pygame.quit()
    if keys[pygame.K_LEFT]:
      if snake.horizontal!=1:
        snake.horizontal = -1
        snake.vertical = 0
    elif keys[pygame.K_RIGHT]:
      if snake.horizontal!=-1:
        snake.horizontal = 1
        snake.vertical = 0
    elif keys[pygame.K_UP]:
      if snake.vertical!=1:
        snake.horizontal = 0
        snake.vertical = -1
    elif keys[pygame.K_DOWN]:
      if snake.vertical!=-1:
        snake.horizontal = 0
        snake.vertical = 1
    if snake.x_px >= snake.vel and snake.x_px < SCREEN_WIDTH - snake.width:
      snake.x_real += snake.vel * snake.horizontal
    else:
      print("wlazłeś w ściane")
      death_screen()
      run = False
      break
    if snake.y_px >= snake.vel and snake.y_px < SCREEN_HEIGHT - snake.height:
      snake.y_real += snake.vel * snake.vertical
    else:
      print("wlazłeś w ściane")
      death_screen()
      run = False
      break
    snake.x_display = int(snake.x_real)
    snake.y_display = int(snake.y_real)
    snake.x_px = x_to_px(snake.x_display)
    snake.y_px = y_to_px(snake.y_display)
    draw_window()
  keys = pygame.key.get_pressed()
  if keys[pygame.K_SPACE]:
    run = False
    main()
if __name__ == '__main__':
    main()
'''
