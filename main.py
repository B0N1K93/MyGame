import random

import os

import time

import math

import pygame
from pygame.constants import QUIT, K_DOWN, K_UP, K_LEFT, K_RIGHT, K_w, K_a, K_s, K_d, K_p, K_ESCAPE

pygame.init()

FPS = pygame.time.Clock()

HEIGHT = 800
WIDTH = 1200

FONT = pygame.font.SysFont('Verdana', round(WIDTH/30))
LARGE_TEXT = pygame.font.SysFont('Verdana', round(WIDTH/12))
SMALL_TEXT = pygame.font.SysFont('Verdana', round(WIDTH/45))

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)

main_display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Слава Україні!')

bg_move = 3
score = 0
level = 1
lives = 3
jumps : int
enemy_count : int
enemy_collisions : int
bonus_count : int
bonus_collected : int
max_score : int
extra_lives : int
extra_jumps : int
rage_count : int
rage_used_count : int

paused = False
game_end = False
control = False
intro = False
difficulty : str

game_icon = pygame.image.load('icon.png')
pygame.display.set_icon(game_icon)

crash_sound = pygame.mixer.Sound('explosion.wav')
pygame.mixer.Sound.set_volume(crash_sound, 0.25)
coin_sound = pygame.mixer.Sound('coin.wav')
pygame.mixer.Sound.set_volume(crash_sound, 0.75)
rage_sound = pygame.mixer.Sound('rage.wav')
pygame.mixer.Sound.set_volume(rage_sound, 1)

def game_exit():
    pygame.quit()
    quit()

def create_rage():
    global level, rage_count, difficulty
    rage = pygame.transform.scale(pygame.image.load('rage.png'), (WIDTH*0.05, WIDTH*0.05))
    rage_size = rage.get_size()
    rage_rect = pygame.Rect(random.randint(round(WIDTH*0.25), round(WIDTH*0.85)), random.randint(0, (HEIGHT - rage_size[1])), *rage_size)
    rage_count += 1
    match difficulty:
        case 'easy':
            rage_duration = random.randint(12500, 15000)
            rage_screen_time = random.randint(10500, 12000)
        case 'normal':
            rage_duration = random.randint(10000, 12500)
            rage_screen_time = random.randint(9000, 10500)
        case 'hard':
            rage_duration = random.randint(7500, 10000)
            rage_screen_time = random.randint(7500, 9000)
    return [rage, rage_rect, rage_duration, rage_screen_time]


def create_enemy():
    global level, bg_move, enemy_count
    # enemy_size = (30, 30)
    # enemy = pygame.Surface(enemy_size)
    # enemy.fill(COLOR_BLUE)
    enemy = pygame.image.load('enemy.png').convert_alpha()
    enemy_size = enemy.get_size()
    enemy_rect = pygame.Rect(WIDTH, random.randint(0, (HEIGHT - enemy_size[1])), *enemy_size)
    enemy_move = [random.randint(-4-bg_move-math.floor(level-1), -1-bg_move-math.floor(level-1)), 0]
    enemy_count += 1
    return [enemy, enemy_rect, enemy_move]

