#imports
import socket
import pygame
import json
import os
import messages
import threading
import time

#constants
WIDTH = 1000
HEIGHT = 700

tile_size = 76

#setup connection with server
# server_address=("localhost", 6789)
IP = 'localhost'
port = 6789

temp_ip = input(f"IP Address ({IP}): ")
if temp_ip!="":
    try:
        IP = int(temp_ip)
    except ValueError:
        IP = temp_ip

temp_port = input(f"Port ({port}): ")
if temp_port!="":
    port = int(temp_port)

server_address = (IP,port)

max_size=100000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
#data=client.recv(max_size)

#game variables
game_state = -1
#player_id = 0
gamedata_string = str(client.recv(max_size), "utf-8")
game_data = json.loads(gamedata_string)
#time.sleep(0.1)
print(game_data)
print(type(game_data["players"]))

x_offset = 0
y_offset = 0

#setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

player_id = int(client.recv(28).decode().split("|")[0])

time.sleep(0.5)

tiles = [pygame.transform.scale(pygame.image.load("assets/tiles/sky.png"),(tile_size,tile_size)),
        pygame.transform.scale(pygame.image.load("assets/tiles/ground.png"),(tile_size,tile_size)),
        pygame.transform.scale(pygame.image.load("assets/tiles/gate.png"),(tile_size,tile_size))]

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(650,100)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(650,100))]

freeze_vfx_img = pygame.transform.scale(pygame.image.load("assets/misc/freeze.png"),(100,50))
freeze_vfx = []
freeze_vfx_1 = pygame.Surface((50, 50))
freeze_vfx_1.set_colorkey((0,0,0))
freeze_vfx_1.blit(freeze_vfx_img, (0, 0), (0, 0, 50, 50))
freeze_vfx_2 = pygame.Surface((50, 50))
freeze_vfx_2.set_colorkey((0,0,0))
freeze_vfx_2.blit(freeze_vfx_img, (0, 0), (50, 0, 50, 50))

freeze_vfx.append(freeze_vfx_1)
freeze_vfx.append(freeze_vfx_2)

# all five frames of the attack are in this image
freeze_attack = pygame.transform.scale(pygame.image.load("assets/misc/attack_freeze.png"),(175*2,70))

# creating a list allows us to have as many freezes as we need on the screen. When they're gone, they simply get removed from the list
# this information is organized as [x,y,state]
freezes = []

def display_tiles():
    window.fill((0,0,0));
    for row_count,row in enumerate(game_data["level"]["grid"]):
        for col_count,column in enumerate(row):
            window.blit(tiles[column],((col_count * tile_size)-x_offset,(row_count * tile_size)-y_offset))
    return 1

anim_speed = 7
player1_animation = "idle"
player2_animation = "idle"
player1_animation_state = 0
player2_animation_state = 0
player1_animation_direction = 1
player2_animation_direction = 1
animation_counter = 0
on_ground = 0
# set this to the number of times the players are able to jump without touching the ground
num_jumps = 3
jumps = num_jumps

player_y_vel = 0
game_data["players"][player_id]["x_vel"] = 0
gravity_counter = 0
friction_counter = 0
friction_speed = 8
max_x_vel = 7
x_vel_change = 1

punch_range = 50
punch_speed = 10

winner = 0

def display_win_screen():
    global winner
    global x_offset, y_offset
    fadeout = pygame.Surface((WIDTH,HEIGHT))
    fadeout = fadeout.convert()
    fadeout.fill((0,0,0))
    fadeout.set_alpha(250)
    displaying_anim = True
    fireworks = pygame.transform.scale(pygame.image.load("assets/misc/fireworks.png"),(3040,380))
    crown = pygame.transform.scale(pygame.image.load('assets/misc/crown.png'),(250,300))
    firework_state = 0
    counter = 0
    darkness = 0
    fade = -1
    fw = pygame.Surface((380, 380))
    fw.set_colorkey((0,0,0))
    while displaying_anim:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                quit()
        # x_offset =
        display_tiles()
        display_players()
        window.blit(fadeout,(0,0))
        if darkness>0 and fade==1:
            darkness-=1
            fadeout.set_alpha(darkness)
        elif fade==-1 and darkness<250:
            darkness+=1
            fadeout.set_alpha(darkness)
        elif darkness<=0 and fade == 1:
            fade = 0
        elif darkness>=250 and fade == -1:
            displaying_anim = False
        elif fade == 0:
            counter+=1
            if counter>50:
                fade = -1
        pygame.display.update()

    display_winner = True
    counter = 0
    p1 = pygame.Surface((250, 250))
    p1.set_colorkey((0,0,0))
    p1.blit(pygame.transform.scale(players[1],(250*9,500)), (0, 0), (0, 0, 250, 250))
    p0 = pygame.Surface((250, 250))
    p0.set_colorkey((0,0,0))
    p0.blit(pygame.transform.scale(players[0],(250*9,500)), (0, 0), (0, 0, 250, 250))
    while display_winner:
        clock.tick(60)
        window.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                quit()
        window.blit(p0,(200,250))
        window.blit(p1,(550,250))
        if winner == 0:
            window.blit(crown,(200,200))
        else:
            window.blit(crown,(550,200))
        fw.fill((0,0,0,0))
        if firework_state<9:
            fw.blit(fireworks, (0, 0), ((firework_state) * 380, 0, 380, 380))
            if winner == 0:
                window.blit(fw,(200-65,250-65))
            else:
                window.blit(fw,(550-65,250-65))
            counter+=1
            if counter>anim_speed:
                firework_state+=1
                counter = 0
        pygame.display.update()

