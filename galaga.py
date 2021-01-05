import pygame as pg
import os
import time
import random

# Needed to use fonts in the game and usually initialized at the top
pg.font.init()

# Create game window/title
width, height = 700, 700
window = pg.display.set_mode((width, height))
pg.display.set_caption('Galaga Shooter')

# Loading images, takes the arguments of folder and the image
# Enemy_ships ships
red_ship = pg.image.load(os.path.join('assets', 'red_ship.png'))
blue_ship = pg.image.load(os.path.join('assets', 'blue_ship.png'))
green_ship = pg.image.load(os.path.join('assets', 'green_ship.png'))

# Main ship
yellow_main_ship = pg.image.load(os.path.join('assets', 'yellow_main_ship.png'))

# Enemy_ships lasers
red_laser = pg.image.load(os.path.join('assets', 'red_laser.png'))
blue_laser = pg.image.load(os.path.join('assets', 'blue_laser.png'))
green_laser = pg.image.load(os.path.join('assets', 'green_laser.png'))

# Main ship laser
yellow_laser = pg.image.load(os.path.join('assets', 'yellow_laser.png'))

# Background
# We use transform to scale the image as it was orginally: "background = pg.image.load(os.path.join('assets', 'background.png'))"
background = pg.transform.scale(pg.image.load(os.path.join('assets', 'background.png')), (width, height))

class Laser_class():
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pg.mask.from_surface(self.img)

    def draw_the_laser(self, window):
        window.blit(self.img, (self.x, self.y))

    def move_enemy(self, vel):
        self.y += vel

    # Used to remove the laser if it is off the screen
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        # Self is referring to the laser and obj is any object the laser hits
        return colliding(self, obj)

