import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1500, 1000
FPS = 60
PLAYER_VEL = 5
FONT = pygame.font.SysFont("sans", 12)
     

window = pygame.display.set_mode((WIDTH, HEIGHT))
player_skin = "PinkMan"

#Pause menu stuff
pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
#------------------------------

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]
    
    all_sprites = {}
    
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
            
        if direction:
            all_sprites[image.replace(".png", "" + "_right")] = sprites
            all_sprites[image.replace(".png", "" + "_left")] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
            
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

        
class Player(pygame.sprite.Sprite):
    PINKMAN = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    MASKDUDE = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    NINJAFROG = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    VIRTUALGUY = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)

    COLOR = (255, 0, 0)
    GRAVITY = 1
    #SPRITES = load_sprite_sheets("MainCharacters", player_skin, 32, 32, True]
    SPRITES = [PINKMAN, MASKDUDE, NINJAFROG, VIRTUALGUY]
    SPAWN = load_sprite_sheets("MainCharacters", "Appear", 96,96, False)
    ANIMATION_DELAY = 3
    SPAWN_ANIMATION_DELAY = 7
    
       
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.character = 0
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.spawning = True
        
        
        print(self.SPAWN.keys())
        self.appear = load_sprite_sheets("MainCharacters", "Appear", 96, 96)
        
    def change_character(self):
        if self.character < 3:
            self.character += 1
        else:
            self.character = 0
            
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
        
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
            

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        
        self.fall_count += 1
        self.update_sprite()
        
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1
        
    def update_sprite(self):     
        sprite_sheet = "idle"
        if self.spawning:
            count = 0
            sprite_sheet_name = "Appearing"
            sprites = self.SPAWN[sprite_sheet_name]
            sprite_index = (self.animation_count // self.SPAWN_ANIMATION_DELAY) % len(sprites)
            self.y_vel = 0
            self.fall_count = 0
            if sprite_index == len(sprites) - 1:
                self.spawning = False
                self.animation_count = 0
            else:
                self.sprite = sprites[sprite_index]
                self.animation_count += 1
                count += 1
                self.y_vel = 0
                self.update()
                return
        elif self.hit and not self.spawning: 
            sprite_sheet = "hit"
        elif self.y_vel < 0 and not self.spawning:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2 and not self.spawning:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2 and not self.spawning:
            sprite_sheet = "fall"
        elif self.x_vel != 0 and not self.spawning:
            sprite_sheet = "run"
        if not self.spawning:    
            sprite_sheet_name = sprite_sheet + "_" + self.direction
            sprites = self.SPRITES[self.character][sprite_sheet_name]
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        sprite_sheet = "idle"
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
        
    def draw(self, win, offset_x, offset_y):
        if self.spawning:
            win.blit(self.sprite, (self.rect.x - offset_x  - 62, self.rect.y - offset_y -72))
        else:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
        
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
        
    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
        
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
    
class Fire(Object):
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["on"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"
        
    def on(self):
        self.animation_name = "on"
        
    def off(self):
        self.animation_name = "off"
        
    def loop(self):
        sprites = self.fire[self.animation_name] 
        if len(sprites) > 1:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
            self.image = sprites[sprite_index]
            self.animation_count += 1
        
            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
            self.mask = pygame.mask.from_surface(self.image)
        
            if self.animation_count // self.ANIMATION_DELAY > len(sprites):
                self.animation_count = 0
            
        self.update()
        

          
        
def get_background():
    image = pygame.image.load(join("assets", "Background", "nature_1", "origbig.png"))
    __, __, width, height = image.get_rect()
    return image
   
            

def draw(window, bg_image, player, objects, offset_x, offset_y):
    window.blit(bg_image, (0,0))
        
    for obj in objects:
        obj.draw(window, offset_x, offset_y)
    
    player.draw(window, offset_x, offset_y)
    
    pygame.display.update()
    
def draw_pause():
    pygame.draw.rect(pause_surface, (128, 128, 128, 150), [0, 0, WIDTH, HEIGHT])
    pygame.draw.rect(pause_surface, ('yellow'), [200, 150, 600, 50])
    reset = pygame.draw.rect(pause_surface, ('green'), [200, 220, 280, 50])
    save = pygame.draw.rect(pause_surface, ('green'), [520, 220, 280, 50])
    quit = pygame.draw.rect(pause_surface, ('red'), [200, 290, 600, 50])
    pause_surface.blit(FONT.render('Game paused: press esc to resume', True, 'black'), (220, 160))
    pause_surface.blit(FONT.render('Restart', True, 'black'), (220, 230))
    pause_surface.blit(FONT.render('Save', True, 'black'), (540, 230))
    pause_surface.blit(FONT.render('Quit', True, 'black'), (220, 300))
    window.blit(pause_surface, (0, 0))
    pygame.display.update()
    return reset, save, quit    
        
    
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
                
            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
        
    player.move(-dx, 0)
    player.update()
    return collided_object
            
def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
  
def draw_platforms(y, start, stop):
    block_size = 96
    list = [Block(i * block_size, HEIGHT - block_size * y, block_size) for i in range(start, stop)]
    return list

def draw_walls(x, start, stop):
    block_size = 96
    list = [Block(block_size * x, HEIGHT - block_size * i, block_size) for i in range(start, stop)]
    return list


def main(window):
    clock = pygame.time.Clock()
    bg_image = get_background()
    pause = False
    block_size = 96
     
    player = Player(250, HEIGHT - block_size * 2, 50, 50)
    fire = Fire(450, HEIGHT - block_size -64, 16, 32)
    fire.on()
    
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 5 // block_size)]
    
    platform1 = draw_platforms(5, 1, 5)
    
    wall1 = draw_walls(5, 2, 6)
    wall2 = draw_walls(-3, 2, 5)
    wall3 = draw_walls(-4, 2, 4)
    wall4 = draw_walls(-5, 2, 3) 
    
    objects = [*wall1, *wall2, *wall3, *wall4, *platform1, *floor, Block(0, HEIGHT - block_size * 5, block_size), Block(0, HEIGHT - block_size * 4, block_size), Block(0, HEIGHT - block_size *2, block_size), fire]
    
    offset_x = 0
    offset_y = 0
    scroll_area_width = 200
    scroll_area_height = 250

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player.change_character()
                if event.key == pygame.K_x:
                    player = Player(100, 100, 50, 50)
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    if pause: 
                        pause = False
                    else:
                        pause = True
                    
            if event.type == pygame.MOUSEBUTTONDOWN and pause:
                if restart.collidepoint(event.pos):
                    player = Player(250, HEIGHT - block_size * 2, 50, 50)
                    offset_x = 0
                    offset_y = 0
                    pause = False
                elif saves.collidepoint(event.pos):
                    pause = False
                elif quit.collidepoint(event.pos):
                    run = False
                           
                    
        if not pause:
            player.loop(FPS)
            handle_move(player, objects)
            fire.loop()
            handle_move(player, objects)
        else:
            restart, saves, quit = draw_pause()
        if not pause:
            pygame.display.update()
            draw(window, bg_image, player, objects, offset_x, offset_y)
        
        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left -offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
            
        if((player.rect.top - offset_y >= HEIGHT - scroll_area_height) and player.y_vel > 0) or ((player.rect.bottom - offset_y <= scroll_area_height) and player.y_vel < 0):
            offset_y += player.y_vel

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)