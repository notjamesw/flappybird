# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 22:02:40 2021

@author: Leran-James Wen
"""

from tkinter import S
import pickle
import pygame
import neat
import random
import time
import os
pygame.init()

WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird3.png")))]

WALL_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images","wall.png")))

BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base.png")))

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images","bg.png")))

END_IMG = pygame.image.load(os.path.join("images", "endscreen.jpg"))

SCORE_FONT = pygame.font.SysFont("georgia", 50)

filename = "genome_pickle"

# bird object
class Bird:
    imgs = BIRD_IMGS
    max_rotation = 25
    rotation_vel = 20
    animation_time = 5

    def __init__ (self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.imgs[0]

    def flap(self):
        if self.y > self.img.get_height():
            self.vel = -8
            self.tick_count = 0
            self.height = self.y

    def move(self):
        self.tick_count+=1

        d = self.vel*self.tick_count + 1.2*self.tick_count**2

        if d >= 16:
            d = 15
        if d < 0:
            d -= 2
        
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rotation_vel
    
    def draw(self, win):
        self.img_count += 1
        i = 0
        if self.img_count < 5:#self.animation_time:
            i = 0
        elif self.img_count < 10:#self.animation_time *2:
            i = 1
        elif self.img_count < 15: #self.animation_time *3:
            i = 2
        elif self.img_count < 20: #self.animation_time *4:
            i = 1
        elif self.img_count == 20: #self.animation_time*4+1:
            i = 0
            self.img_count = 0
        
        self.img = self.imgs[i]

        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.img_count = self.animation_time*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# wall/pipe object
class Wall:
    gap = 200
    vel = 5

    def __init__ (self, x):
        self.x = x
        self.height = 0
        self.gap = 200

        self.top = 0
        self.bottom = 0
        self.wall_top = pygame.transform.flip(WALL_IMG, False, True)
        self.wall_bottom = WALL_IMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.wall_top.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -=  self.vel
    
    def draw(self, win):
        win.blit(self.wall_top, (self.x, self.top))
        win.blit(self.wall_bottom, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.wall_top)
        bottom_mask = pygame.mask.from_surface(self.wall_bottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset  = (self.x - bird.x, self.bottom - round(bird.y))

        bb_point = bird_mask.overlap(bottom_mask, bottom_offset)
        bt_point = bird_mask.overlap(top_mask, top_offset)

        if bb_point or bt_point:
            return True        
        return False

# base object
class Base:
    vel = 5
    width = BASE_IMG.get_width()
    img = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width
    
    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))

    def collide(self, bird):
        if bird.y + bird.img.get_height() >= 680 or bird.y < 0:
            return True
        return False

# function for drawing the game window for one bird. 
# Can be refactored to combine with draw_window_AI option
def draw_window(win, bird, walls, base, score):
    win.blit(BG_IMG, (0,0))
    for wall in walls:
        wall.draw(win)
    
    text = SCORE_FONT.render("Score: " + str(score), 1 , (255, 255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)

    bird.draw(win)
    pygame.display.update()

# function for drawing the game window for multiple birds
# used for the training AI option
def draw_window_AI(win, birds, walls, base, score):
    win.blit(BG_IMG, (0,0))
    for wall in walls:
        wall.draw(win)
    
    text = SCORE_FONT.render("Score: " + str(score), 1 , (255, 255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()
    
# function for the start screen for the human option.
def draw_start(win):
    win.blit(BG_IMG, (0,0))
    start = False
    text = SCORE_FONT.render("Click anywhere to start", 1, (255,255,255))
    win.blit(text, (WIN_WIDTH/2 - text.get_width()/2, WIN_HEIGHT/2))

    pygame.display.update()
    while not start:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
            elif event.type == pygame.QUIT:
                return False


# function for the human/player option
def human():  
    bird = Bird(210,330)
    base = Base(680)
    walls = [Wall(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    run = draw_start(win)
    Wall.vel = 5
    Base.vel = 5
    speed_up = True
    
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif ((event.type == pygame.KEYDOWN 
                   and event.key == pygame.K_SPACE) 
                  or event.type == pygame.MOUSEBUTTONDOWN):
                bird.flap()
                
        bird.move()
        add_wall = False
        rem = []
        for wall in walls:
            if wall.collide(bird):
                run = False
            if wall.x + wall.wall_top.get_width() < 0:
                rem.append(wall)
            if not wall.passed and wall.x < bird.x:
                wall.passed = True
                add_wall = True
            
            wall.move()
        
        if add_wall:
            score += 1
            speed_up = True
            walls.append(Wall(600))
        for r in rem:
            walls.remove(r)

        if base.collide(bird):
            run = False

        draw_window(win, bird, walls, base, score)
        base.move()

        if score > 0 and score % 10 == 0 and speed_up:
            Wall.vel += 1
            Base.vel += 1
            speed_up = False
    game_over(win, score)

# function for the game over screen. 
def game_over(win, score):
    pygame.display.quit()
    win1 = pygame.display.set_mode((1280, 720))
    WIN_WIDTH = 1280
    WIN_HEIGHT = 720
    win1.blit(END_IMG, (0,0))
    text1 = SCORE_FONT.render("GAME OVER.", 1, (255,255,255))
    text2 = SCORE_FONT.render("Your Final Score Is: " + str(score), 1, (255, 255,255))
    win1.blit(text1, (WIN_WIDTH/2 - text1.get_width()/2, WIN_HEIGHT/2 - 50))
    win1.blit(text2, (WIN_WIDTH/2 - text2.get_width()/2, WIN_HEIGHT/2 + 50))
    
    x = True

    pygame.display.update()
    while x:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                x = False
                pygame.display.quit()
                pygame.QUIT

# function for training the AI and displaying the game state. 
def bot_t(genomes, config):
    birds = []
    nets = []
    ge = []

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(210,330))
        g.fitness = 0
        ge.append(g)

    base = Base(680)
    walls = [Wall(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0
    Wall.vel = 5
    Base.vel = 5
    speed_up = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.QUIT

        wall_index = 0
        if len(birds) > 0:
            if (len(walls) > 1 and 
                birds[0].x > walls[0].x + walls[0].wall_top.get_width()):
                wall_index = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - walls[wall_index].height), 
              abs(bird.y - walls[wall_index].bottom), Wall.vel))
            
            if output[0] > 0.5:
                bird.flap()
        
        add_wall = False
        rem = []
        for wall in walls:
            for x, bird in enumerate(birds):
                if wall.collide(bird):
                    ge[x].fitness -= 5
                    nets.pop(x)
                    ge.pop(x)
                    birds.pop(x)

                if not wall.passed and wall.x < bird.x:
                    wall.passed = True
                    add_wall = True

            if wall.x + wall.wall_top.get_width() < 0:
                    rem.append(wall)

            wall.move()
        
        if add_wall:
            score += 1
            speed_up = True
            for g in ge: 
                g.fitness += 5
            walls.append(Wall(600))
        for r in rem:
            walls.remove(r)

        for x, bird in enumerate(birds):
            if base.collide(bird):
                ge[x].fitness -= 5
                nets.pop(x)
                ge.pop(x)
                birds.pop(x)

        draw_window_AI(win, birds, walls, base, score)
        base.move()
        
        if score > 0 and score % 10 == 0 and speed_up:
            Wall.vel += 1
            Base.vel += 1
            speed_up = False

# function for running the loaded genome in a game. 
def bot_r(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    bird = Bird(210,330)
    
    base = Base(680)
    walls = [Wall(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0
    Wall.vel = 5
    Base.vel = 5
    speed_up = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        wall_index = 0
        if (len(walls) > 1 
            and bird.x > walls[0].x + walls[0].wall_top.get_width()):
            wall_index = 1

        bird.move()
        output = net.activate((bird.y, abs(bird.y - walls[wall_index].height), 
          abs(bird.y - walls[wall_index].bottom), Wall.vel))
        if output[0] > 0.5:
            bird.flap()
        
        add_wall = False
        rem = []
        for wall in walls:
            if wall.collide(bird):
                run = False

            if not wall.passed and wall.x < bird.x:
                wall.passed = True
                add_wall = True

            if wall.x + wall.wall_top.get_width() < 0:
                rem.append(wall)

            wall.move()
        
        if add_wall:
            score += 1
            speed_up = True
            walls.append(Wall(600))
        for r in rem:
            walls.remove(r)

        if base.collide(bird):
            run = False

        draw_window(win,bird, walls, base, score)
        base.move()
        
        if score > 0 and score % 10 == 0 and speed_up:
            Wall.vel += 1
            Base.vel += 1
            speed_up = False
            
    game_over(win, score)

# main function
# !!! todo: add additional feature for leaderboard (highest score) and
# for pausing game and restarting game. 
def start(): 
    #function loops while 1 is not entered in the console. 
    
    endprogram = 0
    while endprogram == 0:
        print("AI or human?")
        print("Enter 1 to end program")
        x = input()

        while x != "human" and x != "AI" and x != "1":
            x = input()
    
        if x == "human":      #human or AI option
            human()
        elif x == "1":
            endprogram = 1
        else:
            print("Option 1. Load AI")
            print("Option 2. Train AI")
            y = input()
            if y == "1":
                print("AI working")
                loadAI()
            elif y == "2":
                print("Training AI")
                trainAI()


# function for initializing the training and serializing the result genome 
# (aka the best genome) into genome_pickle file once it has passed the 
# fitness threshold.
def trainAI(): 
    #config for trainAI
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
     neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    #reporter gives statistics for the previous training state.
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    strongest = p.run(bot_t, 20)
    
    pygame.display.quit()
    pickle_out = open(filename, 'wb')
    pickle.dump(strongest, pickle_out) 
    pickle_out.close()

# function for initializing the genome stored in genome_pickle file by 
# deserializing the file. 
# !!! todo: If there is no stored genome, an error is indicated.
def loadAI():
    # config for loadAI is slightly different than the config for training
    # the AI. 
    pickle_in = open(filename, 'rb')
    trained = pickle.load(pickle_in)
    pickle_in.close()
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
     neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path_trained)
    
    ## can use the same method to train the AI to run the trained AI. 
    ## genomes = [(1, trained)]
    ## bot_t(genomes, config)
    bot_r(trained, config)

#finds the config files for trainAI and loadAI. 

local_dir = os.path.realpath(os.path.join(os.getcwd(), 
                                          os.path.dirname("flappygame.py")))
config_path = os.path.join(local_dir, "config.txt")
config_path_trained = os.path.join(local_dir, "configTrained.txt")

# begins the main program. 
start()
pygame.quit()

