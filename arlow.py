import pygame
import random
import sys

pygame.init()

window_width = 600
window_height = 600
window = pygame.display.set_mode((window_width,window_height))
pygame.display.set_caption("Arlow")
running = True
fps = 60
clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT,100)
cell_size = 30
num_cells_x = window_width // cell_size
num_cells_y = window_height // cell_size
pygame.mouse.set_visible(False)
joysticks = []
icon_image = pygame.image.load("icon.ico")
pygame.display.set_icon(icon_image)
window_cell_y = 3
window_stroke_width = 4
window_y = window_cell_y * cell_size

def draw_text(text,x,y,size):
    font = pygame.font.Font("Fonts/retro.ttf",size)
    text_image = font.render(text,True,(100,100,100))
    text_rect = text_image.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    window.blit(text_image,text_rect)

class HungerBar():
    def __init__(self):
        self.hunger = 150
        self.start_hunger = self.hunger
        self.bar_length = 100
        self.bar_height = 20
        self.fill = (self.hunger / self.start_hunger) * self.bar_length
        self.fill_bar = pygame.Rect(200,50,self.fill,self.bar_height)
        self.x = 410
        self.y = 40
        self.hunger_text_x = 460
        self.hunger_text_y = 25
        self.background_bar = pygame.Rect(self.x,self.y,self.bar_length,self.bar_height)
        self.hunger_threshold = 0
        self.eat_amount = 15
        self.refill_amount = 0.4
        self.refill = False

    def update(self):
        if self.hunger <= self.hunger_threshold:
            self.refill = True
        if self.refill:
            self.hunger += self.refill_amount
            if self.hunger > self.start_hunger:
                self.hunger = self.start_hunger
                self.refill = False
        self.fill = (self.hunger / self.start_hunger) * self.bar_length
        self.fill_bar = pygame.Rect(self.x,self.y,self.fill,self.bar_height)

    def draw(self):
        draw_text("Hunger",self.hunger_text_x,self.hunger_text_y,15)
        pygame.draw.rect(window,(179,186,117),self.background_bar,border_radius=3)
        pygame.draw.rect(window,(100,100,100),self.fill_bar,border_radius=3)

class Apple():
    def __init__(self,snake):
        random_pos = self.gen_random_pos()
        in_body = False
        for body_part in snake.body:
            if body_part.x == random_pos[0] and body_part.y == random_pos[1]:
                in_body = True
                break
        while in_body:
            random_pos = self.gen_random_pos()
            for body_part in snake.body:
                if body_part.x == random_pos[0] and body_part.y == random_pos[1]:
                    in_body = True
                    break
            in_body = False
        self.growth = 6
        self.rect = pygame.Rect(random_pos[0]*cell_size,random_pos[1]*cell_size,0,0)
        self.grid_rect = pygame.Rect(random_pos[0]*cell_size,random_pos[1]*cell_size,cell_size,cell_size)
        
    def gen_random_pos(self):
        random_x = random.randint(0,num_cells_x-1)
        random_y = random.randint(window_cell_y,num_cells_y-1)
        return (random_x,random_y)

    def change_size(self):
        self.rect.width += self.growth
        self.rect.height += self.growth
        if self.rect.width < 0:
            self.growth = 6
        elif self.rect.width > cell_size:
            self.growth = -6
        center = self.grid_rect.center
        if self.rect.width >= cell_size and self.rect.height >= cell_size:
            self.rect.width = cell_size
            self.rect.height = cell_size
        self.rect.center = center

    def update(self):
        self.change_size()

    def draw(self):
        pygame.draw.rect(window,(100,100,100),pygame.Rect(self.rect),border_radius=6,width=10)
    
class Snake():
    def __init__(self):
        self.reset()
        self.eat_sound = pygame.mixer.Sound("Sounds/eat sound.ogg")
        self.lose_sound = pygame.mixer.Sound("Sounds/lose sound.mp3")

    def reset(self):
        self.hunger_bar = HungerBar()
        self.score = 0
        self.body = [pygame.Vector2(4,5),pygame.Vector2(3,5),pygame.Vector2(2,5)]
        self.direction = pygame.Vector2(1,0)
        self.apple = Apple(self)

    def handle_keyboard_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.direction != pygame.Vector2(0,1):
            self.direction = pygame.Vector2(0,-1)
        elif keys[pygame.K_s] and self.direction != pygame.Vector2(0,-1):
            self.direction = pygame.Vector2(0,1)
        elif keys[pygame.K_d] and self.direction != pygame.Vector2(-1,0):
            self.direction = pygame.Vector2(1,0)
        elif keys[pygame.K_a] and self.direction != pygame.Vector2(1,0):
            self.direction = pygame.Vector2(-1,0)

    def handle_controller_input(self):
        for joystick in joysticks:
            horizontal = joystick.get_axis(0)
            vertical = joystick.get_axis(1)
            if horizontal < -0.4 and self.direction != pygame.Vector2(1,0):
                self.direction = pygame.Vector2(-1,0)
            elif horizontal > 0.4 and self.direction != pygame.Vector2(-1,0):
                self.direction = pygame.Vector2(1,0)
            elif vertical < -0.4 and self.direction != pygame.Vector2(0,1):
                self.direction = pygame.Vector2(0,-1)
            elif vertical > 0.4 and self.direction != pygame.Vector2(0,-1):
                self.direction = pygame.Vector2(0,1)

    def collide_with_walls(self,head):
        if head.x < 0 or head.x > num_cells_x-1:
            self.reset()
            self.lose_sound.play()
        if head.y <= window_cell_y-1 or head.y > num_cells_y-1:
            self.reset()
            self.lose_sound.play()

    def collide_with_apple(self,head):
        if head.x*cell_size == self.apple.grid_rect.x and head.y*cell_size == self.apple.grid_rect.y:
            self.apple = Apple(self)
            if not self.hunger_bar.refill:
                self.hunger_bar.hunger -= self.hunger_bar.eat_amount
                self.score += 1
                self.eat_sound.play()
            if head.y != window_cell_y and head.y != num_cells_y-1 and head.x != 0 and head.x != num_cells_x-1:
                self.body.insert(0,self.body[0]+self.direction)

    def collide_with_body(self,head):
        for body_part in self.body[1:len(self.body)]:
            if head.x == body_part.x and head.y == body_part.y:
                self.reset()
                self.lose_sound.play()

    def move(self):
        self.body = self.body[:-1]
        self.body.insert(0,self.body[0]+self.direction)
        
    def update(self):
        self.handle_keyboard_input()
        self.handle_controller_input()
        self.apple.update()
        self.move()
        head = self.body[0]
        self.collide_with_body(head)
        self.collide_with_apple(head)
        self.collide_with_walls(head)

    def draw(self):
        for body_part in self.body:
            pygame.draw.rect(window,(100,100,100),pygame.Rect(body_part.x*cell_size,body_part.y*cell_size,cell_size,cell_size),border_radius=6,width=12)
        self.apple.draw()
        self.hunger_bar.draw()

arlow = Snake()

while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joystick)
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            arlow.update()
    window.fill((219,227,143))
    pygame.draw.line(window,(100,100,100),(0,window_y),(window_width,window_y),width=window_stroke_width)
    arlow.hunger_bar.update()
    arlow.draw()
    draw_text("Score: "+str(arlow.score),290,30,19)
    pygame.display.update()
pygame.quit()
sys.exit()
