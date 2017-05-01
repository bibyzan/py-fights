import pygame as pg
from player import Player
from fighter import Fighter, Direction, Action


def make_player_2():
    player2 = Player(Direction.left, [1350, 200])
    player2.controls = {Action.running: [pg.K_LEFT, pg.K_RIGHT],
                        Action.attack: [pg.K_PAGEUP],
                        Action.jumping: [pg.K_UP],
                        Action.crouched: [pg.K_DOWN],
                        Action.block: [pg.K_PAGEDOWN]}
    player2.left_direction_key = pg.K_LEFT
    player2.right_direction_key = pg.K_RIGHT
    player2.hp_status_bar.loc[0] = 1250
    player2.charge_status_bar.loc[0] = 1250

    return player2


class App:
    """
    A class to manage our event, game loop, and overall program flow.
    """
    def __init__(self):
        """
        Get a reference to the display surface; set up required attributes;
        and create a Player instance.
        """
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player()
        self.player2 = make_player_2()

    def collision_checks(self):
        if Action.running in self.player.actions and Action.running in self.player2.actions:
            if self.player.will_collide(self.player2) or self.player2.will_collide(self.player):
                self.player.switch_directions()
                self.player2.switch_directions()
                velocity = ((self.player.current_speed + self.player2.current_speed) / 2) * 1.2
                self.player.start_sliding(velocity)
                self.player2.start_sliding(velocity)
        elif self.player.will_collide(self.player2):
            if Action.running in self.player.actions or Action.slide in self.player.actions:
                self.player2.start_sliding_in_direction(self.player.current_speed, self.player.direction)
            elif Action.attack in self.player.actions:
                if Action.block in self.player2.actions:
                    self.player2.start_sliding_in_direction(self.player.attack_charge / 2, self.player.direction)
                else:
                    self.player2.take_damage(self.player.attack_charge, self.player.direction)
            self.player.stop()
        elif self.player2.will_collide(self.player):
            if Action.running in self.player2.actions or Action.slide in self.player2.actions:
                self.player.start_sliding_in_direction(self.player2.current_speed, self.player2.direction)
            elif Action.attack in self.player2.actions:
                if Action.block in self.player.actions:
                    self.player.start_sliding_in_direction(self.player2.attack_charge / 2, self.player2.direction)
                else:
                    self.player.take_damage(self.player2.attack_charge, self.player2.direction)
            self.player2.stop()

        self.player.check_walls(self.screen_rect.width)
        self.player2.check_walls(self.screen_rect.width)

    def check_game_over(self):
        if not self.player.gg and not self.player2.gg:
            if self.player2.is_dead():
                self.player2.be_dead()
                self.player.be_victorious()
            elif self.player.is_dead():
                self.player.be_dead()
                self.player2.be_victorious()

    def event_loop(self):
        """
        Pass events on to the player.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type in (pg.KEYUP, pg.KEYDOWN):
                self.keys = pg.key.get_pressed()
                self.player.handle_event(event)
                self.player2.handle_event(event)

    def display_fps(self):
        """
        Show the program's FPS in the window handle.
        """
        caption = "{} - FPS: {:.2f}".format('sah', self.clock.get_fps())
        pg.display.set_caption(caption)

    def update(self):
        """
        Update the player.
        The current time is passed for purposes of animation.
        """
        self.collision_checks()
        self.player.update(self.screen_rect)
        self.player2.update(self.screen_rect)

    def render(self):
        """
        Perform all necessary drawing and update the screen.
        """
        pg.display.update()
        if self.player.redraw or self.player2.redraw:
            self.screen.fill(pg.Color("slategray"))
            self.screen.blit(pg.image.load("sprites/Stage.jpg"), [0,500])   
            print (self.screen.get_rect())
            self.player.draw(self.screen, True)
            self.player2.draw(self.screen, True)
        if self.player.gg or self.player2.gg:
            pg.init()
            font = pg.font.SysFont("monospace", 72)

            # render text
            label = font.render("MAXIMUM SUPREME VICTORY", 1, (255, 255, 0))
            self.screen.blit(label, (200, 100))

    def main_loop(self):
        """
        Our main game loop; I bet you'd never have guessed.
        """
        while not self.done:
            self.check_game_over()
            self.event_loop()
            self.update()
            self.render()
            self.clock.tick(self.fps)
            self.display_fps()
