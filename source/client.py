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
player_move_speed = 3

#setup connection with server
# server_address=("localhost", 6789)
IP = 'localhost'
port = 6789

temp_ip = input("IP Address: ")
if temp_ip!="":
    try:
        IP = int(temp_ip)
    except ValueError:
        IP = temp_ip

temp_port = input("Port: ")
if temp_port!="":
    port = int(temp_port)

server_address = (IP,port)

max_size=10000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
#data=client.recv(max_size)

#game variables
game_state = 1
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

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(450,100)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(450,100))]

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
gravity_counter = 0

frozen = 0
freeze_counter = 0
freeze_duration = 500

def display_players():
    p1 = pygame.Surface((50, 50))
    p1.set_colorkey((0,0,0))
    p1.blit(players[1], (0, 0), ((player2_animation_state) * 50, (game_data["players"][1]["facing"]) * 50, 50, 50))
    p0 = pygame.Surface((50, 50))
    p0.set_colorkey((0,0,0))
    p0.blit(players[0], (0, 0), ((player1_animation_state) * 50, (game_data["players"][0]["facing"]) * 50, 50, 50))
    if player_id == 0:
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
    else:
        window.blit(p0,(int(game_data["players"][0]["x"])-x_offset,int(game_data["players"][0]["y"])-y_offset))
        window.blit(p1,(int(game_data["players"][1]["x"])-x_offset,int(game_data["players"][1]["y"])-y_offset))

def listen_to_server(client):
    global player1_animation
    global player2_animation
    global player1_animation_state
    global player2_animation_state
    global player1_animation_direction
    global player2_animation_direction
    global game_data
    global game_state
    global frozen
    global freeze_counter
    while game_state:
        msg = client.recv(max_size)
        if(str(msg,"utf-8") == "quit"):
            print("quit")
            game_state = 0
        game_data,anim_data = messages.parse_message(msg,game_data)
        if anim_data[0]==1:
            if anim_data[1]==0:
                player1_animation = game_data["players"][0]["anim"][0]
                player1_animation_state = game_data["players"][0]["anim"][1]
                player1_animation_direction = game_data["players"][0]["anim"][2]
            else:
                player2_animation = game_data["players"][1]["anim"][0]
                player2_animation_state = game_data["players"][1]["anim"][1]
                player2_animation_direction = game_data["players"][1]["anim"][2]
        if game_data ["players"][player_id]["frozen"]:
            frozen = 1
            freeze_counter = 0

        # print(f'recieved message {str(msg,"utf-8")}')

server_listener = threading.Thread(target=lambda:listen_to_server(client))
server_listener.start()

player_width = 50
player_height = 50
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
    if game_state == 1: # main game loop
        x_offset = int(((int(game_data["players"][player_id]["x"])) / max_char_x) * max_x_offset)
        y_offset = int(((int(game_data["players"][player_id]["y"])) / max_char_y) * max_y_offset)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                messages.send_message("quit",client)
                pygame.quit()
                client.close()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
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
                        if player_id == 0:
                            if abs(game_data['players'][0]["x"] - game_data['players'][1]["x"]) <= player_width*1.5 and abs(game_data['players'][0]["y"] - game_data['players'][1]["y"]) <= player_height*1.5:
                                messages.send_message(f"freeze 1|",client)
                        if player_id == 1:
                            if abs(game_data['players'][1]["x"] - game_data['players'][0]["x"]) <= player_width*1.5 and abs(game_data['players'][1]["y"] - game_data['players'][0]["y"]) <= player_height*1.5:
                                messages.send_message(f"freeze 0|",client)


        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not frozen:
                new_x = (game_data["players"][player_id]["x"]+player_move_speed)+50
                player_y = game_data['players'][player_id]["y"]

                if new_x<(len(game_data["level"]['grid'][0])*tile_size):
                    tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                    tile_2 = 0
                    if player_y % tile_size != 0:
                        tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

                    if tile_1 != 1 and tile_2 != 1:
                        game_data["players"][player_id]["x"]+=player_move_speed
                        messages.send_message(f"move {player_id} {player_move_speed}|",client)
                if player_id == 0:
                    game_data["players"][player_id]["facing"] = 0
                if player_id == 1:
                    game_data["players"][player_id]["facing"] = 0
                messages.send_message(f"face {player_id} 0 |",client)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if not frozen:
                new_x = (game_data["players"][player_id]["x"]-player_move_speed)
                player_y = game_data['players'][player_id]["y"]

                tile_1 = game_data['level']['grid'][game_data['players'][player_id]["y"]//tile_size][new_x//tile_size]
                tile_2 = 0
                if player_y % tile_size != 0:
                    tile_2 = game_data['level']["grid"][(game_data["players"][player_id]["y"]+50)//tile_size][new_x//tile_size]

                if (tile_1 != 1 and tile_2 != 1) and new_x>0:
                    game_data["players"][player_id]["x"]-=player_move_speed
                    messages.send_message(f"move {player_id} -{player_move_speed}|",client)
                if player_id == 0:
                    game_data["players"][player_id]["facing"] = 1
                if player_id == 1:
                    game_data["players"][player_id]["facing"] = 1
                messages.send_message(f"face {player_id} 1 |",client)
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
            else:
                player_y_vel = 0

        gravity_counter+=1
        if gravity_counter>=2:
            gravity_counter = 0
            player_y_vel+=1
            # player_y_vel = 1

        animation_counter += 1
        if animation_counter == anim_speed:
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
            animation_counter = 0

        if frozen:
            if freeze_counter >= freeze_duration:
                frozen = 0
                freeze_counter = 0
            freeze_counter += 1

        display_tiles()
        display_players()
        pygame.display.update()

#close client
client.close()
pygame.quit()
quit()
