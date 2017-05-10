from fighter import Fighter, Direction, Action
from statusbar import StatusBar
import pygame as pg


class Player(Fighter):
    def __init__(self, direction=Direction.right, loc=[50,200]):
        super().__init__(direction, loc)
        self.pressed_keys = []
        self.hp_status_bar = StatusBar(100, pg.Color("red"), [5,10])
        self.charge_status_bar = StatusBar(0, pg.Color("lightblue"), [5, 50])
        self.right_direction_key = pg.K_d
        self.left_direction_key = pg.K_a
        self.controls = {Action.running: [pg.K_a, pg.K_d],
                         Action.block: [pg.K_LSHIFT],
                         Action.jumping: [pg.K_w],
                         Action.crouched: [pg.K_s],
                         Action.attack: [pg.K_SPACE]}

    def handle_event(self, event):
        if not self.gg:
            if event.key in self.control_keys():
                if event.type == pg.KEYDOWN:
                    self.press_key(event.key)
                elif event.type == pg.KEYUP:
                    self.key_released(event.key)

    def control_keys(self):
        control_keys = []
        for action, keys in self.controls.items():
            control_keys += keys

        return control_keys

    def press_key(self, key):
        if key in self.control_keys():
            self.pressed_keys += [key]
            if Action.damaged not in self.actions:
                if key in self.controls[Action.running]:
                    self.start_running_with_key(key)
                elif key in self.controls[Action.block]:
                    self.start_block()
                elif key in self.controls[Action.jumping]:
                    self.start_jumping_charge()
                elif key in self.controls[Action.crouched]:
                    self.start_crouching()
                elif key in self.controls[Action.attack]:
                    if Action.crouched in self.actions:
                        self.start_attacking()
                    else:
                        self.start_charging_attack()

    def start_running_with_key(self, key):
        if Action.crouched not in self.actions:
            if key == self.right_direction_key:
                self.start_running(Direction.right)
            elif key == self.left_direction_key:
                self.start_running(Direction.left)

    def start_sliding_with_key(self, velocity, key):
        if key == self.right_direction_key:
            self.direction = Direction.right
            self.start_sliding(velocity)
        elif key == self.left_direction_key:
            self.direction = Direction.left
            self.start_sliding(velocity)

    def pressed_key(self):
        return self.pressed_keys[-1]

    def key_released(self, key):
        new_pressed_keys = []
        for pressed_key in self.pressed_keys:
            if pressed_key != key:
                new_pressed_keys += [pressed_key]

        self.pressed_keys = new_pressed_keys

        if key == self.controls[Action.block][0]:
            self.is_blocking = False
            self.remove_action(Action.block)

        if key == self.controls[Action.attack][0]:
            self.remove_action(Action.charge)
            self.start_attacking()
            return

        if key == self.controls[Action.crouched][0]:
            self.remove_action(Action.crouched)
            self.pressed_keys = []
            self.current_speed = self.start_speed

        if key == self.controls[Action.jumping][0]:
            self.start_jumping()
            return

        if not self.pressed_keys:
            if self.current_speed > ((self.start_speed + self.max_speed) / 2):
                self.start_sliding_with_key(self.current_speed, key)
            else:
                self.update_action(Action.idle)

            return

        for remaining_key in self.pressed_keys:
            if remaining_key in self.controls[Action.running]:
                self.start_running_with_key(remaining_key)
                break

    def draw(self, surface, force=False):
        super().draw(surface, force)
        self.hp_status_bar.fill_value = self.hp
        self.hp_status_bar.draw(surface)

        if Action.charge in self.actions:
            self.charge_status_bar.fill_value = self.attack_charge / self.attack_max_charge * 100
            self.charge_status_bar.draw(surface)