def create_bonus():
    global level, bg_move, bonus_count, max_score
    # bonus_size = (15, 15)
    # bonus = pygame.Surface(bonus_size)
    # bonus.fill(COLOR_GREEN)
    bonus = pygame.image.load('bonus.png').convert_alpha()
    bonus_size = bonus.get_size()
    score_list = [1, 2, 3, 4, 5]
    score_change = random.choice(score_list)
    if score_change == 1:
        new_bonus_size = (bonus_size[0], bonus_size[1])
        bonus_move = [0, random.randint(1+bg_move+math.floor(level/2), 2+bg_move+math.floor(level/2))]
    elif score_change == 2:
        new_bonus_size = (round(bonus_size[0]*0.8), round(bonus_size[1]*0.8))
        bonus_move = [0, random.randint(2+bg_move+math.floor(level/2), 3+bg_move+math.floor(level/2))]
    elif score_change == 3:
        new_bonus_size = (round(bonus_size[0]*0.6), round(bonus_size[1]*0.6))
        bonus_move = [0, random.randint(3+bg_move+math.floor(level/2), 4+bg_move+math.floor(level/2))]
    elif score_change == 4:
        new_bonus_size = (round(bonus_size[0]*0.4), round(bonus_size[1]*0.4))
        bonus_move = [0, random.randint(4+bg_move+math.floor(level/2), 5+bg_move+math.floor(level/2))]
    else:
        new_bonus_size = (round(bonus_size[0]*0.2), round(bonus_size[1]*0.2))
        bonus_move = [0, random.randint(5+bg_move+math.floor(level/2), 6+bg_move+math.floor(level/2))]
    bonus = pygame.transform.scale(bonus, new_bonus_size)
    bonus_rect = pygame.Rect(random.randint(0, (WIDTH - bonus_size[0])), 0, *new_bonus_size)
    score_change += math.floor(level/4)
    bonus_count += 1
    max_score += score_change
    return [bonus, bonus_rect, bonus_move, score_change]

def text_objects(text : str, font, color : tuple):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def message_display(text : str):
    TextSurf, TextRect = text_objects(text, LARGE_TEXT, COLOR_WHITE)
    TextRect.center = ((round(WIDTH/2)),(round(HEIGHT/2)))
    main_display.fill(COLOR_BLACK)
    main_display.blit(TextSurf, TextRect)

def text_line_display(text : str, height_coef : float):
    TextSurf, TextRect = text_objects(text, SMALL_TEXT, COLOR_WHITE)
    TextRect.center = ((round(WIDTH/2)),(round(HEIGHT*height_coef)))
    main_display.blit(TextSurf, TextRect)

def button(text : str, position : str, action = None):
    
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    textSurf, textRect = text_objects(text, SMALL_TEXT, COLOR_BLACK)
    if position == 'left':
        textRect.center = (round(WIDTH*0.25), round(HEIGHT*0.75))
        if round(WIDTH*(0.25-0.18/2)) <= mouse[0] <= round(WIDTH*(0.25+0.18/2)) and round(HEIGHT*(0.75-0.11/2)) <= mouse[1] <= round(HEIGHT*(0.75+0.11/2)):
            pygame.draw.rect(main_display, COLOR_YELLOW,(round(WIDTH*(0.25-0.18/2)), round(HEIGHT*(0.75-0.11/2)), round(WIDTH*0.18), round(HEIGHT*0.11)))
            if click[0] == 1 and action != None:
                action()
        else:
            pygame.draw.rect(main_display, COLOR_GREEN,(round(WIDTH*(0.25-0.18/2)), round(HEIGHT*(0.75-0.11/2)), round(WIDTH*0.18), round(HEIGHT*0.11)))
    elif position == 'center':
        textRect.center = (round(WIDTH*0.5), round(HEIGHT*0.75))
        if round(WIDTH*(0.5-0.18/2)) <= mouse[0] <= round(WIDTH*(0.5+0.18/2)) and round(HEIGHT*(0.75-0.11/2)) <= mouse[1] <= round(HEIGHT*(0.75+0.11/2)):
            pygame.draw.rect(main_display, COLOR_YELLOW,(round(WIDTH*(0.5-0.18/2)), round(HEIGHT*(0.75-0.11/2)), round(WIDTH*0.18), round(HEIGHT*0.11)))
            if click[0] == 1 and action != None:
                action()
        else:
            pygame.draw.rect(main_display, COLOR_BLUE,(round(WIDTH*(0.5-0.18/2)), round(HEIGHT*(0.75-0.11/2)), round(WIDTH*0.18), round(HEIGHT*0.11)))
    else:
        textRect.center = (round(WIDTH*0.75), round(HEIGHT*0.75))
        if round(WIDTH*(0.75-0.18/2)) <= mouse[0] <= round(WIDTH*(0.75+0.18/2)) and round(HEIGHT*(0.75-0.11/2)) <= mouse[1] <= round(HEIGHT*(0.75+0.11/2)):
            pygame.draw.rect(main_display, COLOR_YELLOW,(round(WIDTH*(0.75-0.18/2)), round(HEIGHT*(0.75-0.11/2)), round(WIDTH*0.18), round(HEIGHT*0.11)))
            if click[0] == 1 and action != None:
                action()
        else:
            pygame.draw.rect(main_display, COLOR_RED,(round(WIDTH*(0.75-0.18/2)), round(HEIGHT*(0.75-0.11/2)), round(WIDTH*0.18), round(HEIGHT*0.11)))
    main_display.blit(textSurf, textRect)  