# The offset tells us the distance between the top left-hand corners of...
# two objects in terms of collision; this tells us if objects have collided
def colliding(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    # Returns the point of intersection at which the objects overlap or collide...
    # either True of False
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Ship_class():
    # Half a second cooldown
    cd = 30

    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        # We initialize these images for later usage
        self.ship_image = None
        self.laser_image = None
        # Collects the amount of lasers shot
        self.lasers = []
        # Initialized counter to make sure the player cannot spam lasers
        self.firing_counter = 0

    def draw_ships(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw_the_laser(window)

    # We have "objs" to check collision with another object
    # This "obj" refers to the player, so the enemy is shooting the player
    def ships_moving_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move_enemy(vel)
            # If the laser is no longer on the screen, we will remove it
            if laser.off_screen(height):
                self.lasers.remove(laser)
            # If the laser collides with an object, the object will lose hp and the laser will be removed
            elif laser.collision(obj):
                obj.hp -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        # If firing counter is greater than the time limit, we do not do anything
        if self.firing_counter >= Ship_class.cd:
            self.firing_counter = 0
        # Elif firing counter is bigger than 0, keep incrementing firing counter by 1
        elif self.firing_counter > 0:
            self.firing_counter += 1

    def shoot(self):
        # If the firing counter is 0, create a laser image, append it to the list...
        # and set the firing counter to 1
        if self.firing_counter == 0:
            laser = Laser_class(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.firing_counter = 1

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()


class Main_ship(Ship_class):
    # This init takes the same arguments of the parents class IN ADDITION to new arguments
    def __init__(self, x, y, hp=100):
        # Form for multiple inheritance and the arguments in init are same as parent class
        Ship_class.__init__(self, x, y, hp)
        self.ship_image = yellow_main_ship
        self.laser_image = yellow_laser
        self.max_hp = hp
        # We define a mask to ensure each collision in the game is "pixel-perfect"
        self.mask = pg.mask.from_surface(self.ship_image)

    # Checking is player's lasers have hit the enemy so "objs" is the list of enemies
    def player_move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move_enemy(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def pship_and_health(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw_the_laser(window)
        self.healthbar(window)

    def healthbar(self, window):
        pg.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pg.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width() * (self.hp/self.max_hp), 10))


class Enemy_ships(Ship_class):
    mapping = {
                'red': (red_ship, red_laser),
                'green': (green_ship, green_laser),
                'blue': (blue_ship, blue_laser)
                }

    # Remember if that you typed "def __init__(self, x, y, hp=200, color)" calling the instance...
    # object would cause an error because hp is before color
    def __init__(self, x, y, color, hp=100):
        Ship_class.__init__(self, x, y, hp)
        # Obtains the enemy ship color and color of laser using dictionary created above
        self.ship_image, self.laser_image = self.mapping[color]
        self.mask = pg.mask.from_surface(self.ship_image)

    # Since the enemy ships are moving downwards
    def move_enemy(self, vel):
        self.y += vel

    def enemy_shooting(self):
        # If the firing counter is 0, create a laser image, append it to the list...
        # and set the firing counter to 1
        if self.firing_counter == 0:
            # Shoot method for the enemy to make sure the laser shot is in the middle...
            # which is why we have "-15"
            laser = Laser_class(self.x - 15, self.y, self.laser_image)
            self.lasers.append(laser)
            self.firing_counter = 1

# Pygame requires a mainloop to handle all events in the game
# Everything int he mainloop block before the while loop includes all the defined variables
def mainloop():
    running = True
    frames = 60
    level = 0
    lives = 5
    # Creates the font which will be used in "font.render" command
    main_font = pg.font.SysFont('arial', 30)
    lost_font = pg.font.SysFont('arial', 50)

    lost = False
    loss_count = 0

    enemies = []
    wave_length = 10
    enemy_velocity = 1

    yellow_main_ship_vel = 5
    laser_velocity = 6
    # Initiates the instance object of player ship
    player_ship = Main_ship(300, 580)
    # Initiates the clock
    clock = pg.time.Clock()

    while running:
        # Setting clock speed so game runs at the set amount of fps
        clock.tick(frames)

        # Updates the game
        pg.display.update()

        # Blit takes an image and draws it on the window location we assign it to
        window.blit(background, (0, 0))

        # You must create a label in order to display the words/font 
        # We also use the variable "font" defined above to call render
        lives_label = main_font.render('Lives: {}'.format(lives), 1, (255, 255, 255))
        level_label = main_font.render('Level: {}'.format(level), 1, (255, 255, 255))

        window.blit(lives_label, (10, 10))
        window.blit(level_label, (width - level_label.get_width() - 10, 10))

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            # Spawns the enemy ships on the screen
            for i in range(wave_length):
                # Random.choice() selects a random elements from a mutable object
                e_ships = Enemy_ships(random.randint(50, width - 100), random.randint(-1500, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(e_ships)

        for enemy in enemies:
            enemy.draw_ships(window)
            enemy.move_enemy(enemy_velocity)

        player_ship.pship_and_health(window)
        player_ship.player_move_laser(-laser_velocity, enemies)

        # You want to put this if clause before the if clause containing "lives" and "player_ship.hp" because...
        # you have to make sure the losing_label is printed before the game exits (running = False)
        if lost == True:
            losing_label = lost_font.render('You Lost!', True, (255, 255, 255))
            window.blit(losing_label, (width/2 - losing_label.get_width()/2, 350))

        if lives <= 0 or player_ship.hp <= 0:
            lost = True
            loss_count += 1
            # Frames * 3 is the three second timer
            if loss_count > frames:
                running = False
            else:
                # If we don't hit three seconds, the screen will stop and the game will exit...
                # after 3 seconds have gone by
                continue

        # We create a copy of the enemies list because we want to remove the enemies when they are off the screen...
        # and not making a copy can change the list size during iteration which is something we don't want
        for enemy in enemies[:]:
            # This is for when the enemy shoots the laser
            enemy.ships_moving_lasers(laser_velocity, player_ship)
            # 50% chance the enemies will shoot
            if random.randint(0, 2*frames) == 1:
                enemy.enemy_shooting()
            if colliding(enemy, player_ship):
                player_ship.hp -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                # Instead of "running = False," we type quit() to make sure the game...
                # closes when we press the X during the game
                quit()

        # This variable returns a dictionary and tells us if a key was pressed
        keys = pg.key.get_pressed()

        # We don't put this whole "if keys" block as part of the event loop is because...
        # we want the ship to move when we're holding the key down and doing so wouldn't happen...
        # and it allows for diagonal movement
        if keys[pg.K_w] and player_ship.y != yellow_main_ship_vel:
            player_ship.y -= yellow_main_ship_vel
        if keys[pg.K_a] and player_ship.x != yellow_main_ship_vel:
            player_ship.x -= yellow_main_ship_vel
        # Add 15 to make sure the healthbar doesn't go off the screen
        if keys[pg.K_s] and player_ship.y != height - (yellow_main_ship_vel + yellow_main_ship.get_height() + 15):
            player_ship.y += yellow_main_ship_vel
        if keys[pg.K_d] and player_ship.x != width - (yellow_main_ship_vel + yellow_main_ship.get_width()):
            player_ship.x += yellow_main_ship_vel
        if keys[pg.K_SPACE]:
            player_ship.shoot() 

def run_game():
    running = True
    title_font = pg.font.SysFont('arial', 60)
    while running:
        window.blit(background, (0, 0))
        title_label = title_font.render('Click to start the game...', True, (255, 255, 255))
        window.blit(title_label, (width/2 - title_label.get_width()/2, 350))
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            # Basically if you click on the screen, the game will start
            if event.type == pg.MOUSEBUTTONDOWN:
                mainloop()
    quit()

if __name__ == '__main__':
    run_game()