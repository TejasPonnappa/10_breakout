"""
Brick: a single block. Three kinds: normal, strong, unbreakable.
"""

import pygame

NORMAL = "normal"
STRONG = "strong"
UNBREAKABLE = "unbreakable"

STRONG_HITS = 3

NORMAL_COLOR = (200, 90, 90)
UNBREAKABLE_COLOR = (120, 120, 130)
# Indexed by hits_remaining - 1: 1 hit left, 2 hits left, 3 hits left
STRONG_COLORS = [(230, 130, 50), (230, 190, 60), (90, 200, 120)]


class Brick:
    def __init__(self, x, y, width, height, kind=NORMAL):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.kind = kind

        if kind == NORMAL:
            self.hits_remaining = 1
        elif kind == STRONG:
            self.hits_remaining = STRONG_HITS
        elif kind == UNBREAKABLE:
            self.hits_remaining = None  # never counts down
        else:
            raise ValueError(f"Unknown brick kind: {kind}")

    @property
    def is_breakable(self):
        return self.kind != UNBREAKABLE

    @property
    def color(self):
        if self.kind == UNBREAKABLE:
            return UNBREAKABLE_COLOR
        if self.kind == STRONG:
            index = min(self.hits_remaining, len(STRONG_COLORS)) - 1
            return STRONG_COLORS[index]
        return NORMAL_COLOR

    def hit(self):
        """Register a hit. Returns True if the brick is now destroyed."""
        if not self.is_breakable:
            return False
        self.hits_remaining -= 1
        return self.hits_remaining <= 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)