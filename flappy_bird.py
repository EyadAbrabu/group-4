
import pygame
from pygame.locals import *
import random
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

menu = 0
playing = 1
game_over = 2
paused = 3

game_state = menu

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

score = 0
font = pygame.font.SysFont('Arial', 60)
font_small = pygame.font.SysFont('Arial', 40)

jump_fx = pygame.mixer.Sound(os.path.join('sound', 'jump.wav'))
point_fx = pygame.mixer.Sound(os.path.join('sound', 'point.wav')) #
collision_fx = pygame.mixer.Sound(os.path.join('sound', 'collision.wav'))

# Variables
ground_scroll = 0
scroll_speed = 4
pipe_frequency = 1500  
last_pipe = pygame.time.get_ticks() - pipe_frequency
pipe_gap = 200

# images
bg = pygame.image.load('img/bg.png')
bg = pygame.transform.scale(bg, (screen_width, screen_height))

ground_img = pygame.image.load('img/ground.png')
ground_img = pygame.transform.scale(ground_img, (screen_width, ground_img.get_height()))

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/bird.png').convert_alpha()  


        bird_width = 80  
        bird_height = 80  
        self.image = pygame.transform.scale(self.image, (bird_width, bird_height))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0

    def update(self):
        self.vel+= 0.5
        if self.vel > 6:
            self.vel = 6
        self.rect.y += int(self.vel)
        # top and bottom boundaries
        if self.rect.top < 0:  
            self.rect.top = 0
        if self.rect.bottom > 680:  
            self.rect.bottom = 680
            return True 
       

        return False  
    


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png').convert_alpha()
        pipe_width = 80
        pipe_height = screen_height
        self.image = pygame.transform.scale(self.image, (pipe_width, pipe_height))
        self.rect = self.image.get_rect()

        self.position = position
        self.passed = False

        # pipes top or bottom
        if position == 1:  # Bottom pipe
            self.rect.topleft = (x, y)
        elif position == -1:  # Top pipe
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:  # remove pipes
            self.kill()

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(150, int(screen_height / 2))
bird_group.add(flappy)

def reset_game():
    global score, last_pipe
    pipe_group.empty()                       
    flappy.rect.center = [150, screen_height // 2]  
    flappy.vel = 0
    score = 0                                      
    last_pipe = pygame.time.get_ticks() - pipe_frequency

#game loop
run = True
while run:
    clock.tick(fps)

    if game_state == menu:
    
        screen.blit(bg, (0, 0))

        bird_group.draw(screen)

        start_text = font_small.render("Click to Start", True, (255, 255, 255))
        screen.blit(start_text, (
            screen_width // 2 - start_text.get_width() // 2,
            screen_height // 2 - start_text.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        
                game_state = playing

        pygame.display.update()
        continue
    elif game_state == playing:
        
        screen.blit(bg, (0, 0))
        bird_group.draw(screen)
        if flappy.update(): 
            collision_fx.play()  
            game_state = game_over
        

        pipe_group.draw(screen)
        pipe_group.update()
    
        screen.blit(ground_img, (ground_scroll, 680))  
        screen.blit(ground_img, (ground_scroll + screen_width, 680))  
        ground_scroll -= scroll_speed


        if abs(ground_scroll) >= screen_width:
            ground_scroll = 0

    # pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height + pipe_gap // 2, 1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height - pipe_gap // 2, -1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
    # score
        for pipe in pipe_group:
            if pipe.position == 1 and not pipe.passed:
                if flappy.rect.left > pipe.rect.right:
                    pipe.passed = True
                    score += 1
                    point_fx.play()

    # check for collisions
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
            collision_fx.play()
            game_state = game_over
         
        
        score_text = font.render(str(score), True, (255, 255, 255))
        screen.blit(score_text, (screen_width // 2, 20)) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            #jumping
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    flappy.vel = -8
                    jump_fx.play()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_state = paused

        pygame.display.update()

    elif game_state == paused:
        
        screen.blit(bg, (0, 0))
        bird_group.draw(screen)
        pipe_group.draw(screen)
        screen.blit(ground_img, (ground_scroll, 680))
        screen.blit(ground_img, (ground_scroll + screen_width, 680))

        
        pause_text = font.render("PAUSED", True, (255, 255, 0))
        screen.blit(
            pause_text,
                (screen_width // 2 - pause_text.get_width() // 2,
                screen_height // 2 - pause_text.get_height() // 2))
        
        resume_text = font_small.render("Press 'P' to Resume", True, (255, 255, 255))
        screen.blit(
            resume_text,
                (screen_width // 2 - resume_text.get_width() // 2,
                screen_height // 2 + 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_state = playing

        pygame.display.update()

    elif game_state == game_over:
    
        screen.blit(bg, (0, 0))
        bird_group.draw(screen)
        pipe_group.draw(screen)
    
        screen.blit(ground_img, (ground_scroll, 680))
        screen.blit(ground_img, (ground_scroll + screen_width, 680))
    
        over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(over_text, (screen_width // 2 - over_text.get_width() // 2,
            screen_height // 2 - over_text.get_height() // 2))

        final_score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2,
            screen_height // 2 + 60))

        restart_text = font_small.render("Click to Restart", True, (255, 255, 255))
        screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2,
            screen_height // 2 + 120))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                reset_game()
                game_state = menu

    pygame.display.update()

pygame.quit()
