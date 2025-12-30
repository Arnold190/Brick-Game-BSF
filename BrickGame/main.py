import pygame
import sys
import random

pygame.init()

# -------------------- CONSTANTS --------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 255)
RED = (200, 60, 60)
GREEN = (60, 200, 120)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Brick Breaker")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 40)

# -------------------- CLASSES --------------------


class Paddle:
    def __init__(self):
        self.width = 120
        self.height = 15
        self.rect = pygame.Rect(
            WIDTH // 2 - self.width // 2,
            HEIGHT - 40,
            self.width,
            self.height
        )
        self.speed = 7

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)


class Ball:
    def __init__(self):
        self.radius = 10
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2, 20, 20)
        self.speed_x = random.choice([-4, 4])
        self.speed_y = -4

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wall collision
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.speed_y *= -1

    def bounce(self):
        self.speed_y *= -1

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, self.rect)


class Brick:
    def __init__(self, x, y, hits):
        self.rect = pygame.Rect(x, y, 70, 25)
        self.hits = hits
        self.max_hits = hits
        self.color = RED if hits == 1 else GREEN

    def hit(self):
        self.hits -= 1
        if self.hits == 1:
            self.color = RED
        return self.hits <= 0

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)


class Game:
    def __init__(self):
        self.state = "MENU"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.max_level = 5

        # self.paddle = Paddle()
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []

    def create_bricks(self):
        bricks = []
        rows = 3 + self.level      # more rows each level
        cols = 10

        for row in range(rows):
            for col in range(cols):
                x = 35 + col * 80
                y = 60 + row * 40

                # Strong bricks appear in higher levels
                hits = 2 if row < self.level // 2 else 1
                bricks.append(Brick(x, y, hits))

        return bricks

    def start_level(self):
        self.ball.reset()
        self.ball.speed_x *= (1 + self.level * 0.1)
        self.ball.speed_y *= (1 + self.level * 0.1)
        self.bricks = self.create_bricks()

    def reset(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.state = "PLAYING"
        self.start_level()

    def next_level(self):
        self.level += 1
        if self.level > self.max_level:
            self.state = "GAME_OVER"
        else:
            self.start_level()

    def update(self):
        keys = pygame.key.get_pressed()

        if self.state == "PLAYING":
            self.paddle.move(keys)
            # self.player.move(keys)
            self.ball.update()

            # Player collision
            # -----------------
            # if self.ball.rect.colliderect(self.player.rect):
            #    self.ball.bounce()
            # -----------------

            if self.ball.rect.colliderect(self.paddle.rect):
                self.ball.speed_y = -abs(self.ball.speed_y)

                # Adjust angle based on hit position
                hit_pos = (self.ball.rect.centerx -
                           self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
                self.ball.speed_x = hit_pos * 5

            # Brick collision
            for brick in self.bricks[:]:
                if self.ball.rect.colliderect(brick.rect):
                    destroyed = brick.hit()
                    self.ball.bounce()
                    self.score += 10 * brick.max_hits
                    if destroyed:
                        self.bricks.remove(brick)
                    break

            # Ball lost
            if self.ball.rect.bottom >= HEIGHT:
                self.lives -= 1
                self.ball.reset()

            # Level cleared
            if not self.bricks:
                self.next_level()

            # Game over
            if self.lives == 0:
                self.state = "GAME_OVER"

    def draw_hud(self):
        screen.blit(font.render(f"Score: {self.score}", True, WHITE), (10, 10))
        screen.blit(font.render(
            f"Lives: {self.lives}", True, WHITE), (120, 10))
        screen.blit(font.render(
            f"Level: {self.level}", True, WHITE), (230, 10))

    def draw(self):
        screen.fill(BLACK)

        if self.state == "MENU":
            title = big_font.render("BRICK BREAKER", True, WHITE)
            info = font.render("Press SPACE to Play", True, WHITE)
            screen.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
            screen.blit(info, (WIDTH // 2 - 90, HEIGHT // 2 + 10))

        elif self.state == "PLAYING":
            # self.paddle.draw()
            self.paddle.draw()
            self.ball.draw()
            for brick in self.bricks:
                brick.draw()
            self.draw_hud()

        elif self.state == "GAME_OVER":
            msg = "YOU WIN!" if self.level > self.max_level else "GAME OVER"
            screen.blit(big_font.render(msg, True, WHITE),
                        (WIDTH // 2 - 100, HEIGHT // 2 - 60))
            screen.blit(font.render(f"Final Score: {self.score}", True, WHITE),
                        (WIDTH // 2 - 80, HEIGHT // 2))
            screen.blit(font.render("Press R to Restart or Q to Quit", True, WHITE),
                        (WIDTH // 2 - 140, HEIGHT // 2 + 40))

        pygame.display.flip()


# -------------------- MAIN LOOP --------------------

game = Game()
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game.state == "MENU" and event.key == pygame.K_SPACE:
                game.reset()

            if game.state == "GAME_OVER":
                if event.key == pygame.K_r:
                    game.reset()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    game.update()
    game.draw()