def statistics():
    global score, difficulty, enemy_count, enemy_collisions, bonus_count, bonus_collected, max_score, extra_lives

    stat = True

    main_display.fill(COLOR_BLACK)

    match difficulty:
        case 'easy':
            diff = 'Легко'
        case 'normal':
            diff = 'Нормально'
        case 'hard':
            diff = 'Складно'

    text_line_display('Статистика', 0.15)
    text_line_display('Складність: ' + diff, 0.2)
    text_line_display('Набрано балів: ' + str(score), 0.25)
    text_line_display('Максимально можливі бали: ' + str(max_score), 0.3)
    text_line_display('Ефективність: ' + str(round(score/max_score*100, 2)) + '%', 0.35)
    text_line_display('Додаткових життів: ' + str(extra_lives), 0.4)
    text_line_display('Всього ракет: ' + str(enemy_count), 0.45)
    text_line_display('Зіткнень з ракетами: ' + str(enemy_collisions), 0.5)
    text_line_display('Всього вантажів: ' + str(bonus_count), 0.55)
    text_line_display('Підібрано вантажів: ' + str(bonus_collected), 0.6)
    text_line_display('Ефективність: ' + str(round(bonus_collected/bonus_count*100, 2)) + '%', 0.65)

    while stat:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
                
        button('Нова гра!', 'left', choose_difficulty)
        button('Вийти :(', 'right', game_exit)

        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            game_exit()
             
        pygame.display.update()