frozen = 0
freeze_counter = 0
freeze_duration = 30

def display_players():
    p1 = pygame.Surface((50, 50))
    p1.set_colorkey((0,0,0))
    p1.blit(players[1], (0, 0), ((player2_animation_state) * 50, (game_data["players"][1]["facing"]) * 50, 50, 50))
    p0 = pygame.Surface((50, 50))
    p0.set_colorkey((0,0,0))
    p0.blit(players[0], (0, 0), ((player1_animation_state) * 50, (game_data["players"][0]["facing"]) * 50, 50, 50))
    if player_id == 0:
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        if game_data["players"][1]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][1]["facing"]],(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        if game_data["players"][0]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][0]["facing"]],(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
    else:
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        if game_data["players"][0]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][0]["facing"]],(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        if game_data["players"][1]["frozen"]:
            window.blit(freeze_vfx[game_data["players"][1]["facing"]],(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))

freezes_counter = 0
def update_freezes():
    global freezes_counter
    freezes_counter+=1
    img = pygame.Surface((70, 70))
    img.set_colorkey((0,0,0))
    for fr in freezes:
        img.blit(freeze_attack, (0, 0), (fr[2] * 70, 0, 70, 70))
        window.blit(img,(fr[0]-x_offset,fr[1]-y_offset))
        if freezes_counter>anim_speed//2:
            fr[2]+=1
            if fr[2]>4:
                freezes.remove(fr)
    if freezes_counter>anim_speed//2:
        freezes_counter = 0

def listen_to_server(client):
    global player1_animation
    global player2_animation
    global player1_animation_state
    global player2_animation_state
    global player1_animation_direction
    global player2_animation_direction
    global game_data
    global game_state
    global winner
    global frozen
    global freeze_counter
    global freezes
    while game_state:
        msg = client.recv(max_size)
        if(str(msg,"utf-8") == "quit"):
            print("quit")
            game_state = 0
        game_data,anim_data,win_data, freeze_data = messages.parse_message(msg,game_data)
        if anim_data[0]==1:
            if anim_data[1]==0:
                player1_animation = game_data["players"][0]["anim"][0]
                player1_animation_state = game_data["players"][0]["anim"][1]
                player1_animation_direction = game_data["players"][0]["anim"][2]
            else:
                player2_animation = game_data["players"][1]["anim"][0]
                player2_animation_state = game_data["players"][1]["anim"][1]
                player2_animation_direction = game_data["players"][1]["anim"][2]
        if win_data[0]==1:
            winner = win_data[1]
            game_state = 0

        if game_data["players"][player_id]["frozen"] and not frozen:
            # print("I got frozen")
            frozen = 1
            freeze_counter = 0

        # print(freeze_data[0])
        if freeze_data[0]==1: # if we need to play the animation
            print("initiating freeze")
            freezes.append([freeze_data[1],freeze_data[2],0])

game_data["countdown"] = 7
server_listener = threading.Thread(target=lambda:listen_to_server(client))
server_listener.start()

player_width = 50
player_height = 50

countdown_font = pygame.font.Font("assets/fonts/mainfont.ttf",120)

def print_text(text,font,color,coordinates,center = False,anti_alias = True):
    text_surface = font.render(text,anti_alias,color)
    if center:
        text_rect = text_surface.get_rect()
        text_rect.center = (coordinates)
        window.blit(text_surface,text_rect)
    else:
        window.blit(text_surface,coordinates)

level_width = len(game_data["level"]['grid'][0])*tile_size
level_height = len(game_data["level"]['grid'])*tile_size
if level_width >= WIDTH:
    max_x_offset = level_width - WIDTH
else: max_x_offset = 0
if level_width >= HEIGHT:
    max_y_offset = level_height - HEIGHT
else: max_y_offset = 0
max_char_x = level_width - player_width
max_char_y = level_height - player_height

while game_state != 0:
    clock.tick(60)
    if game_state == -1: # game_data["countdown"]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        display_tiles()
        display_players()
        if game_data["countdown"] == -1:
            game_state = 1
        elif game_data["countdown"] == 0:
            print_text("GO!",countdown_font,(255,255,255),(WIDTH//2,HEIGHT//2),True,False)
        elif game_data["countdown"] > 5:
            print_text("Ready!",countdown_font,(255,255,255),(WIDTH//2,HEIGHT//2),True,False)
        else:
            print_text(str(game_data["countdown"]),countdown_font,(255,255,255),(WIDTH//2,HEIGHT//2),True,False)
        pygame.display.update()
    elif game_state == 1: # main game loop
        x_offset = int(((int(game_data["players"][player_id]["x"])) / max_char_x) * max_x_offset)
        y_offset = int(((int(game_data["players"][player_id]["y"])) / max_char_y) * max_y_offset)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                messages.send_message("quit",client)
                pygame.quit()
                client.close()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if not frozen:
                        if jumps>0:
                            jumps-=1
                            if player_id==0:
                                player1_animation = "jump"
                                player1_animation_state = 3
                                player1_animation_direction = 1
                                messages.send_message("anim 0 jump 3 1|",client)
                            else:
                                player2_animation = "jump"
                                player2_animation_state = 3
                                player2_animation_direction = 1
                                messages.send_message("anim 1 jump 3 1|",client)
                            player_y_vel -= 10
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if not frozen:
                        messages.send_message(f'fr_attack {game_data["players"][player_id]["x"]-10} {game_data["players"][player_id]["y"]-10}|',client)
                        freezes.append([game_data["players"][player_id]["x"]-10,game_data["players"][player_id]["y"]-10,0])
                        if player_id == 0:
                            if (abs((game_data['players'][0]["x"]) - (game_data['players'][1]["x"])) <= player_width*1.5) and (abs((game_data['players'][0]["y"]) - (game_data['players'][1]["y"])) <= player_height*1.5):
                                #print("froze a player 1")
                                messages.send_message(f"freeze 1 1|",client)
                                game_data['players'][1]["frozen"] = 1;
                        if player_id == 1:
                            if (abs((game_data['players'][1]["x"]) - (game_data['players'][0]["x"])) <= player_width*1.5) and (abs((game_data['players'][1]["y"]) - (game_data['players'][0]["y"])) <= player_height*1.5):
                                #print("froze a player 0")
                                messages.send_message(f"freeze 0 1|",client)
                                game_data['players'][0]["frozen"] = 1;
                if event.key == pygame.K_SPACE:
                    if not frozen:
                        if player_id == 0:
                            player1_animation = "punch"
                            player1_animation_state = 9
                            player1_animation_direction = 1
                            messages.send_message("anim 0 punch 9 1|",client)
                            if game_data['players'][0]['facing'] == 0:
                                new_x = game_data["players"][player_id]["x"]+player_width
                                player_y = game_data['players'][player_id]["y"]
                                if ((new_x + punch_range > game_data['players'][1]["x"]) and (game_data['players'][1]["x"] > game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][1]["y"] - player_height) and (player_y < game_data['players'][1]["y"] + player_height)):
                                    messages.send_message(f"punch 1 {punch_speed}|",client)
                                    player2_animation = "hit"
                                    player2_animation_state = 12
                                    player2_animation_direction = 1
                                    messages.send_message("anim 1 hit 12 1|",client)
                            elif game_data['players'][0]['facing'] == 1:
                                new_x = game_data["players"][player_id]["x"]
                                player_y = game_data['players'][player_id]["y"]
                                if ((new_x - punch_range < game_data['players'][1]["x"]+player_width) and (game_data['players'][1]["x"] < game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][1]["y"] - player_height) and (player_y < game_data['players'][1]["y"] + player_height)):
                                    messages.send_message(f"punch 1 -{punch_speed}|",client)
                                    player2_animation = "hit"
                                    player2_animation_state = 12
                                    player2_animation_direction = 1
                                    messages.send_message("anim 1 hit 12 1|",client)
                        if player_id == 1:
                            player2_animation = "punch"
                            player2_animation_state = 9
                            player2_animation_direction = 1
                            messages.send_message("anim 1 punch 9 1|",client)
                            if game_data['players'][1]['facing'] == 0:
                                new_x = (game_data["players"][player_id]["x"])+player_width
                                player_y = game_data['players'][player_id]["y"]
                                if ((new_x + punch_range > game_data['players'][0]["x"]) and (game_data['players'][0]["x"] > game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][0]["y"] - player_height) and (player_y < game_data['players'][0]["y"] + player_height)):
                                    messages.send_message(f"punch 0 {punch_speed}|",client)
                                    player1_animation = "hit"
                                    player1_animation_state = 12
                                    player1_animation_direction = 1
                                    messages.send_message("anim 0 hit 12 1|",client)
                            elif game_data['players'][1]['facing'] == 1:
                                new_x = game_data["players"][player_id]["x"]
                                player_y = game_data['players'][player_id]["y"]
                                if ((new_x - punch_range < game_data['players'][0]["x"]+player_width) and (game_data['players'][0]["x"] < game_data["players"][player_id]["x"])) and ((player_y > game_data['players'][0]["y"] - player_height) and (player_y < game_data['players'][0]["y"] + player_height)):
                                    messages.send_message(f"punch 0 -{punch_speed}|",client)
                                    player1_animation = "hit"
                                    player1_animation_state = 12
                                    player1_animation_direction = 1
                                    messages.send_message("anim 0 hit 12 1|",client)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not frozen:
                if game_data["players"][player_id]["x_vel"] < max_x_vel:
                    game_data["players"][player_id]["x_vel"] += x_vel_change
                # new_x = (game_data["players"][player_id]["x"]+player_move_speed)+50
                # player_y = game_data['players'][player_id]["y"]
                #
                # if new_x<(len(game_data["level"]['grid'][0])*tile_size):
                #     tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                #     tile_2 = 0
                #     if player_y % tile_size != 0:
                #         tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]
                #
                #     if tile_1 != 1 and tile_2 != 1:
                #         game_data["players"][player_id]["x"]+=player_move_speed
                #         messages.send_message(f"move {player_id} {player_move_speed}|",client)
                # if player_id == 0:
                #     game_data["players"][player_id]["facing"] = 0
                # if player_id == 1:
                #     game_data["players"][player_id]["facing"] = 0
                # messages.send_message(f"face {player_id} 0 |",client)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if not frozen:
                if game_data["players"][player_id]["x_vel"] > -max_x_vel:
                    game_data["players"][player_id]["x_vel"] -= x_vel_change
                # new_x = (game_data["players"][player_id]["x"]-player_move_speed)
                # if new_x>0:
                #     player_y = game_data['players'][player_id]["y"]
                #
                #     tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                #     tile_2 = 0
                #     if player_y % tile_size != 0:
                #         tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]
                #
                #     if tile_1 != 1 and tile_2 != 1:
                #         game_data["players"][player_id]["x"]-=player_move_speed
                #         messages.send_message(f"move {player_id} -{player_move_speed}|",client)
                #         if tile_1==2 or tile_2==2:
                #             print("reached the end")
                #             messages.send_message(f"win {player_id}|",client)
                #             winner = player_id
                #             game_state = 0
                #         if player_id == 0:
                #             game_data["players"][player_id]["facing"] = 1
                #         if player_id == 1:
                #             game_data["players"][player_id]["facing"] = 1
                #         messages.send_message(f"face {player_id} 1 |",client)
        # apply gravity to player
        if player_y_vel>0:
            new_y = (game_data["players"][player_id]["y"]+player_y_vel)+50
            if new_y>len(game_data["level"]["grid"])*tile_size:
                player_y_vel = 0
                messages.send_message(f'move y {player_id} {game_data["level"]["player_y"]-game_data["players"][player_id]["y"]}|',client)
                messages.send_message(f'move {player_id} {game_data["level"]["player_x"]-game_data["players"][player_id]["x"]}|',client)
                game_data["players"][player_id]["y"] = game_data["level"]["player_y"]
                game_data["players"][player_id]["x"] = game_data["level"]["player_x"]
            else:
                player_x = game_data['players'][player_id]["x"]

                tile_1 = game_data['level']['grid'][new_y//tile_size][player_x//tile_size]
                tile_2 = 0
                if player_x % tile_size != 0:
                    tile_2 = game_data['level']['grid'][new_y//tile_size][(player_x+50)//tile_size]

                if tile_1 != 1 and tile_2 != 1:
                    game_data["players"][player_id]["y"]+=player_y_vel
                    messages.send_message(f"move y {player_id} {player_y_vel}|",client)
                    on_ground = 0
                    if tile_1==2 or tile_2==2:
                        print("reached the end")
                        messages.send_message(f"win {player_id} |",client)
                        winner = player_id
                        game_state = 0
                else:
                    player_y_vel = 0
                    if on_ground == 0:
                        if player_id == 0:
                            player1_animation = "land"
                            player1_animation_state = 6
                            player1_animation_direction = 1
                            messages.send_message("anim 0 land 6 1|",client)
                        else:
                            player2_animation = "land"
                            player2_animation_state = 6
                            player2_animation_direction = 1
                            messages.send_message("anim 1 land 6 1|",client)
                    on_ground = 1
                    jumps = num_jumps

        if player_y_vel<0:
            new_y = (game_data["players"][player_id]["y"]+player_y_vel)
            player_x = game_data['players'][player_id]["x"]

            tile_1 = game_data['level']['grid'][new_y//tile_size][player_x//tile_size]
            tile_2 = 0
            if player_x % tile_size != 0:
                tile_2 = game_data['level']['grid'][new_y//tile_size][(player_x+50)//tile_size]

            if tile_1 != 1 and tile_2 != 1:
                game_data["players"][player_id]["y"]+=player_y_vel
                messages.send_message(f"move y {player_id} {player_y_vel}|",client)
                if tile_1==2 or tile_2==2:
                    messages.send_message(f"win {player_id} |",client)
                    winner = player_id
                    game_state = 0
            else:
                player_y_vel = 0

        gravity_counter+=1
        if gravity_counter>=2:
            gravity_counter = 0
            player_y_vel+=1
            # player_y_vel = 1


        if game_data["players"][player_id]["x_vel"]>0:
            new_x = (game_data["players"][player_id]["x"]+game_data["players"][player_id]["x_vel"])+50

            player_y = game_data['players'][player_id]["y"]
            if new_x<(len(game_data["level"]['grid'][0])*tile_size):
                tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                tile_2 = 0
                if player_y % tile_size != 0:
                    tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

                if tile_1 != 1 and tile_2 != 1:
                    game_data["players"][player_id]["x"]+=game_data["players"][player_id]["x_vel"]
                    messages.send_message(f'move {player_id} {game_data["players"][player_id]["x_vel"]}|',client)
                else:
                    game_data["players"][player_id]["x_vel"] = 0
            if tile_1==2 or tile_2==2:
                print("reached the end")
                messages.send_message(f"win {player_id}|",client)
                winner = player_id
                game_state = 0
            if player_id == 0:
                game_data["players"][player_id]["facing"] = 0
            if player_id == 1:
                game_data["players"][player_id]["facing"] = 0
            messages.send_message(f"face {player_id} 0 |",client)


        if game_data["players"][player_id]["x_vel"]<0:
            new_x = (game_data["players"][player_id]["x"]+game_data["players"][player_id]["x_vel"])

            player_y = game_data['players'][player_id]["y"]
            if new_x>0:
                tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                tile_2 = 0
                if player_y % tile_size != 0:
                    tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

                if tile_1 != 1 and tile_2 != 1:
                    game_data["players"][player_id]["x"]+=game_data["players"][player_id]["x_vel"]
                    messages.send_message(f'move {player_id} {game_data["players"][player_id]["x_vel"]}|',client)
                else:
                    game_data["players"][player_id]["x_vel"] = 0
            if tile_1==2 or tile_2==2:
                print("reached the end")
                messages.send_message(f"win {player_id}|",client)
                winner = player_id
                game_state = 0
            if player_id == 0:
                game_data["players"][player_id]["facing"] = 1
            if player_id == 1:
                game_data["players"][player_id]["facing"] = 1
            messages.send_message(f"face {player_id} 1 |",client)


            # new_y = (game_data["players"][player_id]["x"]+game_data["players"][player_id]["x_vel"])
            # player_x = game_data['players'][player_id]["x"]
            #
            # player_y = game_data['players'][player_id]["y"]
            #
            # tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
            # tile_2 = 0
            # if player_y % tile_size != 0:
            #     tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]
            #
            # if tile_1 != 1 and tile_2 != 1:
            #     game_data["players"][player_id]["x"]+=game_data["players"][player_id]["x_vel"]
            #     messages.send_message(f"move {player_id} +{game_data["players"][player_id]["x_vel"]}|",client)
            # else:
            #     player_y_vel = 0
            #     if tile_1==2 or tile_2==2:
            #         print("reached the end")
            #         messages.send_message(f"win {player_id}|",client)
            #         winner = player_id
            #         game_state = 0
            #     if player_id == 0:
            #         game_data["players"][player_id]["facing"] = 1
            #     if player_id == 1:
            #         game_data["players"][player_id]["facing"] = 1
            #     messages.send_message(f"face {player_id} 1 |",client)

        friction_counter+=1
        if friction_counter>=friction_speed:
            friction_counter = 0
            if game_data["players"][player_id]["x_vel"] > 0:
                game_data["players"][player_id]["x_vel"]-=1
            elif game_data["players"][player_id]["x_vel"] < 0:
                game_data["players"][player_id]["x_vel"]+=1


        animation_counter += 1
        if animation_counter == anim_speed:
            if not game_data["players"][0]["frozen"]:
                if player1_animation == "idle":
                    player1_animation_state += player1_animation_direction
                    if player1_animation_state == 2:
                        player1_animation_direction = -1
                    if player1_animation_state == 0:
                        player1_animation_direction = 1
                elif player1_animation == "jump":
                    player1_animation_state += player1_animation_direction
                    if player1_animation_state == 5:
                        player1_animation_direction = -1
                    if player1_animation_state < 3:
                        player1_animation = "idle"
                        player1_animation_state = 0
                        player1_animation_direction = 1
                        #messages.send_message("anim 0 idle 0 1|",client)
                elif player1_animation == "land":
                    player1_animation_state += player1_animation_direction
                    if player1_animation_state == 8:
                        player1_animation_direction = -1
                    if player1_animation_state < 6:
                        player1_animation = "idle"
                        player1_animation_state = 0
                        player1_animation_direction = 1
                        #messages.send_message("anim 0 idle 0 1|",client)
                elif player1_animation == "punch":
                    player1_animation_state += player1_animation_direction
                    if player1_animation_state == 11:
                        player1_animation_direction = -1
                    if player1_animation_state < 9:
                        player1_animation = "idle"
                        player1_animation_state = 0
                        player1_animation_direction = 1
                elif player1_animation == "hit":
                    player1_animation = "idle"
                    player1_animation_state = 0
                    player1_animation_direction = 1
            if not game_data["players"][1]["frozen"]:
                if player2_animation == "idle":
                    player2_animation_state += player2_animation_direction
                    if player2_animation_state == 2:
                        player2_animation_direction = -1
                    if player2_animation_state == 0:
                        player2_animation_direction = 1
                elif player2_animation == "jump":
                    player2_animation_state += player2_animation_direction
                    if player2_animation_state == 5:
                        player2_animation_direction = -1
                    if player2_animation_state < 3:
                        player2_animation = "idle"
                        player2_animation_state = 0
                        player2_animation_direction = 1
                        #messages.send_message("anim 1 idle 0 1|",client)
                elif player2_animation == "land":
                    player2_animation_state += player2_animation_direction
                    if player2_animation_state == 8:
                        player2_animation_direction = -1
                    if player2_animation_state < 6:
                        player2_animation = "idle"
                        player2_animation_state = 0
                        player2_animation_direction = 1
                        #messages.send_message("anim 1 idle 0 1|",client)
                elif player2_animation == "punch":
                    player2_animation_state += player2_animation_direction
                    if player2_animation_state == 11:
                        player2_animation_direction = -1
                    if player2_animation_state < 9:
                        player2_animation = "idle"
                        player2_animation_state = 0
                        player2_animation_direction = 1
                elif player2_animation == "hit":
                    player2_animation = "idle"
                    player2_animation_state = 0
                    player2_animation_direction = 1
            animation_counter = 0

        if frozen:
            if freeze_counter > freeze_duration:
                game_data["players"][player_id]["frozen"] = 0
                messages.send_message(f"freeze {player_id} 0",client)
                frozen = 0
                freeze_counter = 0
            freeze_counter += 1

        display_tiles()
        display_players()
        update_freezes()
        pygame.display.update()

display_win_screen()

#close client
client.close()
pygame.quit()
quit()
