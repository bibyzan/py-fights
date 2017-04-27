import pygame as pg

"""
Classes for displaying various stats for in game
"""


class StatusBar:
    def __init__(self, fill, color, loc):
        self.fill_value = fill
        self.max_value = 100
        self.color = color
        self.loc = loc
        self.size = [250, 37]
        self.bar_image = pg.image.load("hud/bar.png")

    def decimal_filled(self):
        return self.fill_value / self.max_value

    def make_rect(self):
        return pg.Rect(self.loc, self.size)

    def make_fill_rect(self):
        new_size = list(self.size)
        new_size[0] = (self.size[0] * self.decimal_filled()) - 2
        new_loc = list(self.loc)
        new_loc[0] += 2
        return pg.Rect(new_loc, new_size)

    def draw(self, surface):
        resized_image = pg.transform.scale(self.bar_image, self.size)
        pg.draw.rect(surface, self.color, self.make_fill_rect())
        surface.blit(resized_image, self.loc)