def game_over():
    global game_end, score, difficulty

    pygame.mixer.music.stop()
    
    game_end = True

    message_display('Гру завершено :(')

    high_score = []

    try:
        with open('high score.txt', 'x') as f:
            match difficulty:
                case 'easy':
                    high_score = [str(score) + '\n', '0\n', '0\n']
                    f.writelines(high_score)
                case 'normal':
                    high_score = ['0\n', str(score) + '\n', '0\n']
                    f.writelines(high_score)
                case 'hard':
                    high_score = ['0\n', '0\n', str(score) + '\n']
                    f.writelines(high_score)
            text_line_display('Ваш рахунок: ' + str(score), 0.62)
            f.close()
    except FileExistsError:
        with open('high score.txt', 'r') as f:
            high_score = f.readlines()
            f.close()
        with open('high score.txt', 'w') as f:
            match difficulty:
                case 'easy':
                    if score > int(high_score[0]) and int(high_score[0]) != 0:
                        text_line_display('Новий рекорд легкої складності: ' + str(score) + '!!!', 0.6)
                        text_line_display('Попередній рекорд легкої складності: ' + high_score[0].strip(), 0.65)
                        high_score[0] = str(score) + '\n'
                        f.writelines(high_score)
                    elif score == int(high_score[0]):
                        text_line_display('Повторено рекорд легкої складності: ' + str(score) + '!!!', 0.62)
                        f.writelines(high_score)
                    elif score < int(high_score[0]):
                        text_line_display('Ваш рахунок: ' + str(score), 0.6)
                        text_line_display('Рекорд легкої складності: ' + high_score[0].strip(), 0.65)
                        f.writelines(high_score)
                    else:
                        text_line_display('Ваш рахунок: ' + str(score), 0.62)
                        high_score[0] = str(score) + '\n'
                        f.writelines(high_score)
                case 'normal':
                    if score > int(high_score[1]) and int(high_score[1]) != 0:
                        text_line_display('Новий рекорд нормальної складності: ' + str(score) + '!!!', 0.6)
                        text_line_display('Попередній рекорд нормальної складності: ' + high_score[1].strip(), 0.65)
                        high_score[1] = str(score) + '\n'
                        f.writelines(high_score)
                    elif score == int(high_score[1]):
                        text_line_display('Повторено рекорд нормальної складності: ' + str(score) + '!!!', 0.62)
                        f.writelines(high_score)
                    elif score < int(high_score[1]):
                        text_line_display('Ваш рахунок: ' + str(score), 0.6)
                        text_line_display('Рекорд нормальної складності: ' + high_score[1].strip(), 0.65)
                        f.writelines(high_score)
                    else:
                        text_line_display('Ваш рахунок: ' + str(score), 0.62)
                        high_score[1] = str(score) + '\n'
                        f.writelines(high_score)
                case 'hard':
                    if score > int(high_score[2]) and int(high_score[2]) != 0:
                        text_line_display('Новий рекорд складної складності: ' + str(score) + '!!!', 0.6)
                        text_line_display('Попередній рекорд складної складності: ' + high_score[2].strip(), 0.65)
                        high_score[2] = str(score) + '\n'
                        f.writelines(high_score)
                    elif score == int(high_score[2]):
                        text_line_display('Повторено рекорд складної складності: ' + str(score) + '!!!', 0.62)
                        f.writelines(high_score)
                    elif score < int(high_score[2]):
                        text_line_display('Ваш рахунок: ' + str(score), 0.6)
                        text_line_display('Рекорд складної складності: ' + high_score[2].strip(), 0.65)
                        f.writelines(high_score)
                    else:
                        text_line_display('Ваш рахунок: ' + str(score), 0.62)
                        high_score[2] = str(score) + '\n'
                        f.writelines(high_score)
            f.close()

    while game_end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
    
        button('Нова гра!', 'left', choose_difficulty)
        button('Статистика', 'center', statistics)
        button('Вийти :(', 'right', game_exit)

        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            game_exit()  

        pygame.display.update()

def back_to_intro():
    global control
    control = False
    global intro
    intro = False
    time.sleep(0.25)
    game_intro()

def controls():
    global control
    control = True

    main_display.fill(COLOR_BLACK)

    time.sleep(0.25)

    text_line_display('підбирайте вантажі та уникайте ракет', 0.1)
    text_line_display('100* балів = додаткове життя, *кожні 5 рівнів зростає на 50', 0.15)
    text_line_display('кожну хвилину новий рівень', 0.2)
    text_line_display('кожен рівень прискорюються ракети, кожних 2 - вантажі', 0.25)
    text_line_display('кожних 3 рівні прискорюється гусак, а кожних 4 зростають бали за вантажі', 0.3)
    text_line_display('керування:', 0.35)
    text_line_display('стрілка вгору або W - рухати гусака вгору', 0.4)
    text_line_display('стрілка вниз або S - рухати гусака донизу', 0.45)
    text_line_display('стрілка ліворуч або A - рухати гусака ліворуч', 0.5)
    text_line_display('стрілка праворуч або D - рухати гусака праворуч', 0.55)
    text_line_display('P - пауза', 0.6)
    text_line_display('Esc - назад/вихід', 0.65)

    while control:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
                
        button('Головне меню', 'center', back_to_intro)

        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            back_to_intro()
             
        pygame.display.update()

def easy():
    global difficulty
    difficulty = 'easy'
    game_loop()

def normal():
    global difficulty
    difficulty = 'normal'
    game_loop()

def hard():
    global difficulty
    difficulty = 'hard'
    game_loop()

