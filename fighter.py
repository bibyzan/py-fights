import pygame as pg

"""
Bennett Rasmussen 2017
Fighter Class made to facilitate the controls of a generic fighter with no keyboard handling
"""


class Action:
    """
    Basically an enum here. String values are that of their corresponding sprite file names
    """
    idle = "Still"
    running = "Run"
    falling = "Falling"
    attack = "Punch"
    charge = "PunchCharge"
    slide = "Slide"
    block = "Block"
    jump_charge = "JumpCharge"
    jumping = "Jump"
    crouched = "StillCrouched"
    damaged = "Damage"
    crouch_attack = "CrouchedPunch"
    victory = "Victory"
    actor_idle = [idle]
    directional_actions = [block, running, falling, attack, charge, slide, crouched, damaged, crouch_attack]


class Direction:
    """
    Basically an enum for 2 directions
    """
    right = "Right"
    left = "Left"

    def multiplier(self):
        if self is Direction.right:
            return 1
        elif self is Direction.left:
            return -1


def opposite_direction(direction):
    if direction is Direction.right:
        return Direction.left
    elif direction is Direction.left:
        return Direction.right


class Fighter:
    """
    Implementation of Fighter class.
    """
    sprite_update_frames = {Action.idle: 60,
                            Action.running: 5,
                            Action.jump_charge: 0,
                            Action.crouched: 60,
                            Action.slide: 15,
                            Action.charge: 10,
                            Action.crouch_attack: 15,
                            Action.damaged: 0,
                            Action.victory: 60}

    def __init__(self, facing=Direction.right, loc=[0, 0]):
        """
        initialize this bitch. load sprites n stuff
        :param facing: direction value
        :param loc: coordinate on screen
        """
        self.jump_start_charge = 5
        self.jump_charge = self.jump_start_charge
        self.jump_max_charge = 35
        self.hp = 100
        self.start_speed = 2
        self.max_speed = 12
        self.current_speed = self.start_speed
        self.rect = (100, 180)
        self.sprites = {}
        self.current_sprite_list = []
        self.load_sprites()
        self.direction = facing
        self.slide_direction = self.direction
        self.loc = loc
        self.update_frames = 15
        self.update_count_down = self.update_frames
        self.actions = Action.actor_idle
        self.updated_sprite_list = False
        self.sprite_index = -1
        self.image = self.sprites["Still"][0]
        self.redraw = True
        self.velocity = 0
        self.attack_start_charge = 2
        self.attack_charge = self.attack_start_charge
        self.attack_max_charge = 20
        self.gg = False

    def load_sprites(self):
        """
        Loads all sprite files into program memory
        :return: null
        """
        sprite_files = {"Block": 1,
                        "Damage": 2,
                        "Falling": 1,
                        "Jump": 1,
                        "Punch": 1,
                        "PunchCharge": 2,
                        "Still": 2,
                        "Run": 3,
                        "Slide": 2,
                        "JumpCharge": 1,
                        "StillCrouched": 2,
                        "CrouchedPunch": 3,
                        "Victory": 2}
        reversed_sprites = Action.directional_actions
        sprites = {}

        for name, amount in sprite_files.items():
            sprite_list = []
            for i in range(1, amount + 1):
                full_name = name
                if name in reversed_sprites:
                    full_name += "Right"
                new_sprite = pg.image.load("sprites/" + full_name + str(i) + ".png")
                new_sprite = pg.transform.scale(new_sprite, self.rect)
                sprite_list += [new_sprite]

            if name in reversed_sprites:
                sprites[name + "Right"] = sprite_list

                sprite_list_reversed = []
                for sprite in sprite_list:
                    transformed_sprite = pg.transform.flip(sprite, True, False)
                    sprite_list_reversed += [transformed_sprite]

                sprites[name + "Left"] = sprite_list_reversed
            else:
                sprites[name] = sprite_list

        self.sprites = sprites

    def set_update_frames(self, new_update_frames):
        """
        reset update frames and countdown vars
        :param new_update_frames: new value for both
        :return: null
        """
        self.update_frames = new_update_frames
        self.update_count_down = self.update_frames

    def update_image(self):
        """
        Called on every frame. Updates image based on current actions contained in self.actions
        :return: null
        """
        if self.updated_sprite_list:
            self.image = self.increment_sprite_index(True)
            self.updated_sprite_list = False
            self.update_count_down = self.update_frames
            self.redraw = True
        elif self.update_frames == 0:
            return
        elif self.update_count_down == 0:
            if self.sprite_index == 2:
                self.remove_action(Action.crouch_attack)
            self.image = self.increment_sprite_index()
            self.update_count_down = self.update_frames
            self.redraw = True
        else:
            self.update_count_down -= 1

    def increment_sprite_index(self, reset=False):
        """
        :param reset: whether or not first sprite should be returned
        :return: the sprite based on the current incremented self.sprite_index
        """
        self.sprite_index += 1
        if self.sprite_index >= len(self.current_sprite_list) or reset:
            self.sprite_index = 0

        return self.current_sprite_list[self.sprite_index]

    def actions_contained(self, actions):
        for action in self.actions:
            for check_action in actions:
                if action is check_action:
                    return True
        return False

    def switch_directions(self):
        self.direction = opposite_direction(self.direction)

    def start_charging_attack(self):
        if not self.actions_contained([Action.falling, Action.attack, Action.block, Action.jumping, Action.jump_charge]):
            self.attack_charge = self.attack_start_charge
            self.stop_running()
            self.update_action(Action.charge)

    def start_attacking(self):
        if Action.crouched in self.actions:
            self.update_action(Action.crouch_attack)
        else:
            self.remove_action(Action.charge)
            self.update_action(Action.attack)

    def start_crouching(self):
        """
        switches fighter to crouch stance
        """
        if not self.actions_contained([Action.falling, Action.jumping, Action.jump_charge]):
            self.stop_running()
            self.update_action(Action.crouched)

    def start_jumping_charge(self):
        """
        begin charging jump
        """
        if not self.actions_contained([Action.falling, Action.jumping]):
            self.stop_running()
            self.update_action(Action.jump_charge)
            self.jump_charge = self.jump_start_charge

    def start_jumping(self):
        """
        upon jump action finishing, jump releases based on charge
        """
        self.remove_action(Action.jump_charge)
        self.update_action(Action.jumping)
        self.image = self.current_sprite_list[-1]

    def start_block(self):
        """
        puts up the dukes and stops fighter
        """
        self.stop_running()
        self.update_action(Action.block)

    def start_running(self, direction):
        """
        begins running and resets speed
        :param direction: to start running in
        """
        self.current_speed = self.start_speed
        self.direction = direction
        self.update_action(Action.running)

    def stop_running(self):
        if Action.running in self.actions:
            self.start_sliding(self.current_speed)

    def stop(self):
        moving_actions = [Action.attack, Action.running, Action.slide]
        if self.actions_contained(moving_actions):
            for moving_action in moving_actions:
                self.remove_action(moving_action)

    def take_damage(self, damage, direction):
        self.stop()
        self.hp -= damage
        self.start_sliding_in_direction(damage, direction)
        self.update_action(Action.damaged)

    def start_sliding(self, velocity):
        """
        player continues moving until velocity is 0, usually after running
        :param velocity: how fast to start sliding
        :param direction: which direction to slide in
        """
        self.start_sliding_in_direction(velocity, self.direction)

    def start_sliding_in_direction(self, velocity, direction):
        self.slide_direction = direction
        self.remove_action(Action.running)
        self.velocity = velocity
        self.update_action(Action.slide)

    def update_action(self, action):
        """
        update current sprite list vars.
        :param action: action to be added to self.actions
        """
        self.current_sprite_list = self.sprites_from_action(action)
        self.updated_sprite_list = True
        self.add_action(action)
        if action in Fighter.sprite_update_frames.keys():
            self.set_update_frames(Fighter.sprite_update_frames[action])

    def sprites_from_action(self, action):
        """
        :param action: for sprites
        :return: sprite list for action
        """
        if action in Action.directional_actions:
            return self.sprites[action + self.direction]

        return self.sprites[action]

    def direction_multiplier(self):
        if self.direction == Direction.right:
            return 1
        elif self.direction == Direction.left:
            return -1

    def slide_multiplier(self):
        if self.slide_direction == Direction.right:
            return 1
        elif self.slide_direction == Direction.left:
            return -1

    def update_screen_loc(self):
        """
        updates fighters self.loc called on every frame
        """
        old_loc = list(self.loc)

        self.loc = self.next_loc()
        if self.loc != old_loc:
            for action in self.actions:
                if action == Action.running:
                    if self.current_speed < self.max_speed:
                        self.current_speed += 0.5
                elif action == Action.slide:
                    self.velocity -= 0.5
                    self.current_speed = self.velocity
                    if self.velocity <= 0:
                        self.remove_action(Action.slide)
                        self.remove_action(Action.damaged)
                elif action == Action.jumping:
                    if self.jump_charge > self.jump_start_charge:
                        self.jump_charge -= 1
                    else:
                        self.remove_action(Action.jumping)
                elif action == Action.attack:
                    self.attack_charge -= 1
                    if self.attack_charge <= 0:
                        self.remove_action(Action.attack)

            self.redraw = True

    def next_loc(self):
        next_loc = list(self.loc)

        for action in self.actions:
            if action == Action.running:
                next_loc[0] = self.loc[0] + (self.current_speed * self.direction_multiplier())
            elif action == Action.falling:
                next_loc[1] = self.loc[1] + 5
            elif action == Action.slide:
                next_loc[0] = self.loc[0] + (self.velocity * self.slide_multiplier())
            elif action == Action.jumping:
                next_loc[1] = self.loc[1] - (self.jump_charge / 2)
            elif action == Action.attack:
                next_loc[0] = self.loc[0] + ((self.attack_charge * 2) * self.direction_multiplier())

        return next_loc

    def update(self, screen_rect):
        """
        Updates all states on fighter. called on every frame
        """
        if self.actions == Action.actor_idle:
            if self.current_sprite_list != self.sprites[Action.idle]:
                self.current_sprite_list = self.sprites_from_action(Action.idle)
                self.update_frames = Fighter.sprite_update_frames[Action.idle]
                self.updated_sprite_list = True
        else:
            last_action = self.actions[-1]
            action_sprites = self.sprites_from_action(last_action)
            if self.current_sprite_list != action_sprites:
                self.current_sprite_list = action_sprites
                self.updated_sprite_list = True

        if Action.jump_charge in self.actions:
            if self.jump_charge < self.jump_max_charge:
                self.jump_charge += 1

        if Action.charge in self.actions:
            if self.attack_charge < self.attack_max_charge:
                self.attack_charge += .2

        if Action.jumping not in self.actions and not self.gg:
            self.check_gravity(screen_rect.height)
        self.update_screen_loc()
        self.update_image()

    def draw(self, surface, force=False):
        """
        shows image of fighter on game surface
        :param surface: screen to show fighter on
        :param force: ignores redraw
        """
        if self.redraw or force:
            surface.blit(self.image, self.loc)
            self.redraw = False

    def make_rect(self):
        return pg.Rect(self.loc, self.rect)

    def will_collide(self, fighter):
        next_loc = self.next_loc()
        next_rect = pg.Rect(next_loc, self.rect)

        return next_rect.colliderect(fighter.make_rect())

    def check_gravity(self, screen_height):
        """
        called on every frame. determines whether or not the player should be falling
        :param screen_height: height of screen in pixels
        """
        if self.loc[1] + self.rect[1] > screen_height - self.rect[1]/3-10: # TODO - Add constant variable here
            self.loc[1] = screen_height - self.rect[1] + 1 - self.rect[1]/3-10
            if Action.falling in self.actions:
                self.remove_action(Action.falling)
        else:
            self.add_action(Action.falling)

    def be_victorious(self):
        self.gg = True
        self.rect = (200, 360)
        self.loc = [750, 200]
        self.update_action(Action.victory)
        new_spites = []
        for sprite in self.current_sprite_list:
            new_spites += [pg.transform.scale(sprite, self.rect)]
        self.current_sprite_list = new_spites

    def is_dead(self):
        return self.hp <= 0

    def be_dead(self):
        self.gg = True
        self.update_action(Action.damaged)
        self.update_frames = 120

    def check_walls(self, screen_width):
        next_loc = self.next_loc()
        if next_loc[0] < 0 or next_loc[0] + self.rect[0] > screen_width:
            self.stop()

    def remove_action(self, action):
        """
        removes action from self.actions
        :param action: to be removed
        """
        if action not in self.actions:
            return
        old_actions = self.actions
        self.actions = []
        if action in old_actions:
            for a in old_actions:
                if a != action:
                    self.actions += [a]

        if not self.actions:
            self.actions = Action.actor_idle

    def add_action(self, action):
        """
        adds action to list
        :param action: to be added
        :return:
        """
        if action in self.actions:
            return
        elif self.actions == Action.actor_idle:
            self.actions = [action]
        elif action == Action.idle:
            self.actions = Action.actor_idle
        elif action not in self.actions:
            self.actions += [action]