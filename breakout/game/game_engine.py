"""
GameEngine: owns the paddle, ball, and bricks.

Starter version: single brick type, no lives yet, no score/combo yet.
Ball-brick collision also has a known bug (see game/collision.py) that
Task 1 asks you to fix. If the ball falls below the paddle, it just
resets to the starting position with no consequence - that's what
Task 2 builds on.
"""

import pygame
import itertools
import random

from game.paddle import Paddle
from game.ball import Ball
from game.brick import Brick, NORMAL, STRONG, UNBREAKABLE
from game.collision import handle_ball_brick_collision
from game.renderer import WIDTH, HEIGHT

BRICK_ROWS = 4
BRICK_COLS = 8
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 6
BRICK_TOP_MARGIN = 50
STARTING_LIVES = 3
STRONG_SHARE = 0.20
UNBREAKABLE_SHARE = 0.10

class GameEngine:
    def __init__(self):
        self.restart()

    def restart(self):
        self.paddle = Paddle(x=WIDTH / 2, y=HEIGHT - 30)
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)
        self.bricks = self._build_bricks()
        self.lives = STARTING_LIVES
        self.game_over = False

    def _random_layout(self):
        """Return {(row, col): kind} with an exact 70/20/10 split, randomly placed."""
        cells = [(r, c) for r in range(BRICK_ROWS) for c in range(BRICK_COLS)]
        total = len(cells)
        n_unbreakable = round(total * UNBREAKABLE_SHARE)
        n_strong = round(total * STRONG_SHARE)

        # Keep unbreakable bricks from touching each other (including diagonally)
        # so they end up spread out. Retry a limited number of times.
        for _ in range(200):
            unbreakable = random.sample(cells, n_unbreakable)
            touching = any(
                abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1
                for a, b in itertools.combinations(unbreakable, 2)
            )
            if not touching:
                break

        remaining = [c for c in cells if c not in unbreakable]
        strong = random.sample(remaining, n_strong)

        layout = {cell: NORMAL for cell in cells}
        for cell in strong:
            layout[cell] = STRONG
        for cell in unbreakable:
            layout[cell] = UNBREAKABLE
        return layout

    def _build_bricks(self):
        bricks = []
        layout = self._random_layout()
        total_width = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (WIDTH - total_width) / 2
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)
                bricks.append(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, kind=layout[(row, col)]))
        return bricks

    def _reset_ball(self):
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        dx = 0
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.paddle.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.paddle.speed
        self.paddle.move(dx, WIDTH)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.restart()

    def update(self):
        if self.game_over:
            return

        self.ball.update()
        self.ball.bounce_off_walls(WIDTH)

        if self.ball.get_rect().colliderect(self.paddle.get_rect()) and self.ball.vy > 0:
            self.ball.bounce_off_paddle(self.paddle.get_rect())

        for brick in self.bricks:
            if handle_ball_brick_collision(self.ball, brick):
                if brick.hit():
                    self.bricks.remove(brick)
                break

        if self.ball.is_below(HEIGHT):
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.paddle, self.ball, self.bricks)
        breakable_left = sum(1 for b in self.bricks if b.is_breakable)
        renderer.draw_text(surface, font, f"Bricks left: {breakable_left}", (10, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (WIDTH - 110, 10))
        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - Press R to restart")