def choose_difficulty():
    global intro
    intro = False
    diff = True

    main_display.fill(COLOR_BLACK)

    time.sleep(0.25)

    message_display('Оберіть складність')

    while diff:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
                
        button('Легко', 'left', easy)
        button('Нормально', 'center', normal)
        button('Складно', 'right', hard)

        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            diff = False
            time.sleep(0.25)
            game_intro()
             
        pygame.display.update()

def game_intro():
    global intro  
    intro = True

    message_display('Бандерогусак!')

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
                
        button('Грати :)', 'left', choose_difficulty)
        button('Керування', 'center', controls)
        button('Вийти :(', 'right', game_exit)

        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            game_exit()
             
        pygame.display.update()

def unpause():
    global paused
    pygame.mixer.music.unpause()
    paused = False

def pause():
    global paused, score, lives, difficulty
    
    pygame.mixer.music.pause()

    message_display('Пауза!')

    match difficulty:
        case 'easy':
            diff = 'Легко'
        case 'normal':
            diff = 'Нормально'
        case 'hard':
            diff = 'Складно'

    text_line_display('Складність: ' + diff, 0.6)
    text_line_display('Ваш рахунок: ' + str(score) + '   Життів залишилось: ' + str(lives), 0.65)

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
                
        button('Продовжити :)', 'left', unpause)
        button('Нова гра!', 'center', choose_difficulty)
        button('Вийти :(', 'right', game_exit)

        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == 'escape' or 'p':
                    unpause()
             
        pygame.display.update()

def game_loop():
    global paused, bg_move, score, level, difficulty, lives, enemy_count, enemy_collisions, bonus_count, bonus_collected, max_score, extra_lives, jumps, extra_jumps, rage_count, rage_used_count

    pygame.mixer.music.load('Village of fools soundtrack.wav')
    pygame.mixer.music.play(-1)
    
    bg = pygame.transform.scale(pygame.image.load('background.png'), (WIDTH, HEIGHT))
    bg_X1 = 0
    bg_X2 = bg.get_width()
        
    IMAGE_PASS = "Goose"
    PLAYER_IMAGES = os.listdir(IMAGE_PASS)

    # player_size = (20, 20)
    # player = pygame.Surface(player_size)
    player = pygame.image.load('player.png').convert_alpha()
    # player.fill(COLOR_BLACK)
    player_size = player.get_size()
    player_rect = pygame.Rect(0, (HEIGHT - player_size[1]) / 2, *player_size)
    
    match difficulty:
        case 'easy':
            time_correction = 0
            jump = 0
            jumps = 3
        case 'normal':
            time_correction = 250
            jump = 0.5
            jumps = 2
        case 'hard':
            time_correction = 500
            jump = 1
            jumps = 1

    CREATE_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(CREATE_ENEMY, 1500 - time_correction)
    CREATE_BONUS = pygame.USEREVENT + 2
    pygame.time.set_timer(CREATE_BONUS, 1000 + time_correction)
    CHANGE_IMAGE = pygame.USEREVENT + 3
    pygame.time.set_timer(CHANGE_IMAGE, 200)
    CHANGE_LEVEL = pygame.USEREVENT + 4
    pygame.time.set_timer(CHANGE_LEVEL, 60000)

    enemies = []
    bonuses = []
    rages = []

    score = 0
    lives = 3
    level = 1
    score_lives = 0
    score_for_lives = 100
    score_jumps = 0
    score_for_jumps = 50
    enemy_count = 0
    enemy_collisions = 0
    bonus_count = 0
    bonus_collected = 0
    max_score = 0
    extra_lives = 0
    extra_jumps = 0
    animation_boost = 0
    rage_q = 1
    rage_count = 0
    rage_used_count = 0
    rage_duration = 0
    time_elapsed = 0
    rage_appearance_time = 0
    lives_image = pygame.transform.scale(pygame.image.load('lives.png'), (WIDTH*0.05, WIDTH*0.05))
    jumps_image = pygame.transform.scale(pygame.image.load('jump.png'), (WIDTH*0.05, WIDTH*0.05))
    coin = pygame.transform.scale(pygame.image.load('coin.png'), (WIDTH*0.05, WIDTH*0.05))
    pause_image = pygame.transform.scale(pygame.image.load('pause.png'), (WIDTH*0.05, WIDTH*0.05))

    image_index = 0

    gameExit = False

    while not gameExit:
        FPS.tick(120)

        for event in pygame.event.get():
            if event.type == QUIT:
                gameExit = True
                game_exit()
            if event.type == CREATE_ENEMY:
                enemies.append(create_enemy())
            if event.type == CREATE_BONUS:
                bonuses.append(create_bonus())
            if event.type == CHANGE_IMAGE:
                player = pygame.image.load(os.path.join(IMAGE_PASS, PLAYER_IMAGES[image_index]))
                image_index += 1
                if image_index >= len(PLAYER_IMAGES):
                    image_index = 0
            if event.type == CHANGE_LEVEL:
                level += 1
                rages.append(create_rage())
                rage_appearance_time = pygame.time.get_ticks()
            if event.type == pygame.KEYUP:
                # keyup = pygame.key.name(event.key)
                # print (keyup, "Key is released")
                if pygame.key.name(event.key) == 'space':
                    if jumps > 0:
                        pygame.time.set_timer(CHANGE_IMAGE, 40)
                        animation_boost = 15
                        if player_rect[1] - round(HEIGHT/(jump + 4)) < 0:
                            player_rect[1] = 0
                        else:
                            player_rect = player_rect.move([0, -round(HEIGHT/(jump + 4))])
                        jumps -= 1
                if pygame.key.name(event.key) == 'escape':
                    game_exit()
                if pygame.key.name(event.key) == 'p':
                    paused = True
                    pause()

        # main_display.fill(COLOR_BLACK)

        player_move_down = [0, (1.5+bg_move+math.floor(level/3))*rage_q]
        player_move_up = [0, (-0.5-bg_move-math.floor(level/3))*rage_q]
        player_move_right = [(1+bg_move+math.floor(level/3))*rage_q, 0]
        player_move_left = [(-1-bg_move-math.floor(level/3))*rage_q, 0]

        score_for_lives = 100 + 50 * math.floor(level/5)

        bg_X1 -= bg_move
        bg_X2 -= bg_move

        if bg_X1 < -bg.get_width():
            bg_X1 = bg.get_width()

        if bg_X2 < -bg.get_width():
            bg_X2 = bg.get_width()    

        main_display.blit(bg, (bg_X1, 0))
        main_display.blit(bg, (bg_X2, 0))

        keys = pygame.key.get_pressed()

        if (keys[K_DOWN] or keys[K_s]) and player_rect.bottom < HEIGHT:
            player_rect = player_rect.move(player_move_down)

        if (keys[K_UP] or keys[K_w]) and player_rect.top > 0:
            player_rect = player_rect.move(player_move_up)    
        
        if (keys[K_RIGHT] or keys[K_d]) and player_rect.right < WIDTH:
            player_rect = player_rect.move(player_move_right)

        if (keys[K_LEFT] or keys[K_a]) and player_rect.left > 0:
            player_rect = player_rect.move(player_move_left)

        if animation_boost > 0:
            if animation_boost == 1:
                pygame.time.set_timer(CHANGE_IMAGE, 200)
            animation_boost -= 1

        for enemy in enemies:
            enemy[1] = enemy[1].move(enemy[2])
            main_display.blit(enemy[0], enemy[1])

            if player_rect.colliderect(enemy[1]):
                pygame.mixer.Sound.play(crash_sound)
                lives -= 1
                enemy_collisions += 1
                if lives <= 0:
                    game_over()
                enemies.pop(enemies.index(enemy))

        for bonus in bonuses:
            bonus[1] = bonus[1].move(bonus[2])
            main_display.blit(bonus[0], bonus[1])

            if player_rect.colliderect(bonus[1]):
                pygame.mixer.Sound.play(coin_sound)
                score += bonus[3]
                score_lives += bonus[3]
                score_jumps += bonus[3]
                bonus_collected += 1
                if score_lives >= score_for_lives:
                    lives += 1
                    score_lives += -score_for_lives
                    extra_lives += 1
                if score_jumps >= score_for_jumps:
                    jumps += 1
                    score_jumps += -score_for_jumps
                    extra_jumps += 1
                bonuses.pop(bonuses.index(bonus))

        for rage in rages:
            main_display.blit(rage[0], rage[1])
            rage_screen_time = rage[3]

            if pygame.time.get_ticks() > rage_appearance_time + rage_screen_time:
                rage_screen_time = 0
                rages.pop(rages.index(rage))

            if player_rect.colliderect(rage[1]):
                pygame.mixer.Sound.play(rage_sound)
                time_elapsed = pygame.time.get_ticks()
                rage_duration = rage[2]
                rage_q = 1.5
                rage_used_count += 1
                rages.pop(rages.index(rage))

        if pygame.time.get_ticks() > time_elapsed + rage_duration:
            rage_duration = 0
            rage_q = 1

        main_display.blit(coin, (round(WIDTH*(0.895-0.065)), round(HEIGHT*0.025)))
        main_display.blit(FONT.render(str(score), True, COLOR_BLACK), (round(WIDTH*0.895), round(HEIGHT*0.03)))
        match lives:
            case 1:
                main_display.blit(lives_image, (round(WIDTH*0.042), round(HEIGHT*0.025)))
            case 2:
                main_display.blit(lives_image, (round(WIDTH*0.042), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-1))), round(HEIGHT*0.025)))
            case 3:
                main_display.blit(lives_image, (round(WIDTH*0.042), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-2))), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-1))), round(HEIGHT*0.025)))
            case 4:
                main_display.blit(lives_image, (round(WIDTH*(0.042)), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-3))), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-2))), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-1))), round(HEIGHT*0.025)))
            case 5:
                main_display.blit(lives_image, (round(WIDTH*0.042), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-4))), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-3))), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-2))), round(HEIGHT*0.025)))
                main_display.blit(lives_image, (round(WIDTH*(0.042+0.065*(lives-1))), round(HEIGHT*0.025)))
            case _:
                main_display.blit(lives_image, (round(WIDTH*0.042), round(HEIGHT*0.025)))
                main_display.blit(FONT.render("X " + str(lives), True, COLOR_BLACK), (round(WIDTH*(0.042+0.065)), round(HEIGHT*0.03)))
        main_display.blit(jumps_image, (round(WIDTH*(0.895-0.065)), round(HEIGHT*0.895)))
        main_display.blit(FONT.render("X " + str(jumps), True, COLOR_BLACK), (round(WIDTH*0.895), round(HEIGHT*0.9)))
        main_display.blit(pause_image,(round(WIDTH*(0.5-0.05/2)), round(HEIGHT*0.025)))
        main_display.blit(FONT.render("Рівень: " + str(level), True, COLOR_BLACK), (round(WIDTH*(0.042)), round(HEIGHT*0.9)))
        main_display.blit(player, player_rect)

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if round(WIDTH*(0.5-0.027/2)) <= mouse[0] <= round(WIDTH*(0.5+0.027/2)) and round(HEIGHT*0.025) <= mouse[1] <= round(HEIGHT*(0.025+0.05)):
            if click[0] == 1:
                paused = True
                pause()

        pygame.display.flip()

        for enemy in enemies:
            if enemy[1].right < 0:
                enemies.pop(enemies.index(enemy))

        for bonus in bonuses:
            if bonus[1].top > HEIGHT:
                bonuses.pop(bonuses.index(bonus))

game_intro()
game_exit()